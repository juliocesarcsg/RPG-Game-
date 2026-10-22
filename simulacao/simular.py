"""Simulador de partidas da Arena de Combate com jogadores-robô.

Os robôs respondem aos mesmos prompts que uma pessoa (via console.input do main.py), então todo o fluxo
real é exercitado: menu de ações, voltar/confirmar, inventário, alvos, Comerciante, substituição e Forja.
Eles jogam com heurísticas simples de "jogador comum" e um pouco de aleatoriedade (às vezes desistem de
um ataque, cancelam uma confirmação, poupam ouro...).

Escolha de alvo (como pessoas costumam jogar): miram em quem tem mais vida (o mais forte) ou em quem causa mais
dano; só preferem o de menos vida quando ele está quase eliminado (12% da vida ou menos).

Uso (na pasta do projeto):
    python simulacao/simular.py teste        # 2 partidas com a interface renderizada em simulacao/partida_teste_*.txt
    python simulacao/simular.py massa [N] [sufixo]  # ~N partidas (padrão 5000) sem renderizar; gera simulacao/resultados[sufixo].json
"""

import collections
import json
import math
import os
import random
import re
import statistics
import sys
import time
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))

import dice  # noqa: E402
import main  # noqa: E402
import shop  # noqa: E402

RACAS = list(main.RACAS)
LIMITE_ENTRADAS = 30000
LIMITE_RODADAS = 150


class PartidaTravada(Exception):
    pass


class ConsoleMudo:
    """Console que não desenha nada (para simular rápido)."""

    def print(self, *a, **k):
        pass

    def clear(self, *a, **k):
        pass

    def rule(self, *a, **k):
        pass


# ----------------------------------------------------------------------
# Coleta de dados
# ----------------------------------------------------------------------
class Coleta:
    def __init__(self):
        self.partidas = []          # um registro por partida
        self.ataques = []           # (cenario, raca, categoria, bruto, final, fator, postura_alvo, rodada)
        self.diretos = []           # (cenario, raca, item, dano)
        self.visitas = []           # visitas ao Comerciante
        self.compras = collections.Counter()
        self.itens_usados = collections.Counter()
        self.acoes = collections.defaultdict(collections.Counter)  # raca -> ação -> n
        self.ouro = collections.defaultdict(collections.Counter)   # raca -> fonte -> total
        self.jogos_raca = collections.Counter()                     # raca -> nº de participações
        self.bugs = collections.Counter()
        self.exemplos_bug = {}
        self.erros = []
        self.posse_itens = collections.defaultdict(lambda: [0, 0])  # item -> [donos no fim, donos que venceram]
        self.recebidos = collections.defaultdict(collections.Counter)  # raça -> ataques/dano recebidos
        self.curas = collections.defaultdict(collections.Counter)  # raça -> fonte -> vida curada
        self.habilidades = collections.defaultdict(collections.Counter)  # raça -> habilidade -> usos
        self.cenario = ""

    def bug(self, chave, exemplo=""):
        self.bugs[chave] += 1
        self.exemplos_bug.setdefault(chave, exemplo)


C = Coleta()


class Ctx:
    """Estado da partida atual compartilhado entre os wrappers e o robô."""

    def __init__(self):
        self.fase = None
        self.jogador = None
        self.jogadores = []
        self.rodada = 0
        self.estoque = None
        self.compras = []
        self.ultimos_alvos = []
        self.acao_turno = None
        self.eliminacoes = []
        self.raca_alvo = None
        self.enfurecido = False


X = Ctx()


# ----------------------------------------------------------------------
# Robô
# ----------------------------------------------------------------------
class Robo:
    def __init__(self, racas, rng):
        self.racas = list(racas)
        self.rng = rng
        self.n = 0
        self.reset_turno()

    def reset_turno(self):
        self.decisoes = 0
        self.plano_item = None
        self.alvo_desejado = None
        self.voltar_ataque = False
        self.cancelar = False
        self.tentados = set()
        self.tentativas_loja = 0
        self.usadas = set()  # habilidades livres já tentadas neste turno
        self.par_mistura = None

    # --------------------------- despacho ---------------------------
    def responder(self, msg=""):
        self.n += 1
        if self.n > LIMITE_ENTRADAS:
            raise PartidaTravada(f"mais de {LIMITE_ENTRADAS} entradas (último prompt: {msg!r})")
        t = re.sub(r"\[[^\]]*\]", "", str(msg))
        if "Pressione Enter" in t:
            return ""
        if "Quantos jogadores" in t:
            return str(len(self.racas))
        if "Nome do Jogador" in t:
            return "Robo" + re.search(r"Jogador (\d+)", t).group(1)
        if "Alvo (" in t:
            return self.escolher_alvo()
        if "Número do item" in t:
            return self.usar_inventario()
        if "Substituir qual item" in t:
            return self.substituir()
        if "Item para forjar" in t:
            return self.forjar()
        if "Primeiro consumível" in t or "Segundo consumível" in t:
            return self.mistura("Primeiro" in t)
        m = re.search(r"Escolha \((\d+)-(\d+)\)", t)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if (lo, hi) == (1, 2):
                return self.confirmar()
            if X.fase == "raca":
                return str(RACAS.index(X.raca_alvo) + 1)
            if X.fase == "turno":
                return self.decidir_acao(hi)
            if X.fase == "loja":
                return self.decidir_loja()
        raise PartidaTravada(f"prompt desconhecido: {t!r} (fase {X.fase})")

    def confirmar(self):
        if self.cancelar:
            self.cancelar = False
            return "2"
        return "1"

    # --------------------------- turno ---------------------------
    def acao(self, nome):
        """Número da ação no menu do turno do jogador atual."""
        return str(main.acoes_do_turno(X.jogador).index(nome) + 1)

    def decidir_acao(self, maximo):
        j, js, rng = X.jogador, X.jogadores, self.rng
        raca = j["raca"]
        self.decisoes += 1
        if self.decisoes > 14:
            C.bug("robô: turno com decisões demais (possível loop de menu)", f"{raca} rodada {X.rodada}")
            return self.acao("passar")
        alvos = main.alvos_disponiveis(j, js)
        feiticeiro = raca == "Feiticeiro"
        pode_atacar = (bool(alvos) and (not feiticeiro or j["mana"] >= 1)
                       and (raca != "Mosqueteiro" or j["municao"] >= 1))
        # pessoa indecisa: abre o ataque e volta, ou cancela uma ação na confirmação
        r = rng.random()
        if self.decisoes == 1 and r < 0.03 and pode_atacar:
            self.voltar_ataque = True
            return self.acao("atacar")
        if self.decisoes == 1 and r < 0.05:
            self.cancelar = True
            return self.acao("passar")
        # habilidades de ação livre (antes de agir)
        hp_pct = j["hp"] / j["hp_max"]
        if raca == "Bárbaro" and "folego" not in self.usadas and j["furia"] >= main.FURIA_MAX and hp_pct < 0.45:
            self.usadas.add("folego")
            return self.acao("folego")
        if (raca == "Hemomante" and "pacto" not in self.usadas and pode_atacar and hp_pct > 0.4
                and main.bloqueio_habilidade(j, "pacto") is None):
            self.usadas.add("pacto")
            return self.acao("pacto")
        if (raca == "Mosqueteiro" and "na_mira" not in self.usadas and pode_atacar
                and main.bloqueio_habilidade(j, "na_mira") is None):
            self.usadas.add("na_mira")
            return self.acao("na_mira")
        plano = self.planejar_item(j, js, alvos, pode_atacar)
        if plano:
            self.plano_item = plano
            return self.acao("inventario")
        if feiticeiro:
            # o Feiticeiro não tem postura: no lugar dela, o Escudo de Mana
            if not j["escudo_mana"] and j["mana"] >= 2 and hp_pct < 0.5 and rng.random() < 0.35:
                return self.acao("escudo_mana")
            if not pode_atacar or rng.random() < 0.01:
                return self.acao("passar")
            return self.acao("atacar")
        if raca == "Mosqueteiro" and j["municao"] == 0:
            return self.acao("recarregar")
        if not pode_atacar:
            return self.acao("postura")
        if hp_pct < 0.3 and not j["postura"] and rng.random() < 0.35:
            return self.acao("postura")
        if not j["postura"] and rng.random() < 0.12:
            return self.acao("postura")
        if rng.random() < 0.01:
            return self.acao("passar")  # às vezes passa a vez
        return self.acao("atacar")

    def planejar_item(self, j, js, alvos, pode_atacar):
        rng = self.rng
        hp_pct = j["hp"] / j["hp_max"]
        cura, buff, defesa, alvo_item, roubo = [], [], [], [], []
        for item in j["itens"]:
            if item["tipo"] not in ("consumivel", "ativo") or id(item) in self.tentados:
                continue
            if not shop.pode_usar(j, item)[0]:
                continue
            e = item["efeitos"]
            if "bomba_area" in e:  # Barril: vale a pena com 2 ou mais oponentes, ou para finalizar alguém
                oponentes = [o for o in main.vivos(js) if o is not j]
                if len(oponentes) >= 2 or any(o["hp"] <= e["bomba_area"] for o in oponentes):
                    alvo_item.append((item, None))
            elif "bomba" in e or "raio" in e:
                if alvos:
                    dano = e.get("bomba", e.get("raio"))
                    finalizaveis = [a for a in alvos if a["hp"] <= dano]
                    if finalizaveis:
                        alvo_item.append((item, min(finalizaveis, key=lambda a: a["hp"])))
                    elif rng.random() < 0.5:
                        alvo_item.append((item, self.alvo_preferido(alvos)))
            elif "sentenca" in e:
                if pode_atacar:
                    buff.append((item, self.alvo_preferido(alvos)))
            elif "acido" in e:
                afet = main.alvos_afetaveis(j, js)
                if afet:
                    duro = max(afet, key=lambda a: main.defesa_total(a))
                    if main.defesa_total(duro) >= 3 and not duro["acido"]:
                        alvo_item.append((item, duro))
            elif "roubo" in e:
                afet = main.alvos_afetaveis(j, js)
                if afet:
                    rico = max(afet, key=lambda a: a["ouro"])
                    if rico["ouro"] >= 5:
                        roubo.append((item, rico))
            elif "cura" in e or e.get("antidoto"):
                falta = j["hp_max"] - j["hp"]
                if (hp_pct < 0.55 and falta >= 0.6 * e.get("cura", 0)) or (j["veneno"] and j["veneno"]["dano"] >= 3):
                    cura.append((item, None))
            elif any(k in e for k in ("buff_dano", "buff_rolagem", "veneno_arma", "ferida_arma")) and not e.get("invisibilidade"):
                if pode_atacar:
                    buff.append((item, None))
            elif any(k in e for k in ("defesa_temp", "escudo_pv", "invisibilidade")):
                if hp_pct < 0.6 or rng.random() < 0.4:
                    defesa.append((item, None))
        for grupo in (cura if hp_pct < 0.35 else [], roubo, buff, defesa, alvo_item, cura):
            if grupo:
                return grupo[0]
        return None

    def usar_inventario(self):
        j = X.jogador
        if not self.plano_item:
            return "0"
        item, alvo = self.plano_item
        self.plano_item = None
        self.tentados.add(id(item))
        if item not in j["itens"]:
            return "0"
        self.alvo_desejado = alvo
        return str(j["itens"].index(item) + 1)

    def escolher_alvo(self):
        alvos, rng = X.ultimos_alvos, self.rng
        if self.voltar_ataque:
            self.voltar_ataque = False
            return "0"
        alvo = self.alvo_desejado if self.alvo_desejado in alvos else self.alvo_preferido(alvos)
        self.alvo_desejado = None
        return str(alvos.index(alvo) + 1)

    def alvo_preferido(self, alvos):
        """Como pessoas costumam escolher: elimina quem está quase morto (12% da vida ou menos); fora isso, mira em
        quem tem mais vida (o mais forte) ou em quem causa mais dano, com um pouco de acaso."""
        rng = self.rng
        quase = [a for a in alvos if a["hp"] <= 0.12 * a["hp_max"]]
        if quase:
            return min(quase, key=lambda a: a["hp"])
        r = rng.random()
        if r < 0.45:
            return max(alvos, key=lambda a: (a["hp"], rng.random()))
        if r < 0.85:
            return max(alvos, key=lambda a: (a["dano"], rng.random()))
        return rng.choice(alvos)

    # --------------------------- Comerciante ---------------------------
    def forjaveis(self, j):
        return [i for i in j["itens"] if i["tipo"] in shop.EQUIPAVEIS and i.get("forja", 0) < shop.MAX_FORJA]

    def decidir_loja(self):
        j, estoque = X.jogador, X.estoque
        self.tentativas_loja += 1
        if self.tentativas_loja > 12:
            C.bug("robô: loja com tentativas demais (possível loop de menu)", j["raca"])
            return "0"
        n_itens = 0 if shop.compras_esgotadas(j) else len(estoque)
        extras = [chave for chave, _ in main.extras_loja(j)]
        if "forja" in extras and self.forjaveis(j):
            return str(n_itens + extras.index("forja") + 1)
        if n_itens:
            item = self.escolher_compra(j, estoque)
            if item is not None:
                self.item_escolhido = item
                return str(estoque.index(item) + 1)
        if "mistura" in extras:
            return str(n_itens + extras.index("mistura") + 1)
        return "0"

    def mistura(self, primeiro):
        """Alquimista: junta os 2 primeiros consumíveis que podem ser misturados (ou 2 usos do mesmo)."""
        opcoes = shop.misturaveis(X.jogador)
        if primeiro:
            self.par_mistura = (1, 2) if len(opcoes) >= 2 else (1, 1)
            return str(self.par_mistura[0])
        return str(self.par_mistura[1])

    def valor(self, j, item):
        preco = item["preco"]
        e = item["efeitos"]
        raca = j["raca"]
        if item["tipo"] == "consumivel":
            consumiveis = [i for i in j["itens"] if i["tipo"] == "consumivel"]
            if len(consumiveis) >= 3 + (2 if raca == "Alquimista" else 0):
                return 0.1 * preco
            if "cura" in e and not any("cura" in i["efeitos"] for i in consumiveis):
                v = 0.7 * preco
            else:
                v = 0.4 * preco
            if raca == "Alquimista":
                v *= 1.8  # o personagem dos consumíveis
            if raca == "Hemomante" and "cura" in e:
                v *= 0.5  # curas rendem metade para ele
            return v
        v = float(preco)
        if shop.slot_cheio(j, item["tipo"]):
            pior = shop.pior_item_do_slot(j, item["tipo"])
            valor_pior = pior.get("valor", 0) + 5 * pior.get("forja", 0)
            if valor_pior >= preco:
                return 0
            v = preco - 0.7 * valor_pior
        if "dano" in e:
            v *= shop.rendimento_dano(j, item.get("magico", False))  # dano fora da afinidade rende menos
        if item["tipo"] == "arma" and shop.fora_do_alcance(j, item):
            v *= 0.6  # arma de alcance diferente: −1 no D10
        if raca == "Feiticeiro" and "mana_regen" in e:
            v *= 1.3
        if raca == "Bárbaro" and "furia_extra" in e:
            v *= 1.3
        if raca == "Ferreiro" and item["tipo"] in shop.EQUIPAVEIS:
            v *= 1.2
        if raca == "Goblin" and "ouro_turno" in e:
            v *= 1.2
        if raca == "Mosqueteiro" and "municao_extra" in e:
            v *= 1.4
        if raca == "Hemomante" and "pacto_desconto" in e:
            v *= 1.4
        return v

    def escolher_compra(self, j, estoque):
        rng = self.rng
        melhores = []
        for item in estoque:
            if shop.bloqueio_compra(j, item) or item["preco"] > j["ouro"]:
                continue
            v = self.valor(j, item) * rng.uniform(0.8, 1.2)
            if v >= 10:
                melhores.append((v, item))
        if not melhores:
            return None
        return max(melhores, key=lambda t: t[0])[1]

    def substituir(self):
        j = X.jogador
        tipo = self.item_escolhido["tipo"]
        candidatos = shop.itens_do_slot(j, tipo)
        return str(candidatos.index(shop.pior_item_do_slot(j, tipo)) + 1)

    def forjar(self):
        f = self.forjaveis(X.jogador)
        armas = [i for i in f if i["tipo"] == "arma"]
        escolha = max(armas, key=lambda i: i["efeitos"].get("dano", 0)) if armas else f[0]
        return str(f.index(escolha) + 1)


ROBO = None


# ----------------------------------------------------------------------
# Wrappers sobre o jogo (só observam; não mudam regras)
# ----------------------------------------------------------------------
CAP = []
_orig = {}


def instalar_wrappers():
    _orig.update(
        resultado_ataque=dice.resultado_ataque,
        executar_ataque=main.executar_ataque,
        dano_direto=main.dano_direto,
        dano_area=main.dano_area,
        turno=main.turno,
        escolher_raca=main.escolher_raca,
        escolher_alvo=main.escolher_alvo,
        loja_jogador=main.loja_jogador,
        ouro_do_turno=main.ouro_do_turno,
        assumir_postura=main.assumir_postura,
        recarregar=main.recarregar,
        aplicar_item_com_alvo=main.aplicar_item_com_alvo,
        usar_item=shop.usar_item,
        comprar=shop.comprar,
        atacar=main.atacar,
        fim_de_rodada=main.fim_de_rodada,
        aplicar_cura=shop.aplicar_cura,
        usar_habilidade=main.usar_habilidade,
        misturar=shop.misturar,
    )

    def resultado_ataque(*a, **k):
        r = _orig["resultado_ataque"](*a, **k)
        CAP.append(r)
        return r

    def eliminar(alvo, por):
        X.eliminacoes.append((alvo["nome"], alvo["raca"], X.rodada, por, [i["nome"] for i in alvo["itens"]]))

    def executar_ataque(atk, alvo):
        CAP.clear()
        X.enfurecido = atk["raca"] == "Bárbaro" and atk["furia"] >= main.FURIA_MAX
        buff = atk["buff_dano"]
        poder = atk["dano_fisico"] + atk["dano_magico"]
        hp0, esc0 = alvo["hp"], alvo["escudo_pv"]
        ouro_a0, ouro_d0 = atk["ouro"], alvo["ouro"]
        postura = alvo["postura"]
        mira, penal = atk["na_mira"], atk["penalidade_mira"]
        if atk["postura"]:
            C.bug("atacante continua em postura defensiva enquanto ataca (postura de turno anterior não expira)",
                  "assumir_postura em um turno + atacar nos seguintes: a postura só some quando o jogador é atingido")
        _orig["executar_ataque"](atk, alvo)
        rolls = list(CAP)
        fator = sum(r["fator"] for r in rolls)
        cat = "Fúria" if X.enfurecido else rolls[0]["nome"]
        X.enfurecido = False
        bruto = round(poder * fator * buff)
        final = (hp0 - alvo["hp"]) + (esc0 - alvo["escudo_pv"])
        C.ataques.append((C.cenario, atk["raca"], cat, bruto, final, fator, postura, X.rodada, buff > 1, mira, penal))
        C.recebidos[alvo["raca"]]["ataques"] += 1
        C.recebidos[alvo["raca"]]["dano"] += final
        C.ouro[atk["raca"]]["ataques (crítico, saque, roubo)"] += atk["ouro"] - ouro_a0
        delta_alvo = alvo["ouro"] - ouro_d0
        C.ouro[alvo["raca"]]["defesa perfeita" if delta_alvo >= 0 else "roubado por crítico do Goblin"] += delta_alvo
        if hp0 > 0 and not alvo["vivo"]:
            eliminar(alvo, atk["raca"])

    def dano_direto(atk, alvo, dano, item):
        hp0 = alvo["hp"]
        if alvo["postura"] or alvo["escudo_mana"]:
            C.bug("bomba/raio atinge alvo em postura ou com Escudo de Mana sem consumir a defesa",
                  "dano_direto ignora a postura e o Escudo de Mana, mas eles continuam ativos para o próximo ataque")
        _orig["dano_direto"](atk, alvo, dano, item)
        C.diretos.append((C.cenario, atk["raca"], item["nome"], hp0 - alvo["hp"]))
        if hp0 > 0 and not alvo["vivo"]:
            eliminar(alvo, atk["raca"] + " (item)")

    def dano_area(atk, jogadores, dano, item):
        vivos0 = [o for o in jogadores if o["vivo"] and o is not atk]
        hp0 = {id(o): o["hp"] for o in vivos0}
        _orig["dano_area"](atk, jogadores, dano, item)
        C.diretos.append((C.cenario, atk["raca"], item["nome"], sum(hp0[id(o)] - o["hp"] for o in vivos0)))
        for o in vivos0:
            if not o["vivo"]:
                eliminar(o, atk["raca"] + " (item)")

    def turno(rodada, jogador, jogadores):
        if rodada > LIMITE_RODADAS:
            raise PartidaTravada(f"passou de {LIMITE_RODADAS} rodadas")
        X.fase, X.jogador, X.jogadores, X.rodada = "turno", jogador, jogadores, rodada
        X.acao_turno = None
        ROBO.reset_turno()
        escudo0 = jogador["escudo_mana"]
        _orig["turno"](rodada, jogador, jogadores)
        acao = X.acao_turno
        if acao is None:
            acao = "Escudo de Mana" if (jogador["escudo_mana"] and not escudo0) else "passar"
        C.acoes[jogador["raca"]][acao] += 1
        X.fase = None
        checar_invariantes(jogadores, f"fim do turno de {jogador['raca']} (rodada {rodada})")

    def escolher_raca(nome, cor):
        X.fase = "raca"
        X.raca_alvo = ROBO.racas[len(X.jogadores_criados)]
        r = _orig["escolher_raca"](nome, cor)
        X.jogadores_criados.append(r)
        X.fase = None
        return r

    def escolher_alvo(atacante, jogadores, alvos=None, titulo="🎯 ESCOLHA O ALVO"):
        X.ultimos_alvos = alvos if alvos is not None else main.alvos_disponiveis(atacante, jogadores)
        return _orig["escolher_alvo"](atacante, jogadores, alvos, titulo)

    def loja_jogador(jogador, estoque):
        fase_ant = X.fase
        X.fase, X.jogador, X.estoque, X.compras = "loja", jogador, estoque, []
        ROBO.reset_turno()
        ouro0 = jogador["ouro"]
        acessivel = any(i["preco"] <= ouro0 for i in estoque)
        r = _orig["loja_jogador"](jogador, estoque)
        C.visitas.append({
            "cenario": C.cenario, "raca": jogador["raca"], "rodada": X.rodada_loja,
            "fase": shop.fase_da_rodada(X.rodada_loja), "ouro_entrada": ouro0, "ouro_saida": jogador["ouro"],
            "acessivel": acessivel, "compras": X.compras, "n_estoque": len(estoque),
        })
        X.fase = fase_ant
        return r

    def ouro_do_turno(jogador, *a, **k):
        total, gob, itens = _orig["ouro_do_turno"](jogador, *a, **k)
        o = C.ouro[jogador["raca"]]
        o["turno (base)"] += total - gob - itens
        o["Goblin (turno)"] += gob
        o["itens (ouro por turno)"] += itens
        return total, gob, itens

    def assumir_postura(jogador):
        o0 = jogador["ouro"]
        msg = _orig["assumir_postura"](jogador)
        C.ouro[jogador["raca"]]["Goblin (postura)"] += jogador["ouro"] - o0
        X.acao_turno = "postura"
        return msg

    def recarregar(jogador):
        X.acao_turno = "recarregar"
        return _orig["recarregar"](jogador)

    def aplicar_item_com_alvo(jogador, item, alvo):
        o0, oa0 = jogador["ouro"], alvo["ouro"]
        C.itens_usados[item["nome"]] += 1
        _orig["aplicar_item_com_alvo"](jogador, item, alvo)
        C.ouro[jogador["raca"]]["roubo (Luvas)"] += jogador["ouro"] - o0
        C.ouro[alvo["raca"]]["roubado de mim"] += alvo["ouro"] - oa0
        if item["efeitos"].get("livre"):
            C.acoes[jogador["raca"]]["item livre (não encerra)"] += 1
        else:
            X.acao_turno = "item (com alvo)"

    def usar_item(jogador, item):
        ok, msg = _orig["usar_item"](jogador, item)
        if ok:
            C.itens_usados[item["nome"]] += 1
            if not item["efeitos"].get("livre"):
                X.acao_turno = "item (gasta o turno)"
            else:
                C.acoes[jogador["raca"]]["item livre (não encerra)"] += 1
        return ok, msg

    def comprar(jogador, item, substituir=None):
        o0 = jogador["ouro"]
        ok, msg = _orig["comprar"](jogador, item, substituir)
        if ok:
            gasto = o0 - jogador["ouro"]
            X.compras.append({"nome": item["nome"], "tipo": item["tipo"], "tier": item["tier"], "preco": item["preco"],
                              "pago": gasto, "substituiu": bool(substituir)})
            C.compras[item["nome"]] += 1
            C.ouro[jogador["raca"]]["gasto no Comerciante"] += gasto
            C.ouro[jogador["raca"]]["economia Pechinchar"] += item["preco"] - gasto
        elif X.fase == "loja":
            C.bug(f"compra recusada pelo jogo: {msg[2:]}", item["nome"])
        return ok, msg

    def atacar(jogador, alvo):
        X.acao_turno = "ataque"
        return _orig["atacar"](jogador, alvo)

    def aplicar_cura(jogador, valor, fonte=""):
        curou = _orig["aplicar_cura"](jogador, valor, fonte)
        C.curas[jogador["raca"]][fonte or "outros"] += curou
        return curou

    def usar_habilidade(jogador, acao):
        C.habilidades[jogador["raca"]][acao] += 1
        return _orig["usar_habilidade"](jogador, acao)

    def misturar(jogador, a, b):
        ok, msg = _orig["misturar"](jogador, a, b)
        if ok:
            C.habilidades[jogador["raca"]]["mistura"] += 1
        return ok, msg

    def fim_de_rodada(jogadores):
        eventos = _orig["fim_de_rodada"](jogadores)
        checar_invariantes(jogadores, "fim de rodada")
        return eventos

    orig_fase_loja = main.fase_loja

    def fase_loja(jogadores, ordem, rodada=main.INTERVALO_LOJA):
        X.rodada_loja = rodada
        X.fase_max = max(X.fase_max, shop.fase_da_rodada(rodada))
        for j in main.vivos(jogadores):
            C.ouro[j["raca"]]["Comerciante (base)"] += main.OURO_LOJA
            if j["raca"] == "Goblin":
                C.ouro[j["raca"]]["Goblin (Comerciante)"] += int(main.OURO_LOJA * main.BONUS_GOBLIN)
        orig_fase_loja(jogadores, ordem, rodada)
        checar_invariantes(jogadores, "depois do Comerciante")

    dice.resultado_ataque = resultado_ataque
    main.executar_ataque = executar_ataque
    main.dano_direto = dano_direto
    main.dano_area = dano_area
    main.turno = turno
    main.escolher_raca = escolher_raca
    main.escolher_alvo = escolher_alvo
    main.loja_jogador = loja_jogador
    main.ouro_do_turno = ouro_do_turno
    main.assumir_postura = assumir_postura
    main.recarregar = recarregar
    main.aplicar_item_com_alvo = aplicar_item_com_alvo
    shop.usar_item = usar_item
    shop.comprar = comprar
    main.atacar = atacar
    main.fim_de_rodada = fim_de_rodada
    main.fase_loja = fase_loja
    shop.aplicar_cura = aplicar_cura
    main.usar_habilidade = usar_habilidade
    shop.misturar = misturar


def checar_invariantes(jogadores, onde):
    for j in jogadores:
        r = j["raca"]
        if j["hp"] > j["hp_max"]:
            C.bug("vida acima do máximo", f"{r} {j['hp']}/{j['hp_max']} em {onde}")
        if j["hp"] < 0:
            C.bug("vida negativa", f"{r} em {onde}")
        if j["vivo"] != (j["hp"] > 0):
            C.bug("flag 'vivo' não bate com a vida", f"{r} hp={j['hp']} vivo={j['vivo']} em {onde}")
        if not isinstance(j["hp"], int):
            C.bug("vida com valor não inteiro", f"{r} hp={j['hp']!r} em {onde}")
        if j["ouro"] < 0:
            C.bug("ouro negativo", f"{r} em {onde}")
        if not 0 <= j["mana"] <= main.MAX_PIPS:
            C.bug("mana fora de 0..3", f"{r} mana={j['mana']} em {onde}")
        if not 0 <= j["furia"] <= main.FURIA_MAX:
            C.bug("fúria fora da barra", f"{r} fúria={j['furia']} em {onde}")
        if not 0 <= j["municao"] <= j["municao_max"]:
            C.bug("munição fora da barra", f"{r} munição={j['municao']} em {onde}")
        for tipo in shop.LIMITE_SLOTS:
            if len(shop.itens_do_slot(j, tipo)) > shop.limite_slot(j, tipo):
                C.bug("mais itens equipados do que o espaço permite", f"{r} {tipo} em {onde}")


# ----------------------------------------------------------------------
# Partidas
# ----------------------------------------------------------------------
def jogar_partida(racas, semente):
    global ROBO
    random.seed(semente)
    ROBO = Robo(racas, random.Random(semente * 7 + 1))
    main.console.input = ROBO.responder
    X.__init__()
    X.jogadores_criados = []
    X.rodada_loja = 0
    X.fase_max = 0
    for r in racas:
        C.jogos_raca[(C.cenario, r)] += 1
    jogadores = main.configurar_jogadores()
    main.tela_resumo(jogadores)
    main.pausar()
    vencedor = main.jogar(jogadores)
    main.tela_vitoria(vencedor, jogadores)
    for j in jogadores:
        nomes = set(j["itens"][k]["nome"] for k in range(len(j["itens"])))
        if j is vencedor:
            for n in nomes:
                C.posse_itens[n][0] += 1
                C.posse_itens[n][1] += 1
    for _, _, _, _, itens in X.eliminacoes:
        for n in set(itens):
            C.posse_itens[n][0] += 1
    C.partidas.append({
        "cenario": C.cenario, "racas": racas, "vencedor": vencedor["raca"], "rodadas": X.rodada,
        "fase_max": X.fase_max, "hp_vencedor": vencedor["hp"], "hp_max_vencedor": vencedor["hp_max"],
        "eliminacoes": [(r, rod, por) for _, r, rod, por, _ in X.eliminacoes],
        "final": [{"raca": j["raca"], "ouro": j["ouro"], "forja": sum(i.get("forja", 0) for i in j["itens"]), "dano": j["dano"], "defesa": j["defesa"], "hp_max": j["hp_max"],
                   "vivo": j["vivo"]} for j in jogadores],
    })


def rodar(cenario, gerador, n, semente0):
    C.cenario = cenario
    for k in range(n):
        racas = gerador(k)
        try:
            jogar_partida(racas, semente0 + k)
        except PartidaTravada as e:
            C.erros.append({"cenario": cenario, "racas": racas, "semente": semente0 + k, "erro": str(e)})
        except Exception:
            C.erros.append({"cenario": cenario, "racas": racas, "semente": semente0 + k, "erro": traceback.format_exc()})


# ----------------------------------------------------------------------
# Análise
# ----------------------------------------------------------------------
def media(xs):
    return round(statistics.mean(xs), 2) if xs else None


def pct(a, b):
    return round(100 * a / b, 1) if b else None


def ic95(p, n):
    return round(196 * math.sqrt(p * (1 - p) / n), 1) if n else None


def analisar():
    R = {"partidas": len(C.partidas), "erros": C.erros[:20], "n_erros": len(C.erros)}
    cenarios = sorted(set(p["cenario"] for p in C.partidas))

    # vitórias
    vit = {}
    for cen in cenarios:
        ps = [p for p in C.partidas if p["cenario"] == cen]
        linha = {}
        for r in RACAS:
            jogos = sum(1 for p in ps if r in p["racas"])
            vits = sum(1 for p in ps if p["vencedor"] == r)
            esperado = sum(p["racas"].count(r) / len(p["racas"]) for p in ps)
            linha[r] = {"jogos": jogos, "vitorias": vits, "pct_vitoria": pct(vits, len(ps)),
                        "pct_das_partidas_em_que_jogou": pct(vits, jogos),
                        "vitorias_por_esperado": round(vits / esperado, 2) if esperado else None,
                        "ic95": ic95(vits / len(ps), len(ps)) if ps else None}
        rod = [p["rodadas"] for p in ps]
        q = statistics.quantiles(rod, n=10) if len(rod) > 1 else rod
        vit[cen] = {"n": len(ps), "racas": linha, "rodadas_media": media(rod), "rodadas_mediana": statistics.median(rod),
                    "rodadas_p10": q[0], "rodadas_p90": q[-1], "pct_mais_de_30": pct(sum(1 for x in rod if x > 30), len(rod)),
                    "pct_venc_vida_baixa": pct(sum(1 for p in ps if p["hp_vencedor"] <= 0.25 * p["hp_max_vencedor"]), len(ps))}
    R["vitorias"] = vit

    # duelos
    duelos = collections.defaultdict(lambda: [0, 0])
    for p in C.partidas:
        if p["cenario"] == "duelos":
            a, b = sorted(p["racas"])
            duelos[(a, b)][0 if p["vencedor"] == a else 1] += 1
    R["duelos"] = {f"{a} x {b}": {a: v[0], b: v[1], f"% {a}": pct(v[0], sum(v))} for (a, b), v in duelos.items()}

    # ataques
    cats = collections.defaultdict(list)
    for at in C.ataques:
        cats[at[2]].append(at)
    total_at = len(C.ataques)
    R["ataques"] = {}
    for cat, xs in sorted(cats.items()):
        R["ataques"][cat] = {"n": len(xs), "pct": pct(len(xs), total_at), "bruto_medio": media([x[3] for x in xs]),
                             "final_medio": media([x[4] for x in xs]), "fator_medio": media([x[5] for x in xs]),
                             "bruto_max": max(x[3] for x in xs)}
    por_raca = {}
    for r in RACAS:
        xs = [a for a in C.ataques if a[1] == r]
        if not xs:
            continue
        por_raca[r] = {"n": len(xs), "final_medio": media([x[4] for x in xs]), "bruto_medio": media([x[3] for x in xs]),
                       "por_categoria": {c: {"n": len(ys), "final_medio": media([y[4] for y in ys]),
                                             "bruto_medio": media([y[3] for y in ys])}
                                         for c in sorted(set(x[2] for x in xs)) for ys in [[x for x in xs if x[2] == c]]}}
    R["ataques_por_raca"] = por_raca
    furia = [a for a in C.ataques if a[2] == "Fúria"]
    R["furia_fatores"] = dict(collections.Counter(a[5] for a in furia))
    nao_furia_barb = [a for a in C.ataques if a[1] == "Bárbaro" and a[2] != "Fúria"]
    R["barbaro_fator_medio_sem_furia"] = media([a[5] for a in nao_furia_barb])
    R["barbaro_pct_ataques_com_furia"] = pct(len(furia), len(furia) + len(nao_furia_barb))
    R["ataques_contra_postura"] = {"n": sum(1 for a in C.ataques if a[6]),
                                   "final_medio": media([a[4] for a in C.ataques if a[6]]),
                                   "final_medio_sem_postura": media([a[4] for a in C.ataques if not a[6]])}
    fases_dano = collections.defaultdict(list)
    for a in C.ataques:
        fases_dano["rodadas 1-10" if a[7] <= 10 else "rodadas 11-20" if a[7] <= 20 else "rodadas 21-30" if a[7] <= 30 else "rodada 31+"].append(a[4])
    R["dano_final_por_periodo"] = {k: media(v) for k, v in sorted(fases_dano.items())}
    R["picos"] = sorted(C.ataques, key=lambda a: -a[4])[:5]
    R["diretos"] = {nome: {"n": len(xs), "dano_medio": media([x[3] for x in xs])}
                    for nome in sorted(set(d[2] for d in C.diretos)) for xs in [[d for d in C.diretos if d[2] == nome]]}

    # ações
    R["acoes"] = {r: {a: pct(n, sum(c.values())) for a, n in c.most_common()} for r, c in C.acoes.items()}

    # ouro (por participação em partida)
    part = collections.Counter()
    for (cen, r), n in C.jogos_raca.items():
        part[r] += n
    R["ouro_por_partida"] = {r: {f: round(v / part[r], 1) for f, v in sorted(c.items(), key=lambda t: -abs(t[1]))}
                             for r, c in C.ouro.items()}
    # Comerciante
    vis = C.visitas
    R["comerciante"] = {}
    for r in RACAS:
        vs = [v for v in vis if v["raca"] == r]
        if not vs:
            continue
        compr = [c for v in vs for c in v["compras"]]
        R["comerciante"][r] = {
            "visitas": len(vs), "ouro_medio_na_chegada": media([v["ouro_entrada"] for v in vs]),
            "pct_comprou": pct(sum(1 for v in vs if v["compras"]), len(vs)),
            "pct_duas_compras": pct(sum(1 for v in vs if len(v["compras"]) >= 2), len(vs)),
            "compras_por_visita": media([len(v["compras"]) for v in vs]),
            "pct_nada_acessivel": pct(sum(1 for v in vs if not v["acessivel"]), len(vs)),
            "preco_medio_pago": media([c["pago"] for c in compr]),
            "gasto_medio_por_visita": media([sum(c["pago"] for c in v["compras"]) for v in vs]),
            "ouro_medio_saida": media([v["ouro_saida"] for v in vs]),
            "pct_compras_por_tipo": {t: pct(n, len(compr)) for t, n in collections.Counter(c["tipo"] for c in compr).most_common()},
            "pct_compras_por_fase": {TIERS_NOME[t]: pct(n, len(compr)) for t, n in collections.Counter(c["tier"] for c in compr).most_common()},
            "pechinchas": sum(1 for c in compr if c["pago"] < c["preco"]),
        }
    R["visitas_por_fase"] = dict(collections.Counter(TIERS_NOME[v["fase"]] for v in vis))
    R["partidas_que_viram_fase"] = {
        TIERS_NOME[f]: pct(sum(1 for p in C.partidas if p["fase_max"] >= f), len(C.partidas)) for f in (2, 3)
    }
    R["partidas_que_viram_fase_por_cenario"] = {
        cen: {TIERS_NOME[f]: pct(sum(1 for p in ps if p["fase_max"] >= f), len(ps)) for f in (2, 3)}
        for cen in cenarios for ps in [[p for p in C.partidas if p["cenario"] == cen]]
    }
    R["fases_do_comerciante"] = shop.texto_fases()
    # ganho total de ouro por raça (sem contar gastos e roubos sofridos) e razão em relação à média das outras
    ganho = {r: sum(v for f, v in c.items() if f not in ("gasto no Comerciante", "roubado de mim", "economia Pechinchar"))
             for r, c in R["ouro_por_partida"].items()}
    R["ouro_ganho_por_partida"] = {r: round(g, 1) for r, g in ganho.items()}
    # ganho por rodada vivo (para comparar raças que sobrevivem tempos diferentes)
    rodadas_vivo = collections.Counter()
    for p in C.partidas:
        mortes = {}
        for raca, rod, _ in p["eliminacoes"]:
            mortes.setdefault(raca, []).append(rod)
        for raca in p["racas"]:
            lista = mortes.get(raca)
            rodadas_vivo[raca] += lista.pop(0) if lista else p["rodadas"]
    R["ouro_ganho_por_rodada_vivo"] = {
        r: round(sum(v for f, v in C.ouro[r].items() if f not in ("gasto no Comerciante", "roubado de mim", "economia Pechinchar"))
                 / rodadas_vivo[r], 2) for r in RACAS if rodadas_vivo[r]}
    forjas = [f["forja"] for p in C.partidas for f in p["final"] if f["raca"] == "Ferreiro"]
    R["ferreiro_niveis_forja_no_fim"] = media(forjas)
    R["mais_comprados"] = C.compras.most_common(15)
    R["menos_comprados"] = sorted(C.compras.items(), key=lambda t: t[1])[:10]
    R["nunca_comprados"] = [i["nome"] for i in shop.CATALOGO if i["nome"] not in C.compras]
    R["itens_usados"] = C.itens_usados.most_common()
    posse = {}
    for nome, (donos, venc) in C.posse_itens.items():
        if donos >= 100:
            posse[nome] = {"donos": donos, "pct_vitoria_do_dono": pct(venc, donos)}
    R["posse_itens"] = dict(sorted(posse.items(), key=lambda t: -t[1]["pct_vitoria_do_dono"]))

    # ouro final e status final do vencedor x perdedores
    fins = collections.defaultdict(list)
    for p in C.partidas:
        for f in p["final"]:
            fins[f["raca"]].append(f)
    R["ouro_parado_no_fim"] = {r: media([f["ouro"] for f in fs]) for r, fs in fins.items()}

    R["ataques_recebidos_por_rodada_viva"] = {
        r: {"ataques": round(C.recebidos[r]["ataques"] / rodadas_vivo[r], 2),
            "dano": round(C.recebidos[r]["dano"] / rodadas_vivo[r], 2)} for r in RACAS if rodadas_vivo[r]}
    R["curas_por_rodada_viva"] = {r: {f: round(v / rodadas_vivo[r], 2) for f, v in C.curas[r].most_common()}
                                  for r in RACAS if rodadas_vivo[r]}
    turnos = {r: sum(C.acoes[r].values()) for r in RACAS}
    R["habilidades_por_turno"] = {r: {h: pct(n, turnos[r]) for h, n in C.habilidades[r].most_common()}
                                  for r in RACAS if C.habilidades[r] and turnos[r]}
    R["ataques_com_penalidade_de_mira"] = {r: pct(sum(1 for a in C.ataques if a[1] == r and a[10]),
                                                  sum(1 for a in C.ataques if a[1] == r)) for r in RACAS}
    mira = [a for a in C.ataques if a[9]]
    R["na_mira"] = {"n": len(mira), "dano_final_medio": media([a[4] for a in mira]),
                    "dano_final_medio_mosqueteiro_sem_mira": media([a[4] for a in C.ataques
                                                                   if a[1] == "Mosqueteiro" and not a[9]])}
    R["dano_por_turno"] = {r: round(sum(a[4] for a in C.ataques if a[1] == r) / turnos[r], 2) for r in RACAS if turnos[r]}
    rod_elim = collections.defaultdict(list)
    for p in C.partidas:
        if p["cenario"] == CENARIO_4J:
            for raca, rod, _ in p["eliminacoes"]:
                rod_elim[raca].append(rod)
    R["rodada_media_de_eliminacao_4j"] = {r: media(v) for r, v in rod_elim.items()}

    # ordem de eliminação
    primeiro = collections.Counter()
    for p in C.partidas:
        if p["cenario"] == CENARIO_4J and p["eliminacoes"]:
            primeiro[p["eliminacoes"][0][0]] += 1
    R["primeiro_eliminado_4j"] = {r: pct(n, sum(primeiro.values())) for r, n in primeiro.most_common()}
    R["bugs"] = {k: {"n": n, "exemplo": C.exemplos_bug.get(k)} for k, n in C.bugs.most_common()}
    return R


TIERS_NOME = {1: "Early", 2: "Mid", 3: "Late"}
CENARIO_4J = "4 jogadores (personagens sorteados, sem repetir)"
CENARIO_56 = "5-6 jogadores (personagens sorteados, pode repetir)"


def modo_massa(n_total, sufixo=""):
    main.console = ConsoleMudo()
    main.animar_dado = lambda *a, **k: None
    main.animar_roleta = lambda *a, **k: None
    instalar_wrappers()
    pares = [(a, b) for i, a in enumerate(RACAS) for b in RACAS[i + 1:]]
    n4 = int(n_total * 0.6)
    nd = int(n_total * 0.24) // len(pares) * len(pares)
    n56 = n_total - n4 - nd
    rng = random.Random(2026)
    inicio = time.time()
    rodar(CENARIO_4J, lambda k: rng.sample(RACAS, 4), n4, 100000)
    print(f"  4 jogadores: {n4} partidas ({time.time() - inicio:.0f}s)", flush=True)
    rodar("duelos", lambda k: rng.sample(list(pares[k % len(pares)]), 2), nd, 200000)
    print(f"  duelos: {nd} partidas ({time.time() - inicio:.0f}s)", flush=True)
    rodar(CENARIO_56, lambda k: [rng.choice(RACAS) for _ in range(rng.randint(5, 6))], n56, 300000)
    print(f"  5-6 jogadores: {n56} partidas ({time.time() - inicio:.0f}s)", flush=True)
    R = analisar()
    R["segundos"] = round(time.time() - inicio)
    with open(os.path.join(AQUI, f"resultados{sufixo}.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=1, default=str)
    print(f"  resultados salvos em simulacao/resultados{sufixo}.json")


def modo_teste():
    from rich.console import Console
    import time as _t
    _t.sleep = lambda s: None
    instalar_wrappers()
    for k, racas in enumerate((["Hemomante", "Alquimista", "Mosqueteiro", "Bárbaro"], ["Mosqueteiro", "Goblin"]), start=1):
        caminho = os.path.join(AQUI, f"partida_teste_{k}.txt")
        with open(caminho, "w", encoding="utf-8") as f:
            main.console = Console(file=f, width=110, color_system=None, force_terminal=False, legacy_windows=False)
            C.cenario = "teste"
            try:
                jogar_partida(racas, 42 + k)
                p = C.partidas[-1]
                print(f"Partida {k}: {racas} → venceu {p['vencedor']} na rodada {p['rodadas']} "
                      f"(entradas do robô: {ROBO.n}) • tela completa em {caminho}")
            except Exception:
                print(f"Partida {k}: ERRO\n{traceback.format_exc()}")
    print("bugs observados:", dict(C.bugs))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "massa":
        modo_massa(int(sys.argv[2]) if len(sys.argv) > 2 else 5000, sys.argv[3] if len(sys.argv) > 3 else "")
    else:
        modo_teste()
