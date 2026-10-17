"""Motor da partida para a janela do jogo (app.py): o mesmo jogo do main.py, sem input() nem print().

A interface (interface/jogo.js) chama Partida.agir(acao, dados) a cada clique e desenha o que Partida.estado()
devolve. As regras continuam no main.py, shop.py e dice.py; aqui fica só o fluxo da partida (de quem é a vez,
qual tela mostrar) e a conversão dos textos do jogo (marcação do rich) para HTML.
"""

import html
import traceback

from rich.console import Console
from rich.errors import MarkupError
from rich.text import Text

import dice
import main
import shop

# Cores do rich usadas nos textos do jogo -> cores legíveis no fundo creme/laranja da janela
CORES_TEXTO = {
    "red": "#b3261e", "bright_red": "#c62828", "green": "#1e7a34", "bright_green": "#2e8b3a",
    "yellow": "#8a5a00", "bright_yellow": "#9a6b00", "blue": "#1d5fa8", "bright_blue": "#2c5fcc",
    "cyan": "#13788a", "bright_cyan": "#0f8a9e", "magenta": "#8e2f8e", "bright_magenta": "#a03aa0",
    "bright_black": "#6b5a3a", "black": "#1a1a1a",
}
# Cor de cada jogador (main.CORES_JOGADORES) nos cartões e bordas
CORES_JOGADOR = {
    "red": "#c0392b", "cyan": "#1f8a9e", "green": "#2e8b3a", "yellow": "#b8860b",
    "magenta": "#8e44ad", "bright_blue": "#2c5fcc",
}
CARACTERES_PROIBIDOS = "[]<>"  # quebrariam a marcação de cores dos textos do jogo

_console = Console(width=10_000, color_system="truecolor", force_terminal=True)


def para_html(marcacao):
    """Converte um texto com a marcação do rich ("[bold red]Ana[/] ataca") em HTML seguro para a janela."""
    if not marcacao:
        return ""
    try:
        texto = Text.from_markup(str(marcacao))
    except MarkupError:
        return html.escape(str(marcacao)).replace("\n", "<br>")
    partes = []
    for seg in texto.render(_console, end=""):
        if not seg.text:
            continue
        trecho = html.escape(seg.text)
        estilo = seg.style
        if estilo:
            css = []
            if estilo.color and estilo.color.name in CORES_TEXTO:
                css.append(f"color:{CORES_TEXTO[estilo.color.name]}")
            if estilo.bold:
                css.append("font-weight:700")
            if estilo.italic:
                css.append("font-style:italic")
            if estilo.strike:
                css.append("text-decoration:line-through")
            elif estilo.underline:
                css.append("text-decoration:underline")
            if css:
                trecho = f'<span style="{";".join(css)}">{trecho}</span>'
        partes.append(trecho)
    return "".join(partes).replace("\n", "<br>")


def cor_jogador(cor):
    return CORES_JOGADOR.get(cor, CORES_TEXTO.get(cor, "#6b4a00"))


def status_curto(j):
    """Os mesmos estados de main.status_jogador, curtos para caber nos cartões (até 6 jogadores lado a lado)."""
    if not j["vivo"]:
        return ["💀 Eliminado"]
    partes = []
    if j["protegido"]:
        partes.append("💢 Protegido")
    if j["invisivel"]:
        partes.append("👻 Invisível")
    if j["postura"]:
        partes.append("🔰 Postura")
    if j["escudo_mana"]:
        partes.append(f"🔮 Escudo ({j['escudo_mana_rodadas']} rod.)")
    if j["escudo_pv"]:
        partes.append(f"🧿 Escudo {j['escudo_pv']}")
    if j["sentenca"]:
        partes.append("📜 Sentenciado")
    if j["acido"]:
        partes.append(f"🧪 Ácido −{j['acido']['valor']}")
    if j["bonus"].get("ultima_provacao") and j["provacao_pronta"]:
        partes.append("🏰 Provação")
    if j["veneno"]:
        partes.append(f"🐍 Veneno −{j['veneno']['dano']}")
    return partes or ["✔ Em pé"]


def tirar_prefixo(mensagem):
    """As mensagens de erro do shop.py começam com "❌ "; a janela mostra o próprio ícone de erro."""
    return mensagem[2:] if mensagem.startswith("❌") else mensagem


# ----------------------------------------------------------------------
# Textos fixos das ações do turno (os mesmos do menu do terminal)
# ----------------------------------------------------------------------
def texto_acao(acao, jogador):
    raca = jogador["raca"]
    textos = {
        "atacar": ("🔪 Atacar oponente",
                   {"Feiticeiro": "custa 1/3 de mana", "Mosqueteiro": "gasta 1 de munição"}.get(
                       raca, "o D10 define o dano: fraco ×0,5, normal ×1, crítico ×2")),
        "postura": ("🔰 Postura defensiva",
                    "até a sua próxima vez, o D10 de defesa bloqueia de 0% a 95% do dano"
                    + (" • com a munição zerada, recarrega" if raca == "Mosqueteiro" else "")),
        "escudo_mana": ("🔮 Escudo de Mana",
                        f"custa 2/3 de mana • mitiga {round(main.ESCUDO_MANA * 100)}% do próximo ataque • "
                        f"dura até {main.ESCUDO_MANA_RODADAS} rodadas"),
        "inventario": ("🎒 Inventário e itens", "consumíveis e itens ativos (os de ação livre não gastam o turno)"),
        "passar": ("⏩ Passar a vez", "não faz nada neste turno"),
        "folego": ("😤 Fôlego de Batalha", f"com a Fúria cheia, cura {round(main.FOLEGO_CURA * 100)}% da vida máxima"),
        "pacto": ("🦇 Pacto de Sangue",
                  f"paga {main.PACTO_CUSTO} de vida: próximo ataque ×{f'{main.PACTO_MULT:g}'.replace('.', ',')}"),
        "na_mira": ("🎯 Na mira", f"próximo disparo ignora Defesa e postura • recarga de {main.NA_MIRA_RECARGA} turnos seus"),
    }
    return textos[acao]


def lista_personagens():
    """Dados de cada personagem para a tela de escolha (atributos já com o item inicial)."""
    lista = []
    for nome, r in main.RACAS.items():
        ref = main.criar_jogador("", nome, "red")
        if nome == "Feiticeiro":
            postura = r["postura"]
        else:
            postura = (f"Até a sua próxima vez, o D10 de defesa bloqueia parte do dano "
                       f"({dice.texto_bloqueio_defesa()}). {r['postura']}")
        itens = [
            f"{i['nome']} ({', '.join(shop.descrever_efeitos(shop.efeitos_efetivos(ref, i), i.get('magico', False)))})"
            for i in ref["itens"]
        ]
        lista.append({
            "nome": nome, "emoji": r["emoji"], "descricao": r["descricao"],
            "vida": ref["hp_max"], "fis": ref["dano_fisico"], "mag": ref["dano_magico"],
            "estilo": f"{shop.ALCANCES[r['alcance']]} • dano {main.ROTULO_AFINIDADE[r['afinidade']]}",
            "passiva": para_html(r["passivo"]),
            "habilidade": para_html(r["habilidade"]) if r["habilidade"] else "",
            "postura": para_html(postura),
            "itens": [para_html(i) for i in itens],
        })
    return lista


class Partida:
    """Uma partida inteira: escolha dos personagens, rodadas, Comerciante e resultado final."""

    def __init__(self):
        self.personagens = lista_personagens()
        self.novo_jogo()

    def novo_jogo(self):
        self.tela = "escolha"      # escolha / turno / loja / fim
        self.modo = None           # o que a caixa principal mostra (acoes, alvo, inventario, painel, estoque...)
        self.quantidade = None
        self.jogadores = []
        self.rodada = 0
        self.ordem = []
        self.vez = 0
        self.registro = []         # histórico de ações (HTML), mais recente primeiro
        self.aviso = None          # mensagem que aparece uma vez: {"tipo": "erro"|"ok", "texto": html}
        self.painel = None         # resultado ou anúncio na caixa principal (com dados, se houver)
        self.alvo_de = None        # para que é a escolha de alvo: {"tipo": "ataque"} ou {"tipo": "item", "item": item}
        self.loja = None
        self.vencedor = None
        main.ELIMINADOS.clear()
        shop.fator_cura_global = 1.0

    # ------------------------------------------------------------------
    # Entrada única da interface
    # ------------------------------------------------------------------
    def agir(self, acao, dados=None):
        """Executa uma ação da interface e devolve o novo estado da tela."""
        dados = dados or {}
        try:
            metodo = getattr(self, f"_acao_{acao}", None)
            if metodo is None:
                self.erro(f"Ação desconhecida: {acao}")
            else:
                metodo(**dados)
        except Exception as e:  # nunca derruba a janela: mostra o erro e deixa o jogo seguir
            traceback.print_exc()
            self.erro(f"Erro inesperado ({type(e).__name__}: {e}). A partida continua.")
        return self.estado()

    def erro(self, texto):
        self.aviso = {"tipo": "erro", "texto": para_html(tirar_prefixo(texto))}

    def ok(self, texto):
        self.aviso = {"tipo": "ok", "texto": para_html(texto)}

    def registrar(self, marcacao):
        self.registro.insert(0, para_html(marcacao))
        del self.registro[60:]

    def mostrar_painel(self, titulo, linhas, depois, botao="Continuar", dados=None, roleta=None):
        """Troca a caixa principal por um painel (resultado de ação, anúncio de rodada, Comerciante...).
        `depois` é o método chamado quando o jogador clica no botão."""
        self.modo = "painel"
        self.painel = {"titulo": titulo, "linhas": linhas, "depois": depois, "botao": botao,
                       "dados": dados or [], "roleta": roleta}

    def _acao_continuar(self):
        if self.modo != "painel" or not self.painel:
            return
        depois = self.painel["depois"]
        self.painel = None
        getattr(self, depois)()

    def _acao_novo_jogo(self):
        self.novo_jogo()

    # ------------------------------------------------------------------
    # Escolha dos jogadores
    # ------------------------------------------------------------------
    def _acao_quantidade(self, n):
        n = int(n)
        if self.tela == "escolha" and main.MIN_JOGADORES <= n <= main.MAX_JOGADORES:
            self.quantidade = n
            del self.jogadores[n:]

    def _acao_trocar_quantidade(self):
        if self.tela == "escolha":
            self.quantidade = None
            self.jogadores = []

    def _acao_entrar(self, nome, personagem):
        if self.tela != "escolha" or not self.quantidade or len(self.jogadores) >= self.quantidade:
            return
        nome = " ".join(str(nome).split())
        if not nome:
            return self.erro("O nome não pode ficar vazio.")
        if len(nome) > 20:
            return self.erro("O nome pode ter no máximo 20 caracteres.")
        if any(c in nome for c in CARACTERES_PROIBIDOS):
            return self.erro("O nome não pode ter os caracteres [ ] < >.")
        if nome.lower() in (j["nome"].lower() for j in self.jogadores):
            return self.erro("Esse nome já está em uso. Escolha outro.")
        if personagem not in main.RACAS:
            return self.erro("Escolha um personagem.")
        cor = main.CORES_JOGADORES[len(self.jogadores)]
        self.jogadores.append(main.criar_jogador(nome, personagem, cor))

    def _acao_refazer(self):
        if self.tela == "escolha":
            self.jogadores = []

    def _acao_comecar(self):
        if self.tela != "escolha" or not self.quantidade or len(self.jogadores) != self.quantidade:
            return
        main.ELIMINADOS.clear()
        self.rodada = 1
        self.iniciar_rodada()

    # ------------------------------------------------------------------
    # Rodadas e turnos
    # ------------------------------------------------------------------
    def atual(self):
        return self.ordem[self.vez] if self.tela == "turno" and self.vez < len(self.ordem) else None

    def iniciar_rodada(self):
        main.RODADA_ATUAL = self.rodada
        shop.fator_cura_global = main.CURA_MORTE_SUBITA if self.rodada >= main.RODADA_MORTE_SUBITA else 1.0
        self.tela = "turno"
        self.ordem = main.sortear_ordem(self.jogadores)
        self.vez = 0
        linhas = []
        if self.rodada > 1 and main.ouro_base_do_turno(self.rodada) > main.ouro_base_do_turno(self.rodada - 1):
            linhas.append(f"💰 [bold yellow]A ECONOMIA AQUECEU![/] A partir de agora cada turno dá "
                          f"+{main.ouro_base_do_turno(self.rodada)} moedas (antes: +{main.ouro_base_do_turno(self.rodada - 1)}).")
        if self.rodada == main.RODADA_MORTE_SUBITA:
            linhas.append(f"💀 [bold red]MORTE SÚBITA![/] A partir de agora todas as curas rendem só "
                          f"{round(main.CURA_MORTE_SUBITA * 100)}%.")
        linhas.append("📋 Ordem da rodada: " + "  ➜  ".join(
            f"{i}º [bold {j['cor']}]{j['nome']}[/]" for i, j in enumerate(self.ordem, start=1)))
        roleta = None
        if self.rodada == 1:
            roleta = {"nomes": [j["nome"] for j in self.jogadores],
                      "cores": [cor_jogador(j["cor"]) for j in self.jogadores],
                      "vencedor": self.jogadores.index(self.ordem[0])}
        titulo = "🎲 Sorteando quem começa" if self.rodada == 1 else f"🔔 Rodada {self.rodada}"
        self.mostrar_painel(titulo, linhas, "comecar_turno", "▶ Começar a rodada", roleta=roleta)

    def comecar_turno(self):
        while self.vez < len(self.ordem) and not self.ordem[self.vez]["vivo"]:
            self.vez += 1
        if self.vez >= len(self.ordem):
            return self.fim_da_rodada()
        j = self.ordem[self.vez]
        main.passar_protecao(self.jogadores)
        aviso = main.inicio_de_turno(j, self.rodada)
        self.registrar(f"[bold {j['cor']}]{j['nome']}[/]: {aviso}")
        self.modo = "acoes"
        self.alvo_de = None

    def fim_do_turno(self):
        sobreviventes = main.vivos(self.jogadores)
        if len(sobreviventes) == 1:
            self.vencedor = sobreviventes[0]
            self.tela = "fim"
            self.modo = None
            return
        self.vez += 1
        self.comecar_turno()

    def fim_da_rodada(self):
        eventos = main.fim_de_rodada(self.jogadores)
        for e in eventos:
            self.registrar(e)
        depois = "abrir_loja" if self.rodada % main.INTERVALO_LOJA == 0 else "proxima_rodada"
        if eventos:
            self.mostrar_painel(f"🌙 Fim da rodada {self.rodada}", eventos, depois)
        else:
            getattr(self, depois)()

    def proxima_rodada(self):
        self.rodada += 1
        self.loja = None
        self.iniciar_rodada()

    def acao_encerra_turno(self, titulo, linhas, registro=None, dados=None):
        """Mostra o resultado de uma ação que gasta o turno; o botão Continuar passa a vez."""
        if registro:
            self.registrar(registro)
        self.mostrar_painel(titulo, linhas, "fim_do_turno", "Continuar", dados=dados)

    # ------------------------------------------------------------------
    # Ações do turno
    # ------------------------------------------------------------------
    def _acao_acao(self, id):
        j = self.atual()
        if not j or self.modo != "acoes" or id not in main.acoes_do_turno(j):
            return
        if id == "atacar":
            bloqueio = main.bloqueio_ataque(j, self.jogadores)
            if bloqueio:
                return self.erro(bloqueio)
            self.alvo_de = {"tipo": "ataque"}
            self.modo = "alvo"
        elif id == "postura":
            msg = main.assumir_postura(j)
            self.acao_encerra_turno("🔰 Postura defensiva", [msg], registro=msg)
        elif id == "escudo_mana":
            bloqueio = main.bloqueio_escudo_mana(j)
            if bloqueio:
                return self.erro(bloqueio)
            msg = main.erguer_escudo_mana(j)
            self.acao_encerra_turno("🔮 Escudo de Mana", [msg], registro=msg)
        elif id == "inventario":
            self.modo = "inventario"
        elif id == "passar":
            msg = f"⏩ [bold {j['cor']}]{j['nome']}[/] passou a vez."
            self.acao_encerra_turno("⏩ Passou a vez", [msg], registro=msg)
        elif id in main.PERGUNTAS_HABILIDADE:  # ação livre: o turno continua
            bloqueio = main.bloqueio_habilidade(j, id)
            if bloqueio:
                return self.erro(bloqueio)
            msg = main.usar_habilidade(j, id)
            self.registrar(msg)
            self.ok(msg)

    def _acao_voltar(self):
        if self.tela == "turno":
            if self.modo == "alvo" and self.alvo_de and self.alvo_de["tipo"] == "item":
                self.modo = "inventario"
            elif self.modo in ("alvo", "inventario"):
                self.modo = "acoes"
            self.alvo_de = None
        elif self.tela == "loja" and self.loja:
            self.loja["selecionado"] = None
            self.loja["mistura"] = []
            self.modo = "estoque"

    def alvos_validos(self, j):
        """Quem pode ser escolhido na escolha de alvo atual (ataque ou item com alvo)."""
        if not self.alvo_de:
            return []
        if self.alvo_de["tipo"] == "item":
            e = self.alvo_de["item"]["efeitos"]
            if "roubo" in e or "acido" in e or "sentenca" in e:
                return main.alvos_afetaveis(j, self.jogadores)
        return main.alvos_disponiveis(j, self.jogadores)

    def _acao_alvo(self, indice):
        j = self.atual()
        if not j or self.modo != "alvo":
            return
        alvo = self.jogadores[int(indice)]
        if alvo not in self.alvos_validos(j):
            return self.erro("Esse alvo não pode ser escolhido agora.")
        hp_antes = alvo["hp"]
        if self.alvo_de["tipo"] == "ataque":
            main.pagar_ataque(j)
            resultado = main.resolver_ataque(j, alvo)
            dados = [{"legenda": t, "valor": v, "cor": cor_jogador(c)} for t, v, c in resultado["dados"]]
            perda = hp_antes - alvo["hp"]
            resumo = (f"🔪 [bold {j['cor']}]{j['nome']}[/] atacou [bold {alvo['cor']}]{alvo['nome']}[/]: "
                      f"🎲 {' + '.join(str(d['valor']) for d in dados)} • −{perda} 💖"
                      + (" • 💀 eliminado!" if not alvo["vivo"] else ""))
            self.alvo_de = None
            return self.acao_encerra_turno("💥 Resultado do ataque", resultado["linhas"], registro=resumo, dados=dados)
        # item com alvo (bomba, raio, roubo, ácido, sentença)
        item = self.alvo_de["item"]
        self.alvo_de = None
        e = item["efeitos"]
        shop.gastar_item(j, item)
        painel = main.efeito_item_com_alvo(j, item, alvo)
        if painel:
            titulo, texto, _ = painel
            linhas = [texto]
        else:
            titulo = "💥 Resultado"
            linhas = main.resolver_dano_direto(j, alvo, e.get("bomba", e.get("raio", 0)), item)
        resumo = f"{item['nome']}: [bold {j['cor']}]{j['nome']}[/] usou em [bold {alvo['cor']}]{alvo['nome']}[/]"
        if not alvo["vivo"]:
            resumo += " • 💀 eliminado!"
        if e.get("livre"):  # ação livre com alvo (Luvas do Ladrão, Coroa): o turno continua
            self.registrar(resumo)
            linhas.append("🆓 [green]Ação livre: o seu turno continua.[/]")
            depois = "fim_do_turno" if len(main.vivos(self.jogadores)) == 1 else "voltar_acoes"
            return self.mostrar_painel(titulo, linhas, depois, "Voltar às ações")
        self.acao_encerra_turno(titulo, linhas, registro=resumo)

    def voltar_acoes(self):
        self.modo = "acoes"

    def _acao_usar(self, indice):
        j = self.atual()
        if not j or self.modo != "inventario":
            return
        indice = int(indice)
        if not 0 <= indice < len(j["itens"]):
            return
        item = j["itens"][indice]
        pode, msg = shop.pode_usar(j, item)
        if not pode:
            return self.erro(msg)
        if shop.exige_alvo(item):
            self.alvo_de = {"tipo": "item", "item": item}
            if not self.alvos_validos(j):
                self.alvo_de = None
                return self.erro("Nenhum alvo disponível agora (protegidos por terem sido atacados no turno anterior, "
                                 "ou invisíveis).")
            self.modo = "alvo"
            return
        usou, msg = shop.usar_item(j, item)
        if not usou:
            return self.erro(msg)
        if item["efeitos"].get("livre"):  # ação livre: o turno continua
            self.registrar(f"[bold {j['cor']}]{j['nome']}[/]: {msg}")
            self.ok(msg)
            self.modo = "acoes"
            return
        self.acao_encerra_turno("🎒 Item usado", [msg], registro=f"[bold {j['cor']}]{j['nome']}[/]: {msg}")

    # ------------------------------------------------------------------
    # O Comerciante
    # ------------------------------------------------------------------
    def abrir_loja(self):
        r = self.rodada
        compradores = shop.ordem_compras(self.jogadores)
        curas = []
        for j in compradores:  # mesmo começo da fase_loja do terminal
            j["ouro"] += main.OURO_LOJA + (int(main.OURO_LOJA * main.BONUS_GOBLIN) if j["raca"] == "Goblin" else 0)
            cura = shop.aplicar_cura(j, j["hp_max"] * main.CURA_COMERCIANTE, "Comerciante")
            j["mistura_usada"] = False
            j["provacao_pronta"] = True
            curas.append(f"[{j['cor']}]{j['nome']}[/] +{cura} 💖 {j['hp']}/{j['hp_max']}")
            j["forja_usada"] = False
            j["pechinchar_pronto"] = True
            j["compras_visita"] = {}
        self.tela = "loja"
        self.loja = {"compradores": compradores, "vez": 0, "estoque": [], "comprados": [], "resumo": [],
                     "selecionado": None, "mistura": [], "fase": shop.fase_da_rodada(r)}
        pocao = shop.pocao_fixa(r)
        nome_fase = main.TIERS[self.loja["fase"]][0]
        linhas = [
            f"Rodada exclusiva de compras: cada jogador recebe [bold yellow]+{main.OURO_LOJA} moedas[/] e recupera "
            f"{round(main.CURA_COMERCIANTE * 100)}% da vida máxima.",
            f"Cada jogador tem um estoque próprio de {shop.ITENS_POR_JOGADOR} itens, sorteado só para ele, mais a "
            f"{pocao['emoji']} {pocao['nome']} sempre à venda • até {shop.texto_limite_compras()} por jogador.",
            f"Rodada {r} • só itens da fase [bold]{nome_fase}[/] ({shop.texto_fases()}).",
            "💚 " + "   ".join(curas),
        ]
        self.mostrar_painel("🧳 O Comerciante chegou!", linhas, "proximo_comprador", "Abrir o Comerciante")

    def comprador(self):
        L = self.loja
        return L["compradores"][L["vez"]] if self.tela == "loja" and L and L["vez"] < len(L["compradores"]) else None

    def proximo_comprador(self):
        L = self.loja
        if L["vez"] >= len(L["compradores"]):
            return self.fechar_loja()
        L["estoque"] = shop.sortear_estoque(self.rodada)
        L["comprados"] = []
        L["selecionado"] = None
        L["mistura"] = []
        self.modo = "estoque"

    def fechar_loja(self):
        for j in self.jogadores:  # Pechinchar, Forja e Mistura voltam ao normal quando o Comerciante parte
            j["pechinchar_pronto"] = True
            j["forja_usada"] = False
            j["mistura_usada"] = False
        linhas = ["Compras desta visita:"] + [f"  • {linha}" for linha in self.loja["resumo"]] + ["", "O combate será retomado!"]
        self.mostrar_painel("🧳 O Comerciante partiu", linhas, "proxima_rodada", "⚔️ Voltar ao combate")

    def _acao_item(self, indice):
        j = self.comprador()
        if not j or self.modo != "estoque":
            return
        indice = int(indice)
        item = self.loja["estoque"][indice]
        bloqueio = shop.bloqueio_compra(j, item)
        if bloqueio:
            return self.erro(bloqueio)
        self.loja["selecionado"] = indice

    def _acao_comprar(self):
        j = self.comprador()
        L = self.loja
        if not j or self.modo != "estoque" or L["selecionado"] is None:
            return
        item = L["estoque"][L["selecionado"]]
        if item["tipo"] != "consumivel" and shop.slot_cheio(j, item["tipo"]) and j["ouro"] >= item["preco"] \
                and not shop.bloqueio_compra(j, item):
            self.modo = "substituir"
            return
        self.finalizar_compra(item, None)

    def _acao_substituir(self, indice):
        j = self.comprador()
        L = self.loja
        if not j or self.modo != "substituir":
            return
        item = L["estoque"][L["selecionado"]]
        candidatos = shop.itens_do_slot(j, item["tipo"])
        self.modo = "estoque"
        self.finalizar_compra(item, candidatos[int(indice)])

    def finalizar_compra(self, item, substituir):
        j = self.comprador()
        sucesso, msg = shop.comprar(j, item, substituir)
        if sucesso:
            self.loja["comprados"].append(f"{item['emoji']} {item['nome']}")
            self.loja["selecionado"] = None
            self.ok(msg)
        else:
            self.erro(msg)

    def _acao_forja(self):
        j = self.comprador()
        if not j or self.modo != "estoque" or j["raca"] != "Ferreiro":
            return
        if j["forja_usada"]:
            return self.erro("A Forja já foi usada nesta visita do Comerciante.")
        equipaveis = [i for i in j["itens"] if i["tipo"] in shop.EQUIPAVEIS]
        if not equipaveis:
            return self.erro("Você não tem armas ou armaduras para forjar.")
        if not [i for i in equipaveis if i.get("forja", 0) < shop.MAX_FORJA]:
            return self.erro(f"Todos os seus itens já estão no nível máximo da Forja ({shop.MAX_FORJA}).")
        self.loja["selecionado"] = None
        self.modo = "forja"

    def forjaveis(self, j):
        return [i for i in j["itens"] if i["tipo"] in shop.EQUIPAVEIS and i.get("forja", 0) < shop.MAX_FORJA]

    def _acao_forjar(self, indice):
        j = self.comprador()
        if not j or self.modo != "forja":
            return
        sucesso, msg = shop.forjar(j, self.forjaveis(j)[int(indice)])
        self.modo = "estoque"
        self.ok(msg) if sucesso else self.erro(msg)

    def pode_misturar(self, j):
        opcoes = shop.misturaveis(j)
        return len(opcoes) >= 2 or (opcoes and opcoes[0].get("usos", 1) >= 2)

    def _acao_mistura(self):
        j = self.comprador()
        if not j or self.modo != "estoque" or j["raca"] != "Alquimista":
            return
        if j["mistura_usada"]:
            return self.erro("A Mistura já foi usada nesta visita do Comerciante.")
        if not self.pode_misturar(j):
            return self.erro("Você precisa de 2 consumíveis (bombas não entram) para fazer uma Mistura.")
        self.loja["selecionado"] = None
        self.loja["mistura"] = []
        self.modo = "mistura"

    def _acao_ingrediente(self, indice):
        """Alquimista: marca/desmarca um consumível da Mistura (o mesmo item pode entrar 2 vezes se tiver 2 usos)."""
        j = self.comprador()
        if not j or self.modo != "mistura":
            return
        escolhidos = self.loja["mistura"]
        indice = int(indice)
        opcoes = shop.misturaveis(j)
        if not 0 <= indice < len(opcoes):
            return
        if escolhidos.count(indice) and (escolhidos.count(indice) >= opcoes[indice].get("usos", 1) or len(escolhidos) >= 2):
            escolhidos.remove(indice)
        elif len(escolhidos) < 2:
            escolhidos.append(indice)

    def _acao_misturar(self):
        j = self.comprador()
        L = self.loja
        if not j or self.modo != "mistura" or len(L["mistura"]) != 2:
            return
        opcoes = shop.misturaveis(j)
        sucesso, msg = shop.misturar(j, opcoes[L["mistura"][0]], opcoes[L["mistura"][1]])
        L["mistura"] = []
        self.modo = "estoque"
        self.ok(msg) if sucesso else self.erro(msg)

    def _acao_sair_loja(self):
        j = self.comprador()
        L = self.loja
        if not j or self.modo not in ("estoque", "forja", "mistura", "substituir"):
            return
        L["resumo"].append(f"[{j['cor']}]{j['nome']}[/]: {', '.join(L['comprados']) if L['comprados'] else 'não comprou nada'}")
        L["vez"] += 1
        self.proximo_comprador()

    # ------------------------------------------------------------------
    # Estado para a interface
    # ------------------------------------------------------------------
    def cartao(self, j):
        r = main.RACAS[j["raca"]]
        status = main.status_jogador(j)
        return {
            "indice": self.jogadores.index(j), "nome": j["nome"], "personagem": j["raca"], "emoji": r["emoji"],
            "cor": cor_jogador(j["cor"]), "vida": j["hp"], "max": j["hp_max"], "ouro": j["ouro"], "vivo": j["vivo"],
            "status": [para_html(s) for s in status],
            "curto": status_curto(j),  # versão curta para os cartões da caixa de cima
            "dica": " • ".join(Text.from_markup(s).plain for s in status),
        }

    def painel_jogador(self, j, info=True):
        """Caixa da direita: tudo sobre o jogador da vez."""
        dados = self.cartao(j)
        defesa = f"{main.defesa_total(j):g}"
        if j["acido"] or j["defesa_temp"]:
            defesa += "*"
        espacos = []
        for tipo in shop.LIMITE_SLOTS:
            itens = shop.itens_do_slot(j, tipo)
            espacos.append({
                "rotulo": shop.ROTULO_SLOT[tipo].capitalize(), "usados": len(itens), "limite": shop.limite_slot(j, tipo),
                "itens": [para_html(i["nome"] + (f" [yellow]🔨{i['forja']}[/]" if i.get("forja") else "")) for i in itens],
            })
        consumiveis = [i["nome"] + (f" ×{i['usos']}" if i.get("usos", 1) > 1 else "")
                       for i in j["itens"] if i["tipo"] == "consumivel"]
        dados.update({
            "fis": shop.num(j["dano_fisico"]), "mag": shop.num(j["dano_magico"]), "defesa": defesa,
            "recurso": para_html(main.linha_recurso(j)),
            "buffs": para_html(main.linha_buffs(j)),
            "espacos": espacos,
            "consumiveis": [para_html(c) for c in consumiveis],
            "info": [para_html(linha) for linha in main.info_rodada(self.rodada)] if info else [],
        })
        return dados

    def dados_painel(self):
        p = self.painel
        return {"titulo": para_html(p["titulo"]), "linhas": [para_html(l) for l in p["linhas"]], "botao": p["botao"],
                "dados": p["dados"], "roleta": p["roleta"]}

    def dados_acoes(self, j):
        acoes = []
        for acao in main.acoes_do_turno(j):
            bloqueio = None
            if acao == "atacar":
                bloqueio = main.bloqueio_ataque(j, self.jogadores)
            elif acao == "escudo_mana":
                bloqueio = main.bloqueio_escudo_mana(j)
            elif acao in main.PERGUNTAS_HABILIDADE:
                bloqueio = main.bloqueio_habilidade(j, acao)
            nome, desc = texto_acao(acao, j)
            acoes.append({"id": acao, "nome": nome, "desc": desc, "livre": acao in main.PERGUNTAS_HABILIDADE,
                          "bloqueio": bloqueio})
        return acoes

    def dados_alvos(self, j):
        validos = self.alvos_validos(j)
        alvos = []
        for o in main.vivos(self.jogadores):
            if o is j:
                continue
            motivo = None
            if o not in validos:
                motivo = "👻 Invisível" if o["invisivel"] else "💢 Protegido: foi atacado no turno anterior"
            dados = self.cartao(o)
            dados.update({"defesa": f"{main.defesa_total(o):g}", "bloqueio": motivo})
            alvos.append(dados)
        if self.alvo_de and self.alvo_de["tipo"] == "item":
            item = self.alvo_de["item"]
            titulo = "🧤 De quem roubar?" if "roubo" in item["efeitos"] else f"🎯 Alvo de {item['nome']}"
        else:
            titulo = "🎯 Escolha o alvo do ataque"
        return {"titulo": titulo, "lista": alvos}

    def dados_inventario(self, j):
        itens = []
        for i, item in enumerate(j["itens"]):
            rotulo, cor = main.TIPOS_ITEM[item["tipo"]]
            usavel = item["tipo"] in ("consumivel", "ativo")
            if item["tipo"] == "ativo":
                estado = "pronto" if item.get("recarga_atual", 0) == 0 else f"⏳ {item['recarga_atual']} turno(s)"
            elif item["tipo"] == "consumivel":
                estado = f"{item.get('usos', 1)} uso(s)"
            elif "recarga" in item["efeitos"] and item.get("recarga_atual", 0) > 0:
                estado = f"equipado • ⏳ {item['recarga_atual']} turno(s)"
            else:
                estado = "equipado"
            bloqueio = None
            if usavel:
                pode, msg = shop.pode_usar(j, item)
                bloqueio = None if pode else tirar_prefixo(msg)
            forja = item.get("forja", 0)
            itens.append({
                "indice": i,
                "nome": para_html(item["nome"] + (f" [yellow]🔨+{round(forja * shop.BONUS_FORJA * 100)}%[/]" if forja else "")
                                  + (f" ×{item['usos']}" if item["tipo"] == "consumivel" and item.get("usos", 1) > 1 else "")),
                "tipo": rotulo, "cor": CORES_TEXTO.get(cor, "#6b4a00"),
                "efeitos": [para_html(l) for l in shop.descrever_efeitos(shop.efeitos_efetivos(j, item), item.get("magico", False))],
                "estado": estado, "usavel": usavel, "bloqueio": bloqueio,
                "livre": bool(item["efeitos"].get("livre")), "alvo": shop.exige_alvo(item),
            })
        return itens

    def dados_estoque(self, j):
        lista = []
        for i, item in enumerate(self.loja["estoque"]):
            rotulo, cor = main.TIPOS_ITEM[item["tipo"]]
            efeitos = shop.efeitos_efetivos(j, item)
            linhas = shop.descrever_efeitos(efeitos, item.get("magico", False), item.get("usos", 1))
            lista.append({
                "indice": i, "emoji": item["emoji"], "nome": item["nome"], "tipo": rotulo,
                "cor": CORES_TEXTO.get(cor, "#6b4a00"), "fase": main.TIERS[item["tier"]][0], "preco": item["preco"],
                "disponivel": item["disponivel"], "efeitos": [para_html(l) for l in linhas],
                "aviso": any(("❗" in l) for l in linhas), "fixa": item["nome"] == shop.pocao_fixa(self.rodada)["nome"],
            })
        return lista

    def dados_item_selecionado(self, j):
        """Detalhes do item escolhido no estoque (o mesmo conteúdo do painel_item do terminal)."""
        L = self.loja
        if L["selecionado"] is None:
            return None
        item = L["estoque"][L["selecionado"]]
        linhas = []
        if item["tipo"] in shop.EQUIPAVEIS and j.get("mult_equip", 1.0) > 1:
            linhas.append(f"🔨 [bright_black]Já inclui o bônus de +{round((j['mult_equip'] - 1) * 100)}% do Ferreiro[/]")
        if j["raca"] == "Goblin" and j["pechinchar_pronto"]:
            linhas.append(f"💰 [green]Pechinchar pronto: {round(shop.CHANCE_PECHINCHA * 100)}% de chance de "
                          f"{round(shop.DESCONTO_PECHINCHA * 100)}% de desconto ao comprar[/]")
        if item["tipo"] == "consumivel":
            linhas.append("🎒 [bright_black]Vai para o inventário e é usado pelo menu de itens (ação livre ou gasta o turno, "
                          "conforme o item).[/]")
            if j.get("usos_extra_consumivel"):
                linhas.append(f"🔬 [green]Bolsa de poções: você recebe +{j['usos_extra_consumivel']} uso.[/]")
        else:
            usados = len(shop.itens_do_slot(j, item["tipo"]))
            limite = shop.limite_slot(j, item["tipo"])
            linhas.append(f"🔧 [bright_black]Bônus aplicado enquanto estiver equipado (espaço de "
                          f"{shop.ROTULO_SLOT[item['tipo']]}: {usados}/{limite}).[/]")
            if item["tipo"] == "ativo":
                linhas.append("💡 [bright_black]Use pelo Inventário; depois de usado, entra em recarga.[/]")
            if shop.slot_cheio(j, item["tipo"]):
                linhas.append("🔁 [bold yellow]Espaço cheio: você vai escolher qual item equipado substituir.[/]")
        bloqueio = shop.bloqueio_compra(j, item)
        if not bloqueio and j["ouro"] < item["preco"]:
            bloqueio = f"Moedas insuficientes (faltam {item['preco'] - j['ouro']})."
        return {
            "indice": L["selecionado"], "emoji": item["emoji"], "nome": item["nome"], "descricao": item["descricao"],
            "tipo": main.TIPOS_ITEM[item["tipo"]][0], "fase": main.TIERS[item["tier"]][0], "preco": item["preco"],
            "pode_pagar": j["ouro"] >= item["preco"],
            "efeitos": [para_html(l) for l in shop.descrever_efeitos(shop.efeitos_efetivos(j, item), item.get("magico", False),
                                                                     item.get("usos", 1))],
            "detalhes": [para_html(l) for l in linhas],
            "bloqueio": tirar_prefixo(bloqueio) if bloqueio else None,
        }

    def dados_loja(self, j):
        L = self.loja
        d = {
            "rodada": self.rodada, "fase": main.TIERS[L["fase"]][0],
            "ordem": [{"nome": c["nome"], "estado": "atual" if i == L["vez"] else "feito" if i < L["vez"] else ""}
                      for i, c in enumerate(L["compradores"])],
            "proximo": L["compradores"][L["vez"] + 1]["nome"] if j and L["vez"] + 1 < len(L["compradores"]) else None,
        }
        if not j:
            return d
        d["compras"] = [{"rotulo": shop.ROTULO_CATEGORIA[c].capitalize(),
                         "feitas": j["compras_visita"].get(c, 0), "limite": shop.limite_compras(j, c)}
                        for c in shop.LIMITE_COMPRAS]
        d["esgotadas"] = shop.compras_esgotadas(j)
        d["estoque"] = self.dados_estoque(j)
        d["selecionado"] = self.dados_item_selecionado(j)
        extras = []
        if j["raca"] == "Ferreiro":
            extras.append({"id": "forja", "nome": "🔨 Usar A Forja",
                           "bloqueio": "já usada nesta visita" if j["forja_usada"] else None})
        if j["raca"] == "Alquimista":
            extras.append({"id": "mistura", "nome": "🔬 Fazer uma Mistura",
                           "bloqueio": "já usada nesta visita" if j["mistura_usada"]
                           else None if self.pode_misturar(j) else "precisa de 2 consumíveis"})
        d["extras"] = extras
        if self.modo == "substituir" and L["selecionado"] is not None:
            item = L["estoque"][L["selecionado"]]
            d["substituir"] = {
                "titulo": f"🔁 Espaço de {shop.ROTULO_SLOT[item['tipo']]} cheio: qual item substituir por "
                          f"{item['emoji']} {item['nome']}?",
                "lista": [{"indice": i, "nome": para_html(c["nome"]),
                           "efeitos": [para_html(l) for l in shop.descrever_efeitos(shop.efeitos_efetivos(j, c), c.get("magico", False))]}
                          for i, c in enumerate(shop.itens_do_slot(j, item["tipo"]))],
            }
        if self.modo == "forja":
            d["forja"] = {
                "titulo": f"🔨 A Forja • +{round(shop.BONUS_FORJA * 100)}% e {shop.texto_forja_fixo('arma')} (arma) ou "
                          f"{shop.texto_forja_fixo('armadura')} (armadura) por nível (máx. {shop.MAX_FORJA})",
                "lista": [{"indice": i, "nome": para_html(c["nome"]), "nivel": c.get("forja", 0), "max": shop.MAX_FORJA,
                           "efeitos": [para_html(l) for l in shop.descrever_efeitos(shop.efeitos_efetivos(j, c), c.get("magico", False))]}
                          for i, c in enumerate(self.forjaveis(j))],
            }
        if self.modo == "mistura":
            d["mistura"] = {
                "escolhidos": L["mistura"],
                "lista": [{"indice": i, "nome": para_html(c["nome"]), "usos": c.get("usos", 1),
                           "efeitos": [para_html(l) for l in shop.descrever_efeitos(c["efeitos"])]}
                          for i, c in enumerate(shop.misturaveis(j))],
            }
        return d

    def classificacao(self):
        """Vencedor primeiro e depois do último ao primeiro eliminado (como a tabela final do terminal)."""
        venc = self.vencedor
        eliminados = sorted((j for j in self.jogadores if j is not venc), key=lambda j: (
            -j.get("rodada_morte", 0), -main.ELIMINADOS.index(j) if j in main.ELIMINADOS else 0))
        lista = []
        for pos, j in enumerate([venc] + eliminados, start=1):
            dados = self.cartao(j)
            dados.update({"posicao": pos, "vencedor": j is venc, "rodada_morte": j.get("rodada_morte"),
                          "equipamentos": para_html(main.texto_equipamentos(j))})
            lista.append(dados)
        return lista

    def estado(self):
        """Tudo o que a interface precisa para desenhar a tela atual."""
        e = {"tela": self.tela, "modo": self.modo, "aviso": self.aviso, "registro": self.registro[:5]}
        self.aviso = None  # o aviso aparece uma vez só
        if self.modo == "painel" and self.painel:
            e["painel"] = self.dados_painel()
        if self.tela == "escolha":
            e.update({"quantidade": self.quantidade, "min": main.MIN_JOGADORES, "max": main.MAX_JOGADORES,
                      "personagens": self.personagens,
                      "jogadores": [{"nome": j["nome"], "personagem": j["raca"], "emoji": main.RACAS[j["raca"]]["emoji"],
                                     "cor": cor_jogador(j["cor"])} for j in self.jogadores],
                      "cores": [cor_jogador(c) for c in main.CORES_JOGADORES]})
            return e
        e["rodada"] = self.rodada
        e["jogadores"] = [self.cartao(j) for j in self.jogadores]
        if self.tela == "turno":
            j = self.atual()
            e["ordem"] = [{"nome": o["nome"], "estado": "fora" if not o["vivo"] else "atual" if i == self.vez else ""}
                          for i, o in enumerate(self.ordem)]
            if j and self.modo != "painel" or (j and self.painel and self.painel["depois"] != "comecar_turno"):
                e["atual"] = self.jogadores.index(j)
                e["lateral"] = self.painel_jogador(j)
            if j and self.modo == "acoes":
                e["acoes"] = self.dados_acoes(j)
            elif j and self.modo == "alvo":
                e["alvos"] = self.dados_alvos(j)
            elif j and self.modo == "inventario":
                e["inventario"] = self.dados_inventario(j)
        elif self.tela == "loja":
            j = self.comprador()
            e["loja"] = self.dados_loja(j)
            if j:
                e["atual"] = self.jogadores.index(j)
                e["lateral"] = self.painel_jogador(j, info=False)
        elif self.tela == "fim":
            e["classificacao"] = self.classificacao()
            e["lateral"] = self.painel_jogador(self.vencedor, info=False)
            e["atual"] = self.jogadores.index(self.vencedor)
        return e
