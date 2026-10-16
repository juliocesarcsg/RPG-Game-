"""O Comerciante: catálogo, estoque, regras de compra/uso e cálculo de status dos itens (sem interface)."""

import random

ITENS_POR_JOGADOR = 5       # tamanho do estoque exclusivo que cada jogador vê no Comerciante
EQUIPAVEIS = ("arma", "armadura")  # itens de combate físico (recebem Mestre do Metal e A Forja)
LIMITE_SLOTS = {"arma": 2, "armadura": 1, "joia": 2, "ativo": 2}   # quantos itens equipados de cada tipo
ROTULO_SLOT = {"arma": "armas", "armadura": "armadura", "joia": "joias", "ativo": "itens ativos"}
SLOTADOS = tuple(LIMITE_SLOTS)      # tipos que ocupam espaço e dão bônus enquanto equipados
CHANCE_PECHINCHA = 0.35     # Goblin: chance de conseguir desconto (antes: 25%)
DESCONTO_PECHINCHA = 0.15   # Goblin: tamanho do desconto (antes: 10%)
BONUS_FORJA = 0.10          # Ferreiro: ganho por uso de A Forja (antes: 0.15)
MAX_FORJA = 3               # Ferreiro: níveis máximos de Forja por item
PENALIDADE_AFINIDADE = 0.5  # dano de item fora da afinidade do personagem (ex.: mágico num personagem físico) rende 50%
PENALIDADE_MIRA = 1         # arma de alcance diferente do personagem (corpo a corpo x à distância): −1 no D10 de ataque
ALCANCES = {"melee": "corpo a corpo", "ranged": "à distância", "hibrido": "híbrido"}
FORJA_FIXO = {"arma": {"dano": 1}, "armadura": {"defesa": 1, "hp_max": 10}}  # Ferreiro: pontos inteiros por nível de Forja (além do %)
MESTRE_METAL = 1.10         # Ferreiro: eficiência de armas e armaduras (antes: 1.25)
LIMITE_COMPRAS = {"equipamento": 1, "consumivel": 1}  # por visita: 1 equipamento e 1 consumível (antes: 2 itens quaisquer)
ROTULO_CATEGORIA = {"equipamento": "equipamento", "consumivel": "consumível"}
ROTULO_CATEGORIA_PLURAL = {"equipamento": "equipamentos", "consumivel": "consumíveis"}
VENENO_RODADAS = 3          # duração do veneno (ele nunca elimina: deixa no mínimo 1 de vida)
DEFESA_TEMP_RODADAS = 2     # duração da Defesa temporária das poções

# Fases do jogo: o Comerciante só oferece itens da fase em que a partida está
TIERS = {1: "Early", 2: "Mid", 3: "Late"}
FASES_POR_RODADA = ((9, 1), (19, 2))  # até a rodada 9: Early; Mid a partir da 10; Late a partir da 20 (antes: 15 e 30)


def texto_fases():
    """Texto dos limites de fase para a interface (ex.: 'Early até a rodada 9, Mid a partir da 10, Late a partir da 20')."""
    (lim1, _), (lim2, _) = FASES_POR_RODADA
    return f"Early até a rodada {lim1}, Mid a partir da {lim1 + 1}, Late a partir da {lim2 + 1}"


def fase_da_rodada(rodada):
    """Fase (1=Early, 2=Mid, 3=Late) dos itens que o Comerciante oferece na rodada informada."""
    for limite, fase in FASES_POR_RODADA:
        if rodada <= limite:
            return fase
    return 3


CATEGORIAS_GARANTIDAS = ("consumivel", "arma", "armadura", "joia", "ativo")  # o estoque tenta ter 1 de cada (se a fase tiver)

# Bônus passivos dos itens equipados que se somam em jogador["bonus"] (e seus tetos)
SOMADOS = ("crit", "penetracao", "vampirismo", "espinhos", "ouro_turno", "ouro_ataque",
           "cura_turno", "bloqueio_postura", "furia_extra", "mana_regen")
TETOS_BONUS = {"crit": 3, "penetracao": 0.9, "vampirismo": 0.5, "bloqueio_postura": 0.3,
               "furia_extra": 2, "mana_regen": 2}
ESCALAVEIS = ("dano", "defesa", "hp_max")  # só estes valores crescem com Mestre do Metal e A Forja


# Tipo de dano de um item (campo `magico`): False = físico, True = mágico, DANO_HIBRIDO = metade de cada.
# O dano do item soma no status "Dano Físico" ou "Dano Mágico" do jogador (híbrido: 50% em cada).
DANO_HIBRIDO = "hibrido"


def icone_dano(magico):
    """Ícone do dano: 🔪 físico, 🌠 mágico, 🔪🌠 híbrido."""
    if magico == DANO_HIBRIDO:
        return "🔪🌠"
    return "🌠" if magico else "🔪"


def partes_do_dano(valor, magico):
    """Divide um valor de dano de item em (físico, mágico) conforme o tipo de dano do item."""
    if magico == DANO_HIBRIDO:
        return valor / 2, valor / 2
    return (0, valor) if magico else (valor, 0)


def _item(nome, emoji, tipo, tier, preco, efeitos, descricao, magico=False, usos=1, alcance=None):
    return {"nome": nome, "emoji": emoji, "tipo": tipo, "tier": tier, "preco": preco,
            "efeitos": efeitos, "descricao": descricao, "magico": magico, "usos": usos, "alcance": alcance}


# tipo: "consumivel" (uso único), "arma"/"armadura"/"joia"/"ativo" (equipados em espaços limitados)
CATALOGO = [
    # ------------------------------ CONSUMÍVEIS ------------------------------
    # (preços cerca de 30% menores que na versão anterior, para competirem com os equipamentos; as curas mantêm o
    #  preço original, porque curas baratas deixavam partidas sem fim)
    _item("Poção de Cura", "🧪", "consumivel", 1, 24, {"cura": 30},
          "Frascos de ervas curativas. Barato e confiável.", usos=1),
    _item("Antídoto", "🌿", "consumivel", 1, 10, {"antidoto": True, "cura": 10},
          "Neutraliza qualquer veneno e ainda devolve um pouco de vida.", usos=1),
    _item("Trevo da Sorte", "🍀", "consumivel", 2, 18, {"buff_rolagem": 4, "livre": True},
          "Mastigue antes de atacar: soma +4 na rolagem do próximo D10 de ataque.", usos=1),
    _item("Poção de Fúria", "🔥", "consumivel", 1, 20, {"buff_dano": 2.0, "livre": True},
          "Um gole e o sangue ferve: o seu próximo ataque causa o DOBRO de dano.", usos=1),
    _item("Frasco de Veneno", "🐍", "consumivel", 1, 24, {"veneno_arma": 2, "livre": True},
          "Banhe a lâmina: o próximo ataque que ferir envenena o alvo.", usos=1),
    _item("Bombinha", "🧨", "consumivel", 1, 22, {"bomba": 10},
          "Explosivos caseiros. Atingem um oponente que não esteja protegido, ignorando Defesa e postura.", usos=1),
    _item("Elixir Maior", "🍷", "consumivel", 2, 40, {"cura": 60},
          "Elixir concentrado que fecha até feridas profundas."),
    _item("Pele de Pedra", "🧱", "consumivel", 2, 30, {"defesa_temp": 4, "livre": True},
          "A pele endurece como rocha por um tempo.", usos=1),
    _item("Bomba de Pólvora", "💣", "consumivel", 2, 34, {"bomba": 14},
          "Estrondosas. Atingem um oponente que não esteja protegido, ignorando Defesa e postura.", usos=1),
    _item("Essência de Escorpião", "🦂", "consumivel", 3, 42, {"veneno_arma": 4, "livre": True},
          "Veneno concentrado: o próximo ataque que ferir envenena com força.", usos=1),
    _item("Elixir Dourado", "🍶", "consumivel", 3, 55, {"cura": 70, "antidoto": True},
          "A cura dos reis: restaura vida e remove venenos.", usos=1),

    # --------------------------------- ARMAS ---------------------------------
    # alcance: "melee" (corpo a corpo) ou "ranged" (à distância). Arma de alcance diferente do personagem: −1 no D10.
    _item("Espada de Aço", "🔪", "arma", 1, 25, {"dano": 4},
          "Lâmina bem forjada, equilibrada e afiada.", alcance="melee"),
    _item("Orbe Mágico", "🔮", "arma", 1, 25, {"dano": 4},
          "Orbe que carrega consigo um grande poder mágico.", magico=True, alcance="ranged"),
    _item("Machadinha", "🪓", "arma", 1, 30, {"dano": 4, "crit": 1},
          "Leve e traiçoeira: acerta pontos fracos com mais frequência.", alcance="melee"),
    _item("Manoplas do Saqueador", "🥊", "arma", 1, 30, {"dano": 3, "ouro_ataque": 2},
          "Cada soco derruba algumas moedas do bolso do adversário.", alcance="melee"),
    _item("Besta Leve", "🏹", "arma", 1, 28, {"dano": 4},
          "Pequena e fácil de recarregar: a primeira arma de quem luta à distância.", alcance="ranged"),
    _item("Lança Rúnica", "🔱", "arma", 2, 60, {"dano": 7},
          "Arma encantada com runas antigas que brilham em combate.", alcance="melee"),
    _item("Arco Longo", "🏹", "arma", 2, 50, {"dano": 5, "crit": 1},
          "Mira precisa: pontos vitais ficam mais fáceis de acertar.", alcance="ranged"),
    _item("Maça Estilhaçadora", "🔨", "arma", 2, 50, {"dano": 5, "penetracao": 0.30},
          "Pesada o bastante para amassar armaduras: ignora parte da Defesa.", alcance="melee"),
    _item("Machado Sedento", "🪓", "arma", 2, 52, {"dano": 5, "vampirismo": 0.15},
          "Bebe o sangue do inimigo: devolve parte do dano causado como vida.", alcance="melee"),
    _item("Presa de Víbora", "🐍", "arma", 2, 46, {"dano": 3, "veneno": 3},
          "Os ferimentos infeccionam: seus ataques envenenam o alvo.", alcance="melee"),
    _item("Cajado Arcano", "🌟", "arma", 2, 55, {"dano": 5, "penetracao": 0.25},
          "Canaliza energia pura que atravessa parte das defesas.", magico=True, alcance="ranged"),
    _item("Lâmina Lunar", "🌙", "arma", 3, 90, {"dano": 7, "crit": 2},
          "Forjada sob a lua cheia: aço e magia em um só golpe, com críticos muito mais comuns.", magico=DANO_HIBRIDO,
          alcance="melee"),
    _item("Mosquete", "🔫", "arma", 3, 100, {"dano": 9, "penetracao": 0.40},
          "Estampido devastador que atravessa couraças.", alcance="ranged"),
    _item("Grimório Sombrio", "📖", "arma", 3, 95, {"dano": 7, "vampirismo": 0.15, "penetracao": 0.15},
          "Páginas famintas: drena a vida de quem as magias tocam.", magico=True, alcance="ranged"),

    # -------------------------------- ARMADURAS --------------------------------
    _item("Armadura de Couro", "🥋", "armadura", 1, 30, {"hp_max": 35, "defesa": 1},
          "Leve e flexível. Protege sem atrapalhar os movimentos."),
    _item("Gibão Acolchoado", "🧥", "armadura", 1, 26, {"hp_max": 20, "defesa": 1, "cura_turno": 1},
          "Confortável: descansar entre os golpes ajuda a se recuperar."),
    _item("Cota de Malha", "🦺", "armadura", 2, 42, {"hp_max": 45, "defesa": 2, "espinhos": 1},
          "Anéis de metal trançados que machucam quem bate."),
    _item("Armadura de Placas", "🔰", "armadura", 2, 50, {"hp_max": 65, "defesa": 3},
          "Pesada e imponente. Aguenta muito mais castigo."),
    _item("Couraça de Espinhos", "🌵", "armadura", 2, 55, {"hp_max": 45, "defesa": 2, "espinhos": 2},
          "Quem ousa te atacar sai com as mãos sangrando."),
    _item("Manto Arcano", "🧙", "armadura", 2, 52, {"hp_max": 40, "defesa": 1, "mana_regen": 1, "cura_turno": 1},
          "Tecido encantado que revigora corpo e mana."),
    _item("Armadura de Mithril", "💎", "armadura", 3, 100, {"hp_max": 70, "defesa": 5},
          "Leve como seda e dura como diamante."),
    _item("Escamas de Dragão", "🐲", "armadura", 3, 105, {"hp_max": 75, "defesa": 3, "bloqueio_postura": 0.15, "espinhos": 1},
          "Couraça lendária: em postura defensiva quase nada passa."),

    # --------------------------- JOIAS (anéis e amuletos) ---------------------------
    _item("Anel de Ferro", "💍", "joia", 1, 18, {"defesa": 1, "hp_max": 10},
          "Um simples anel de ferro com um encantamento de proteção."),
    _item("Anel do Vigor", "💍", "joia", 1, 16, {"hp_max": 15},
          "Quem o usa se sente mais resistente."),
    _item("Anel do Lucro", "💍", "joia", 1, 22, {"ouro_turno": 2, "hp_max": 10},
          "Atrai moedas como um ímã: ouro extra a cada turno."),
    _item("Anel de Espinhos", "💍", "joia", 1, 24, {"espinhos": 3, "hp_max": 10},
          "Pequenos espinhos escondidos: quem te atacar se fere."),
    _item("Anel da Sorte", "💍", "joia", 2, 36, {"crit": 2, "dano": 1},
          "Os dados parecem rolar a seu favor: crítico bem mais fácil."),
    _item("Anel do Bruto", "💍", "joia", 2, 36, {"dano": 4},
          "Força bruta condensada em um aro de bronze."),
    _item("Anel Perfurante", "💍", "joia", 2, 40, {"penetracao": 0.50, "dano": 2},
          "Seus golpes encontram as frestas das armaduras."),
    _item("Anel Sanguessuga", "💍", "joia", 2, 42, {"vampirismo": 0.25, "hp_max": 10},
          "Parte do dano que você causa volta como vida."),
    _item("Anel Regenerador", "💍", "joia", 2, 40, {"cura_turno": 2},
          "As feridas se fecham sozinhas no início de cada turno."),
    _item("Anel da Fúria", "💍", "joia", 2, 38, {"dano": 3, "furia_extra": 1, "hp_max": 10},
          "Enfurece mais rápido quem o usa (ideal para Bárbaros)."),
    _item("Anel Arcano", "💍", "joia", 2, 36, {"mana_regen": 1, "penetracao": 0.25, "hp_max": 15},
          "Um poço de mana no dedo (ideal para Feiticeiros)."),
    _item("Anel do Mago", "💍", "joia", 2, 36, {"dano": 4},
          "Poder arcano condensado em um aro de prata.", magico=True),
    _item("Anel Venenoso", "💍", "joia", 3, 70, {"veneno": 4, "recarga": 3},
          "Uma agulha oculta: o ataque envenena o alvo (4 de dano por rodada durante 3 rodadas). "
          "Depois de envenenar, o anel recarrega por 3 rodadas (3 turnos seus)."),
    _item("Amuleto Arcano", "📿", "joia", 3, 80, {"dano": 6, "hp_max": 20},
          "Pulsa com magia pura: mais poder mágico e vitalidade.", magico=True),
    _item("Amuleto do Vampiro", "📿", "joia", 3, 85, {"vampirismo": 0.20, "hp_max": 40},
          "Relíquia sombria que transforma sangue alheio em vigor."),
    _item("Amuleto da Fortuna", "📿", "joia", 3, 75, {"ouro_turno": 3, "crit": 2, "hp_max": 20},
          "A sorte (e o ouro) sorriem para o portador."),

    # -------------------------- ATIVOS (usados no Inventário) --------------------------
    _item("Cálice Vital", "🏺", "ativo", 2, 45, {"cura": 20, "recarga": 4},
          "Um gole do cálice e as feridas se fecham. Recarrega com o tempo."),
    _item("Olho Protetor", "🧿", "ativo", 2, 50, {"escudo_pv": 20, "livre": True, "recarga": 2},
          "Cria um escudo que absorve dano até o seu próximo turno."),
    _item("Chifre de Guerra", "📯", "ativo", 2, 55, {"buff_dano": 2.0, "livre": True, "recarga": 3},
          "Um brado de guerra: o próximo ataque causa o DOBRO de dano."),
    _item("Luvas do Ladrão", "🧤", "ativo", 2, 35, {"roubo": 10, "livre": True, "recarga": 2},
          "Dedos ágeis: rouba moedas de um oponente sem nem parar de lutar."),
    _item("Capa da Invisibilidade", "👻", "ativo", 3, 75, {"invisibilidade": True, "buff_dano": 1.5, "livre": True, "recarga": 3},
          "Ninguém pode te escolher como alvo até o seu próximo turno, e a emboscada causa +50% no próximo ataque."),
    _item("Cajado Relâmpago", "⚡", "ativo", 3, 75, {"raio": 16, "recarga": 3},
          "Um raio que ignora Defesa e postura. Atinge um oponente que não esteja protegido."),
]


# Poção simples que o Comerciante SEMPRE oferece (fora do sorteio e de qualquer fase)
POCAO_FIXA = _item("Poção Simples", "🩹", "consumivel", 1, 10, {"cura": 15},
                   "Sempre à venda: um gole rápido para fechar arranhões.", usos=1)
POCAO_REFORCADA = _item("Poção Reforçada", "🧴", "consumivel", 2, 20, {"cura": 30},
                        "Sempre à venda a partir da rodada 20: uma dose caprichada.", usos=1)
RODADA_POCAO_REFORCADA = 20  # a partir desta visita do Comerciante, a poção fixa vira a Reforçada


def pocao_fixa(rodada):
    """Poção que o Comerciante sempre oferece nesta rodada."""
    return POCAO_REFORCADA if rodada >= RODADA_POCAO_REFORCADA else POCAO_FIXA


def num(x):
    """Arredonda para 1 casa decimal; devolve int quando o valor é inteiro."""
    x = round(x, 1)
    return int(x) if x == int(x) else x


# ----------------------------------------------------------------------
# Estoque
# ----------------------------------------------------------------------
def sortear_estoque(rodada=5, tamanho=ITENS_POR_JOGADOR):
    """Sorteia o estoque de UM jogador numa visita: só itens da fase da rodada (ver FASES_POR_RODADA),
    sem repetir item dentro do mesmo estoque. Cada jogador recebe o seu próprio sorteio, então os
    estoques podem ser diferentes (e repetir itens entre jogadores).
    Os tipos 'consumível, arma, armadura, joia e ativo' aparecem pelo menos uma vez quando a fase tem itens deles
    e o estoque comporta. Cada item é uma cópia com a flag `disponivel`."""
    fase = fase_da_rodada(rodada)
    pool = [i for i in CATALOGO if i["tier"] == fase]
    tamanho = min(len(pool), tamanho)
    escolhidos = []
    categorias = list(CATEGORIAS_GARANTIDAS)
    random.shuffle(categorias)  # se o estoque for pequeno, nem sempre as mesmas categorias entram
    for tipo in categorias:
        if len(escolhidos) >= tamanho:
            break
        candidatos = [i for i in pool if i["tipo"] == tipo]
        if candidatos:
            item = random.choice(candidatos)
            escolhidos.append(item)
            pool.remove(item)
    while len(escolhidos) < tamanho:
        item = random.choice(pool)
        escolhidos.append(item)
        pool.remove(item)
    random.shuffle(escolhidos)
    escolhidos.append(pocao_fixa(rodada))  # sempre à venda, além dos itens sorteados
    return [dict(i, efeitos=dict(i["efeitos"]), disponivel=True) for i in escolhidos]


# ----------------------------------------------------------------------
# Descrição dos efeitos
# ----------------------------------------------------------------------
def descrever_efeitos(efeitos, magico=False, usos=1):
    """Converte um dicionário de efeitos em linhas de texto legíveis (magico: False físico, True mágico ou DANO_HIBRIDO;
    usos > 1 indica um pacote de consumíveis)."""
    e = efeitos
    pct = lambda x: round(x * 100)
    linhas = []
    if usos > 1:
        linhas.append(f"📦 Pacote com {usos} usos")
    if "cura" in e:
        linhas.append(f"💚 Cura {num(e['cura'])} de vida")
    if "cura_rende" in e:
        linhas.append(f"⚠️ Para o seu personagem esta cura rende só {e['cura_rende']}%")
    if e.get("antidoto"):
        linhas.append("🌿 Remove veneno")
    if "dano" in e:
        metade = " (metade físico, metade mágico)" if magico == DANO_HIBRIDO else ""
        linhas.append(f"{icone_dano(magico)} +{num(e['dano'])} de Dano{metade}")
    if "dano_rende" in e:
        linhas.append(f"⚠️ Para o seu personagem este dano rende só {e['dano_rende']}%")
    if "mira_penalidade" in e:
        linhas.append(f"⚠️ Arma {ALCANCES[e['alcance_arma']]}: para você, −{e['mira_penalidade']} no D10 de ataque")
    if "defesa" in e:
        linhas.append(f"🔰 +{num(e['defesa'])} de Defesa")
    if "hp_max" in e:
        linhas.append(f"💖 +{num(e['hp_max'])} de Vida máxima")
    if "crit" in e:
        linhas.append(f"🎯 +{e['crit']} na faixa de crítico")
    if "penetracao" in e:
        linhas.append(f"⚡ Ignora {pct(e['penetracao'])}% da Defesa do alvo")
    if "vampirismo" in e:
        linhas.append(f"🩸 Cura {pct(e['vampirismo'])}% do dano causado")
    if "veneno" in e:
        linhas.append(f"🐍 Ataques envenenam ({e['veneno']}/rodada por {VENENO_RODADAS} rodadas)")
    if "espinhos" in e:
        linhas.append(f"🌵 Reflete {e['espinhos']} de dano em quem te atacar")
    if "bloqueio_postura" in e:
        linhas.append(f"🔰 +{pct(e['bloqueio_postura'])}% de bloqueio na postura")
    if "ouro_turno" in e:
        linhas.append(f"🪙 +{e['ouro_turno']} moedas por turno")
    if "ouro_ataque" in e:
        linhas.append(f"🪙 +{e['ouro_ataque']} moedas por ataque")
    if "cura_turno" in e:
        linhas.append(f"🌿 Regenera {e['cura_turno']} de vida por turno")
    if "furia_extra" in e:
        linhas.append(f"🔥 Fúria enche +{e['furia_extra']} a mais (Bárbaro)")
    if "mana_regen" in e:
        linhas.append(f"🔮 +{e['mana_regen']} de mana por rodada (Feiticeiro)")
    if "buff_dano" in e:
        linhas.append(f"💪 Próximo ataque causa ×{e['buff_dano']:g} de dano")
    if "buff_rolagem" in e:
        linhas.append(f"🍀 +{e['buff_rolagem']} na rolagem do próximo ataque")
    if "veneno_arma" in e:
        linhas.append(f"🐍 Próximo ataque envenena ({e['veneno_arma']}/rodada por {VENENO_RODADAS} rodadas)")
    if "defesa_temp" in e:
        linhas.append(f"🧱 +{e['defesa_temp']} de Defesa por {DEFESA_TEMP_RODADAS} rodadas")
    if "bomba" in e:
        linhas.append(f"💣 {e['bomba']} de dano fixo (ignora Defesa e postura)")
    if "raio" in e:
        linhas.append(f"⚡ Raio de {e['raio']} de dano fixo (ignora Defesa e postura)")
    if "roubo" in e:
        linhas.append(f"🧤 Rouba até {e['roubo']} moedas de um oponente")
    if e.get("invisibilidade"):
        linhas.append("👻 Invisível até o seu próximo turno (ninguém pode te escolher)")
    if "escudo_pv" in e:
        linhas.append(f"🧿 Escudo de {e['escudo_pv']} de dano até o seu próximo turno")
    if e.get("livre"):
        linhas.append("🆓 Ação livre (não gasta o turno)")
    if "recarga" in e:
        linhas.append(f"⏳ Recarga de {e['recarga']} rodadas")
    return linhas


# ----------------------------------------------------------------------
# Status e bônus dos itens equipados
# ----------------------------------------------------------------------
def multiplicador_item(jogador, item):
    """Eficiência de um item de combate físico para este jogador (Ferreiro e níveis de forja)."""
    if item["tipo"] not in EQUIPAVEIS:
        return 1.0
    return jogador.get("mult_equip", 1.0) * (1 + BONUS_FORJA * item.get("forja", 0))


def efeitos_efetivos(jogador, item):
    """Efeitos do item já considerando os bônus do jogador (Ferreiro e A Forja).
    A Forja multiplica os valores (BONUS_FORJA por nível) e ainda soma pontos inteiros (FORJA_FIXO por nível)."""
    mult = multiplicador_item(jogador, item)
    nivel = item.get("forja", 0) if item["tipo"] in EQUIPAVEIS else 0
    fixo = FORJA_FIXO.get(item["tipo"], {})
    efeitos = {}
    for chave, valor in item["efeitos"].items():
        if chave not in ESCALAVEIS or (mult == 1.0 and not nivel):
            efeitos[chave] = valor
            continue
        novo = valor * mult + fixo.get(chave, 0) * nivel
        efeitos[chave] = round(novo) if chave == "hp_max" else num(novo)
    for chave, extra in fixo.items():  # atributo que o item ainda não tinha (ex.: armadura sem Defesa)
        if nivel and chave not in efeitos:
            efeitos[chave] = extra * nivel
    if "dano" in efeitos and "raca" in jogador:
        rende = rendimento_dano(jogador, item.get("magico", False))
        if rende < 1:
            efeitos["dano_rende"] = round(rende * 100)
    if item["tipo"] == "arma" and fora_do_alcance(jogador, item):
        efeitos["mira_penalidade"] = PENALIDADE_MIRA
        efeitos["alcance_arma"] = item["alcance"]
    if item["tipo"] == "consumivel" and "cura" in efeitos and jogador.get("mult_cura_consumivel", 1.0) < 1:
        efeitos["cura_rende"] = round(jogador["mult_cura_consumivel"] * 100)
    return efeitos


def fora_do_alcance(jogador, item):
    """A arma é de alcance diferente do personagem? (híbridos e armas sem alcance definido nunca são)"""
    alcance = jogador.get("alcance")
    return bool(item.get("alcance")) and alcance in ("melee", "ranged") and item["alcance"] != alcance


def fator_afinidade(jogador, parte):
    """Quanto rende o dano de item de um tipo ('fisico' ou 'magico') para o personagem do jogador.
    Personagens híbridos aproveitam tudo; os outros perdem PENALIDADE_AFINIDADE no tipo que não é o deles."""
    afinidade = jogador.get("afinidade", "fisico")
    if afinidade == "hibrido" or parte == afinidade:
        return 1.0
    return PENALIDADE_AFINIDADE


def rendimento_dano(jogador, magico):
    """Fração do dano de um item que vale para o jogador (híbrido: metade de cada tipo)."""
    if magico == DANO_HIBRIDO:
        return (fator_afinidade(jogador, "fisico") + fator_afinidade(jogador, "magico")) / 2
    return fator_afinidade(jogador, "magico" if magico else "fisico")


def texto_forja_fixo(tipo):
    """Pontos inteiros que 1 nível de Forja dá para o tipo de item (ex.: '+1 de Dano')."""
    rotulos = {"dano": "de Dano", "defesa": "de Defesa", "hp_max": "de Vida máxima"}
    return " e ".join(f"+{v} {rotulos[k]}" for k, v in FORJA_FIXO.get(tipo, {}).items())


def recalcular_status(jogador):
    """Recalcula dano físico, dano mágico, defesa, vida máxima e bônus passivos (valores base + itens equipados)."""
    fisico = jogador["dano_fisico_base"]
    magico = jogador["dano_magico_base"]
    defesa = jogador["defesa_base"]
    hp_max = jogador["hp_base"]
    bonus = {}
    for item in jogador["itens"]:
        if item["tipo"] not in SLOTADOS:
            continue
        efeitos = efeitos_efetivos(jogador, item)
        d_fis, d_mag = partes_do_dano(efeitos.get("dano", 0), item.get("magico", False))
        fisico += d_fis * fator_afinidade(jogador, "fisico")
        magico += d_mag * fator_afinidade(jogador, "magico")
        defesa += efeitos.get("defesa", 0)
        hp_max += efeitos.get("hp_max", 0)
        for chave in SOMADOS:
            if chave in item["efeitos"]:
                bonus[chave] = bonus.get(chave, 0) + item["efeitos"][chave]
    if jogador.get("vampirismo_base"):  # Hemomante: vampirismo do personagem (soma com os itens, dentro do teto)
        bonus["vampirismo"] = bonus.get("vampirismo", 0) + jogador["vampirismo_base"]
    jogador["penalidade_mira"] = PENALIDADE_MIRA if any(
        i["tipo"] == "arma" and fora_do_alcance(jogador, i) for i in jogador["itens"]) else 0
    for chave, teto in TETOS_BONUS.items():
        if chave in bonus:
            bonus[chave] = min(bonus[chave], teto)
    jogador["bonus"] = bonus
    jogador["dano_fisico"] = num(fisico)
    jogador["dano_magico"] = num(magico)
    jogador["dano"] = num(fisico + magico)  # poder de ataque total (físico + mágico)
    jogador["defesa"] = num(defesa)
    novo_max = round(hp_max)
    jogador["hp_max"] = novo_max  # vida máxima extra NÃO cura: a vida atual só é cortada se passar do novo máximo
    jogador["hp"] = min(jogador["hp"], novo_max)


# ----------------------------------------------------------------------
# Espaços de equipamento (build) e ordem de compra
# ----------------------------------------------------------------------
def itens_do_slot(jogador, tipo):
    return [i for i in jogador["itens"] if i["tipo"] == tipo]


def limite_slot(jogador, tipo):
    """Quantos itens daquele tipo o jogador pode ter equipados (o Alquimista só tem 1 espaço de arma)."""
    return jogador.get("limite_slots", {}).get(tipo, LIMITE_SLOTS.get(tipo))


def slot_cheio(jogador, tipo):
    limite = limite_slot(jogador, tipo)
    return limite is not None and len(itens_do_slot(jogador, tipo)) >= limite


def pior_item_do_slot(jogador, tipo):
    """Item equipado de menor valor naquele espaço (útil para decidir o que substituir)."""
    itens = itens_do_slot(jogador, tipo)
    return min(itens, key=lambda i: i.get("valor", 0) + 5 * i.get("forja", 0)) if itens else None


def categoria_compra(item):
    """Categoria do item para o limite de compras por visita: 'consumivel' ou 'equipamento' (arma, armadura, joia, ativo)."""
    return "consumivel" if item["tipo"] == "consumivel" else "equipamento"


def limite_compras(jogador, categoria):
    """Compras da categoria por visita para este jogador (o Alquimista compra 1 consumível a mais)."""
    return LIMITE_COMPRAS[categoria] + jogador.get("compras_extra", {}).get(categoria, 0)


def compras_restantes(jogador, categoria):
    """Quantas compras da categoria o jogador ainda pode fazer nesta visita do Comerciante."""
    return limite_compras(jogador, categoria) - jogador["compras_visita"].get(categoria, 0)


def compras_esgotadas(jogador):
    return all(compras_restantes(jogador, c) <= 0 for c in LIMITE_COMPRAS)


def texto_limite_compras():
    """Ex.: '1 equipamento e 1 consumível'."""
    return " e ".join(f"{n} {ROTULO_CATEGORIA[c]}" for c, n in LIMITE_COMPRAS.items())


def ativo_repetido(jogador, item):
    """Itens ativos não podem se repetir: o jogador já tem um ativo igual a este?"""
    nome = f"{item['emoji']} {item['nome']}"
    return item["tipo"] == "ativo" and any(i["tipo"] == "ativo" and i["nome"] == nome for i in jogador["itens"])


def bloqueio_compra(jogador, item):
    """Motivo que impede a compra do item agora (sem contar o ouro), ou None se pode comprar."""
    if not item["disponivel"]:
        return "❌ Esse item já foi vendido!"
    categoria = categoria_compra(item)
    if compras_restantes(jogador, categoria) <= 0:
        n = limite_compras(jogador, categoria)
        rotulo = ROTULO_CATEGORIA_PLURAL[categoria] if n > 1 else ROTULO_CATEGORIA[categoria]
        return f"❌ Você já comprou {n} {rotulo} nesta visita."
    if ativo_repetido(jogador, item):
        return "❌ Você já tem esse item ativo: itens ativos não podem se repetir."
    return None


def ordem_compras(jogadores):
    """Ordem no Comerciante: sorteada a cada visita (antes: do menos equipado ao mais equipado).
    Cada jogador tem um estoque próprio, então a ordem não muda o que cada um pode comprar."""
    ordem = [j for j in jogadores if j["vivo"]]
    random.shuffle(ordem)
    return ordem


# ----------------------------------------------------------------------
# Compra e Forja
# ----------------------------------------------------------------------
def comprar(jogador, item, substituir=None):
    """Tenta comprar. Devolve (sucesso, mensagem). O item comprado some do estoque de quem comprou.

    Se o espaço do tipo estiver cheio, `substituir` deve ser o item equipado que será descartado."""
    bloqueio = bloqueio_compra(jogador, item)
    if bloqueio:
        return False, bloqueio
    if jogador["ouro"] < item["preco"]:
        faltam = item["preco"] - jogador["ouro"]
        return False, f"❌ Moedas insuficientes (faltam {faltam})."
    if slot_cheio(jogador, item["tipo"]):
        if substituir is None or substituir not in jogador["itens"] or substituir["tipo"] != item["tipo"]:
            return False, f"❌ Seu espaço de {ROTULO_SLOT[item['tipo']]} está cheio: escolha um item para substituir."

    preco = item["preco"]
    extra = ""
    # Goblin: Pechinchar (só rola quando a compra é possível pelo preço cheio) e sempre informa o resultado
    if jogador["raca"] == "Goblin":
        if not jogador["pechinchar_pronto"]:
            extra = " 🪙 Pechinchar desabilitado: nenhum desconto aplicado."
        elif random.random() < CHANCE_PECHINCHA:
            preco = int(item["preco"] * (1 - DESCONTO_PECHINCHA) + 0.5)
            jogador["pechinchar_pronto"] = False
            extra = (f" 🪙 Pechinchar funcionou! Desconto de {round(DESCONTO_PECHINCHA * 100)}%: "
                     f"pagou {preco} em vez de {item['preco']}.")
        else:
            extra = " 🪙 Pechinchar: o desconto NÃO foi aplicado desta vez."

    jogador["ouro"] -= preco
    item["disponivel"] = False
    categoria = categoria_compra(item)
    jogador["compras_visita"][categoria] = jogador["compras_visita"].get(categoria, 0) + 1
    nome = f"{item['emoji']} {item['nome']}"
    if substituir is not None:
        jogador["itens"].remove(substituir)
        extra = f" 🔁 Substituiu {substituir['nome']}." + extra
    jogador["itens"].append(
        {
            "nome": nome,
            "tipo": item["tipo"],
            "efeitos": dict(item["efeitos"]),
            "forja": 0,
            "valor": item["preco"],
            "magico": item.get("magico", False),
            "recarga_atual": 0,
            "usos": item.get("usos", 1) + (jogador.get("usos_extra_consumivel", 0) if item["tipo"] == "consumivel" else 0),
            "alcance": item.get("alcance"),
        }
    )

    if item["tipo"] == "consumivel":
        return True, f"✅ {nome} comprado! Está no seu inventário.{extra}"
    recalcular_status(jogador)
    return True, f"✅ {nome} comprado e equipado!{extra}"


def forjar(jogador, item):
    """Ferreiro: A Forja. Melhora 1 item de combate físico em +BONUS_FORJA (1 uso por visita, até MAX_FORJA por item)."""
    if jogador["raca"] != "Ferreiro":
        return False, "❌ Só o Ferreiro pode usar A Forja."
    if jogador["forja_usada"]:
        return False, "❌ A Forja já foi usada nesta visita do Comerciante!"
    if item["tipo"] not in EQUIPAVEIS:
        return False, "❌ A Forja só melhora armas e armaduras."
    if item.get("forja", 0) >= MAX_FORJA:
        return False, f"❌ Esse item já está no nível máximo da Forja ({MAX_FORJA})."
    item["forja"] = item.get("forja", 0) + 1
    jogador["forja_usada"] = True
    recalcular_status(jogador)
    efeitos = ", ".join(descrever_efeitos(efeitos_efetivos(jogador, item), item.get("magico", False)))
    return True, f"🔨 A Forja melhorou {item['nome']}! Nível {item['forja']}/{MAX_FORJA} (+{int(item['forja'] * BONUS_FORJA * 100)}%): {efeitos}."


# ----------------------------------------------------------------------
# Uso de itens (consumíveis e ativos)
# ----------------------------------------------------------------------
ACOES_COM_ALVO = ("bomba", "raio", "roubo")  # precisam de um alvo escolhido pela interface


def exige_alvo(item):
    return any(chave in item["efeitos"] for chave in ACOES_COM_ALVO)


def _efeitos_uteis(jogador, e):
    """Efeitos do item que ainda fariam diferença agora (o que já está ativo não conta)."""
    uteis = []
    if "cura" in e and jogador["hp"] < jogador["hp_max"]:
        uteis.append("cura")
    if e.get("antidoto") and jogador["veneno"]:
        uteis.append("antidoto")
    if "buff_dano" in e and jogador["buff_dano"] < e["buff_dano"]:  # bônus de dano não acumulam: vale o maior
        uteis.append("buff_dano")
    if "buff_rolagem" in e and jogador["buff_rolagem"] <= 0:
        uteis.append("buff_rolagem")
    if "veneno_arma" in e and jogador["arma_envenenada"] <= 0:
        uteis.append("veneno_arma")
    if "defesa_temp" in e and jogador["defesa_temp"] <= 0:
        uteis.append("defesa_temp")
    if e.get("invisibilidade") and not jogador["invisivel"]:
        uteis.append("invisibilidade")
    if "escudo_pv" in e and jogador["escudo_pv"] <= 0:
        uteis.append("escudo_pv")
    return uteis


def pode_usar(jogador, item):
    """Confere se o item pode ser usado agora. Devolve (ok, mensagem de erro com prefixo de 2 caracteres)."""
    e = item["efeitos"]
    if item["tipo"] not in ("consumivel", "ativo"):
        return False, "❌ Esse item é um equipamento: o bônus já está valendo."
    if item["tipo"] == "ativo" and item.get("recarga_atual", 0) > 0:
        return False, f"❌ {item['nome']} em recarga ({item['recarga_atual']} rodada(s))."
    if e.get("livre") and jogador["livre_usado"]:
        return False, "❌ Você já usou um item de ação livre neste turno."
    if exige_alvo(item):
        return True, ""
    if not _efeitos_uteis(jogador, e):
        return False, "❌ Esse item não teria efeito agora (já está ativo, vida cheia ou sem veneno)."
    return True, ""


def gastar_item(jogador, item):
    """Consome um uso do item (consumível some no último uso; ativo entra em recarga) e marca a ação livre."""
    if item["tipo"] == "consumivel":
        item["usos"] = item.get("usos", 1) - 1
        if item["usos"] <= 0:
            jogador["itens"].remove(item)
    else:
        item["recarga_atual"] = item["efeitos"].get("recarga", 0)
    if item["efeitos"].get("livre"):
        jogador["livre_usado"] = True


def usar_item(jogador, item):
    """Usa um item que não precisa de alvo. Devolve (sucesso, mensagem)."""
    ok, msg = pode_usar(jogador, item)
    if not ok:
        return False, msg
    e = item["efeitos"]
    uteis = _efeitos_uteis(jogador, e)
    partes = []
    if "cura" in uteis:
        valor = e["cura"] * (jogador.get("mult_cura_consumivel", 1.0) if item["tipo"] == "consumivel" else 1.0)
        cura = aplicar_cura(jogador, valor, "poções e itens")
        partes.append(f"💚 +{cura} de vida ({jogador['hp']}/{jogador['hp_max']})")
    if "antidoto" in uteis:
        jogador["veneno"] = None
        partes.append("🌿 veneno removido")
    if "buff_dano" in uteis:
        jogador["buff_dano"] = e["buff_dano"]
        partes.append(f"💪 próximo ataque ×{e['buff_dano']:g} de dano")
    if "buff_rolagem" in uteis:
        jogador["buff_rolagem"] = e["buff_rolagem"]
        partes.append(f"🍀 +{e['buff_rolagem']} na rolagem do próximo ataque")
    if "veneno_arma" in uteis:
        jogador["arma_envenenada"] = e["veneno_arma"]
        partes.append(f"🐍 arma envenenada ({e['veneno_arma']}/rodada)")
    if "defesa_temp" in uteis:
        jogador["defesa_temp"] = e["defesa_temp"]
        jogador["defesa_temp_rodadas"] = DEFESA_TEMP_RODADAS
        partes.append(f"🧱 +{e['defesa_temp']} de Defesa por {DEFESA_TEMP_RODADAS} rodadas")
    if "invisibilidade" in uteis:
        jogador["invisivel"] = True
        partes.append("👻 invisível até o seu próximo turno")
    if "escudo_pv" in uteis:
        jogador["escudo_pv"] = e["escudo_pv"]
        partes.append(f"🧿 escudo de {e['escudo_pv']} até o seu próximo turno")
    gastar_item(jogador, item)
    return True, f"✅ {item['nome']} usado! " + " • ".join(partes)


# Morte súbita: a partir de certa rodada todas as curas rendem menos (o main.py ajusta este fator a cada rodada)
fator_cura_global = 1.0


def aplicar_cura(jogador, valor, fonte=""):
    """Cura o jogador (respeitando a vida máxima e a morte súbita). Devolve quanto curou de fato.
    `fonte` só identifica a origem da cura (útil para estatísticas)."""
    cura = max(0, min(round(valor * fator_cura_global), jogador["hp_max"] - jogador["hp"]))
    jogador["hp"] += cura
    return cura


# ----------------------------------------------------------------------
# Alquimista: Mistura
# ----------------------------------------------------------------------
def misturaveis(jogador):
    """Consumíveis que podem entrar numa Mistura (os que precisam de alvo, como bombas, ficam de fora)."""
    return [i for i in jogador["itens"] if i["tipo"] == "consumivel" and not exige_alvo(i)]


def misturar(jogador, item_a, item_b):
    """Alquimista: junta 2 consumíveis num só, com os efeitos dos dois (1 vez por visita do Comerciante).
    Gasta 1 uso de cada um. Curas, rolagem, Defesa e veneno se somam; bônus de dano vale o maior."""
    if jogador["raca"] != "Alquimista":
        return False, "❌ Só o Alquimista pode fazer Misturas."
    if jogador.get("mistura_usada"):
        return False, "❌ A Mistura já foi usada nesta visita do Comerciante."
    if item_a not in misturaveis(jogador) or item_b not in misturaveis(jogador):
        return False, "❌ Escolha 2 consumíveis (bombas não entram na Mistura)."
    if item_a is item_b and item_a.get("usos", 1) < 2:
        return False, "❌ Para misturar um consumível com ele mesmo, ele precisa ter 2 usos."
    efeitos = {}
    for origem in (item_a["efeitos"], item_b["efeitos"]):
        for chave, valor in origem.items():
            if chave == "livre":
                continue
            if chave == "antidoto":
                efeitos["antidoto"] = True
            elif chave == "buff_dano":
                efeitos["buff_dano"] = max(efeitos.get("buff_dano", 1.0), valor)
            else:
                efeitos[chave] = efeitos.get(chave, 0) + valor
    if item_a["efeitos"].get("livre") and item_b["efeitos"].get("livre"):
        efeitos["livre"] = True  # só não gasta o turno se os dois ingredientes também não gastavam
    nome = f"⚗️ Mistura ({item_a['nome']} + {item_b['nome']})"
    for ingrediente in (item_a, item_b):
        ingrediente["usos"] = ingrediente.get("usos", 1) - 1
        if ingrediente["usos"] <= 0:
            jogador["itens"].remove(ingrediente)
    jogador["itens"].append({"nome": nome, "tipo": "consumivel", "efeitos": efeitos, "forja": 0,
                             "valor": item_a.get("valor", 0) + item_b.get("valor", 0), "magico": False,
                             "recarga_atual": 0, "usos": 1, "alcance": None})
    jogador["mistura_usada"] = True
    return True, f"⚗️ Mistura pronta: {nome}! " + ", ".join(descrever_efeitos(efeitos))


def aplicar_veneno(alvo, dano):
    """Envenena o alvo (refresca a duração; mantém o maior dano por rodada)."""
    atual = alvo["veneno"]["dano"] if alvo["veneno"] else 0
    alvo["veneno"] = {"dano": max(atual, dano), "rodadas": VENENO_RODADAS}


def avancar_recargas(jogador):
    """Fim de rodada: itens ativos em recarga ficam mais perto de ficar prontos."""
    for item in jogador["itens"]:
        if item.get("recarga_atual", 0) > 0:
            item["recarga_atual"] -= 1