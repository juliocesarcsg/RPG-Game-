"""RPG de Terminal - Etapa 6: itens por fase (early/mid/late por rodada), joias, itens ativos, poções e veneno.

Dependência externa: rich  ->  pip install rich
"""

import random
import time

import dice
import shop
from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

MIN_JOGADORES = 2
MAX_JOGADORES = 6
OURO_POR_TURNO = 5  # moedas ganhas no início de cada turno
INTERVALO_LOJA = 5  # o Comerciante chega ao fim de cada N rodadas completas
OURO_LOJA = 10  # moedas que cada jogador vivo recebe quando o Comerciante chega
OURO_GOBLIN = 5  # ouro extra do Goblin a cada rodada
MAX_PIPS = 3  # barras de Fúria e Mana (3/3)
FURIA_MULT = 1.5  # dano do ataque enfurecido
ESCUDO_MANA = 0.40  # fração do dano mitigada pelo Escudo de Mana
PENETRACAO_MAGICA = 0.50  # fração da Defesa do alvo ignorada pela parte mágica do dano (de qualquer raça)
MANA_REGEN = 1  # mana restaurada no fim de toda rodada
MANA_REGEN_EXTRA = 1  # mana extra se o Feiticeiro não gastou mana na rodada
REFLEXO_POSTURA = 0.75  # fração do dano bloqueado pela postura que volta ao atacante
POSTURA_FERREIRO = 0.10  # bloqueio extra do Ferreiro em postura defensiva
OURO_POSTURA_GOBLIN = 5  # ouro que o Goblin ganha ao assumir a postura

# Cores de cada jogador (por ordem de entrada)
CORES_JOGADORES = ["red", "cyan", "green", "yellow", "magenta", "bright_blue"]

# Valores máximos usados só para desenhar as barras de atributos
MAXIMOS = {"hp": 150, "dano": 10, "defesa": 10}

RACAS = {
    "Bárbaro": {
        "emoji": "🪓",
        "cor": "red",
        "descricao": "Guerreiro selvagem. Cada golpe alimenta sua fúria.",
        "hp": 120,
        "dano_fisico": 3,
        "dano_magico": 0,
        "defesa": 0,
        "passivo": "Fúria: barra 3/3. Cada ataque enche 1/3. Cheia, o próximo ataque causa +50% de dano, "
                   "zera a barra e a desabilita por 1 rodada.",
        "habilidade": None,
        "postura": "Postura: enche +1/3 de Fúria.",
        "itens": [{"nome": "🔪 Espada Curta", "tipo": "arma", "efeitos": {"dano": 3}}],
    },
    "Goblin": {
        "emoji": "👺",
        "cor": "green",
        "descricao": "Pequeno, esperto e ganancioso. Vive de ouro e pechinchas.",
        "hp": 115,
        "dano_fisico": 3,
        "dano_magico": 0,
        "defesa": 0,
        "passivo": f"Ganancioso: recebe +{OURO_GOBLIN} de ouro a mais a cada rodada (e a cada visita do Comerciante).",
        "habilidade": f"Pechinchar: ao comprar do Comerciante, {round(shop.CHANCE_PECHINCHA * 100)}% de chance de "
                      f"{round(shop.DESCONTO_PECHINCHA * 100)}% de desconto. "
                      "Depois do desconto, fica desabilitada até a próxima visita.",
        "postura": f"Postura: ganha +{OURO_POSTURA_GOBLIN} de ouro.",
        "itens": [{"nome": "🔪 Adaga cega", "tipo": "arma", "efeitos": {"dano": 3}}],
    },
    "Feiticeiro": {
        "emoji": "🔮",
        "cor": "magenta",
        "descricao": "Mestre da mana. Poderoso, mas precisa gerenciar sua energia.",
        "hp": 110,
        "dano_fisico": 0,
        "dano_magico": 4,
        "defesa": 0,
        "passivo": f"Mana: barra 3/3. Cada ataque custa 1/3. Ao fim de toda rodada restaura {MANA_REGEN}/3 "
                   f"(+{MANA_REGEN_EXTRA}/3 se não gastou mana). Seu dano é mágico: ignora "
                   f"{round(PENETRACAO_MAGICA * 100)}% da Defesa do alvo.",
        "habilidade": "Escudo de Mana: gasta 2/3 da mana e mitiga 40% do dano do próximo ataque recebido.",
        "postura": "Postura: recupera +1/3 de mana.",
        "itens": [{"nome": "📖 Livro velho", "tipo": "arma", "efeitos": {"dano": 3}, "magico": True}],
    },
    "Ferreiro": {
        "emoji": "🔨",
        "cor": "yellow",
        "descricao": "Artesão de guerra. Tira o máximo de armas e armaduras.",
        "hp": 110,
        "dano_fisico": 3,
        "dano_magico": 0,
        "defesa": 0,
        "passivo": f"Mestre do Metal: armas e armaduras são {round((shop.MESTRE_METAL - 1) * 100)}% mais eficientes nele.",
        "habilidade": f"A Forja: quando o Comerciante chega, melhora 1 item de combate físico em "
                      f"+{round(shop.BONUS_FORJA * 100)}% (1 uso por visita, até {shop.MAX_FORJA} níveis por item).",
        "postura": f"Postura: bloqueia +{round(POSTURA_FERREIRO * 100)}% a mais do dano.",
        "itens": [{"nome": "🔨 Martelo desgastado", "tipo": "arma", "efeitos": {"dano": 3}}],
    },
}

NOMES_RACAS = list(RACAS.keys())

# Rótulo e cor de cada tipo de item (inventário e Comerciante)
TIPOS_ITEM = {
    "equipado": ("Equipado", "bright_black"),
    "arma": ("Arma", "red"),
    "armadura": ("Armadura", "blue"),
    "joia": ("Joia", "magenta"),
    "ativo": ("Ativo", "cyan"),
    "consumivel": ("Consumível", "green"),
}

# Fase do jogo em que cada item costuma aparecer no Comerciante
TIERS = {1: ("Early", "green"), 2: ("Mid", "yellow"), 3: ("Late", "red")}


ROTULO_FISICO = "🔪 Dano Físico"
ROTULO_MAGICO = "🌠 Dano Mágico"


def criar_jogador(nome, raca, cor):
    """Monta o jogador com os atributos e itens iniciais da raça."""
    r = RACAS[raca]
    jogador = {
        "nome": nome,
        "raca": raca,
        "cor": cor,
        "hp": r["hp"],
        "hp_max": r["hp"],
        "hp_base": r["hp"],
        "dano": r["dano_fisico"] + r["dano_magico"],  # poder de ataque total (recalculado pelos itens)
        "dano_fisico": r["dano_fisico"],
        "dano_magico": r["dano_magico"],
        "dano_fisico_base": r["dano_fisico"],
        "dano_magico_base": r["dano_magico"],
        "defesa": r["defesa"],
        "defesa_base": r["defesa"],
        "ouro": 0,
        "itens": [
            {
                "nome": i["nome"],
                "tipo": i["tipo"],
                "efeitos": dict(i["efeitos"]),
                "forja": 0,
                "valor": 0,
                "magico": i.get("magico", False),
                "recarga_atual": 0,
            }
            for i in r["itens"]
        ],
        "bonus": {},  # bônus passivos dos itens equipados (preenchido por shop.recalcular_status)
        "mult_equip": shop.MESTRE_METAL if raca == "Ferreiro" else 1.0,  # Mestre do Metal
        "postura": False,
        "escudo_mana": False,
        "atacado_na_rodada": False,
        "furia": 0,
        "furia_bloqueio": 0,
        "furia_usada": False,
        "mana": MAX_PIPS,
        "mana_gasta": False,
        "pechinchar_pronto": True,
        "forja_usada": False,
        # estados criados por itens
        "invisivel": False,  # ninguém pode escolher como alvo até o próximo turno do dono
        "escudo_pv": 0,  # dano que o escudo ainda absorve
        "veneno": None,  # {"dano": por rodada, "rodadas": restantes}
        "buff_dano": 1.0,  # multiplicador do próximo ataque
        "buff_rolagem": 0,  # soma na rolagem do próximo ataque
        "arma_envenenada": 0,  # dano de veneno que o próximo ataque aplica
        "defesa_temp": 0,
        "defesa_temp_rodadas": 0,
        "livre_usado": False,  # já usou um item de ação livre neste turno?
        "vivo": True,
    }
    shop.recalcular_status(jogador)
    return jogador


def pips(atual, cor="white", total=MAX_PIPS):
    return f"[{cor}]{'▰' * atual}[/][bright_black]{'▱' * (total - atual)}[/] {atual}/{total}"


# ----------------------------------------------------------------------
# Utilidades de entrada
# ----------------------------------------------------------------------
def erro(mensagem):
    console.print(f"  [bold red]✖ {mensagem}[/]")


def ler_inteiro(mensagem, minimo, maximo):
    """Pede um número até receber um valor válido no intervalo."""
    while True:
        entrada = console.input(mensagem).strip()
        if entrada.isdigit() and minimo <= int(entrada) <= maximo:
            return int(entrada)
        erro(f"Entrada inválida. Digite um número de {minimo} a {maximo}.")


def ler_nome(numero, nomes_usados, cor):
    """Pede um nome não vazio e que não repita o de outro jogador."""
    while True:
        nome = console.input(f"[bold {cor}]📝 Nome do Jogador {numero}:[/] ").strip()
        if not nome:
            erro("O nome não pode ficar vazio.")
        elif len(nome) > 20:
            erro("O nome pode ter no máximo 20 caracteres.")
        elif nome.lower() in (n.lower() for n in nomes_usados):
            erro("Esse nome já está em uso. Escolha outro.")
        else:
            return nome


# ----------------------------------------------------------------------
# Telas
# ----------------------------------------------------------------------
def tela_titulo():
    console.clear()
    titulo = Text("🔪 ARENA DE COMBATE  🔪", style="bold yellow", justify="center")
    subtitulo = Text("RPG PvP em turnos • Terminal", style="italic bright_black", justify="center")
    corpo = Text("\n").join([titulo, subtitulo])
    console.print(
        Panel(Align.center(corpo), box=box.DOUBLE, border_style="yellow", padding=(1, 6))
    )


def barra(valor, maximo, cor, tamanho=12):
    """Barra de atributo com trilho: a parte vazia aparece em cinza, então valor 0 também mostra a barra."""
    cheios = 0 if valor <= 0 else min(tamanho, max(1, round(valor / maximo * tamanho)))
    return f"[{cor}]{'█' * cheios}[/][bright_black]{'░' * (tamanho - cheios)}[/]"


def tabela_racas(nome_jogador, cor):
    tabela = Table(
        title=f"[bold {cor}]{nome_jogador}[/], escolha sua raça",
        box=box.ROUNDED,
        border_style=cor,
        header_style="bold white",
        show_lines=True,
    )
    tabela.add_column("#", justify="center", style="bold")
    tabela.add_column("Raça", style="bold")
    tabela.add_column("Resumo")
    for i, nome in enumerate(NOMES_RACAS, start=1):
        r = RACAS[nome]
        tabela.add_row(str(i), f"[{r['cor']}]{r['emoji']} {nome}[/]", r["descricao"])
    return tabela


def painel_detalhes(nome_raca):
    r = RACAS[nome_raca]
    ref = criar_jogador("", nome_raca, "")  # atributos finais já com os itens iniciais
    atributos = Table.grid(padding=(0, 2))
    atributos.add_column(style="bold")
    atributos.add_column()
    atributos.add_column(justify="right", style="bold")
    atributos.add_row("💖 Vida", barra(ref["hp_max"], MAXIMOS["hp"], "green"), str(ref["hp_max"]))
    atributos.add_row(ROTULO_FISICO, barra(ref["dano_fisico_base"], MAXIMOS["dano"], "red"), str(ref["dano_fisico_base"]))
    atributos.add_row(ROTULO_MAGICO, barra(ref["dano_magico_base"], MAXIMOS["dano"], "magenta"), str(ref["dano_magico_base"]))

    itens = "\n".join(
        f"  • {i['nome']}  [bright_black]({', '.join(shop.descrever_efeitos(shop.efeitos_efetivos(ref, i), i.get('magico', False)))})[/]"
        for i in ref["itens"]
    )

    corpo = Table.grid()
    corpo.add_column()
    corpo.add_row(f"[italic]{r['descricao']}[/]")
    corpo.add_row("")
    corpo.add_row("[bold underline]Atributos[/]")
    corpo.add_row(atributos)
    corpo.add_row(
        f"[bright_black]🌠 O dano mágico ignora {round(PENETRACAO_MAGICA * 100)}% da Defesa do alvo (para qualquer raça). "
        "Itens de dano físico ou mágico podem ser comprados por todos.[/]"
    )
    corpo.add_row("")
    corpo.add_row("[bold underline]Passiva[/]")
    corpo.add_row(f"  ✨ {r['passivo']}")
    if r["habilidade"]:
        corpo.add_row("")
        corpo.add_row("[bold underline]Habilidade[/]")
        corpo.add_row(f"  🌟 {r['habilidade']}")
    corpo.add_row("")
    corpo.add_row("[bold underline]Postura Defensiva[/]")
    corpo.add_row(f"  🔰 Bloqueia dano e reflete {round(REFLEXO_POSTURA * 100)}% do que bloqueou. {r['postura']}")
    corpo.add_row("")
    corpo.add_row("[bold underline]Item Inicial[/]")
    corpo.add_row(itens)

    return Panel(
        corpo,
        title=f"{r['emoji']} [bold {r['cor']}]{nome_raca.upper()}[/]",
        box=box.HEAVY,
        border_style=r["cor"],
        padding=(1, 3),
    )


def escolher_raca(nome_jogador, cor):
    """Loop: lista raças -> detalhes -> confirmar ou voltar."""
    while True:
        console.print()
        console.print(tabela_racas(nome_jogador, cor))
        escolha = ler_inteiro(f"[bold {cor}]👉 Escolha (1-{len(NOMES_RACAS)}):[/] ", 1, len(NOMES_RACAS))
        nome_raca = NOMES_RACAS[escolha - 1]

        console.print()
        console.print(painel_detalhes(nome_raca))
        console.print("  [bold green]1.[/] ✅ Confirmar     [bold red]2.[/] 🔙 Voltar")
        decisao = ler_inteiro("[bold]👉 Escolha (1-2):[/] ", 1, 2)
        if decisao == 1:
            return nome_raca


def configurar_jogadores():
    """Fase de configuração: devolve a lista de jogadores criados."""
    tela_titulo()
    console.print()
    quantidade = ler_inteiro(
        f"[bold yellow]👥 Quantos jogadores? ({MIN_JOGADORES}-{MAX_JOGADORES}):[/] ",
        MIN_JOGADORES,
        MAX_JOGADORES,
    )

    jogadores = []
    for numero in range(1, quantidade + 1):
        cor = CORES_JOGADORES[numero - 1]
        console.print()
        console.rule(f"[bold {cor}]Jogador {numero} de {quantidade}[/]", style=cor)
        nome = ler_nome(numero, [j["nome"] for j in jogadores], cor)
        raca = escolher_raca(nome, cor)
        jogadores.append(criar_jogador(nome, raca, cor))
        r = RACAS[raca]
        console.print(f"\n  [bold green]✔[/] [bold {cor}]{nome}[/] entrou como {r['emoji']} [{r['cor']}]{raca}[/]!")
    return jogadores


def tela_resumo(jogadores):
    console.print()
    tabela = Table(
        title="🏰 JOGADORES NA ARENA",
        box=box.DOUBLE_EDGE,
        border_style="yellow",
        header_style="bold white",
        show_lines=True,
    )
    tabela.add_column("#", justify="center")
    tabela.add_column("Jogador", style="bold")
    tabela.add_column("Raça")
    tabela.add_column("💖 HP", justify="center")
    tabela.add_column("🔪 Físico", justify="center")
    tabela.add_column("🌠 Mágico", justify="center")
    for i, j in enumerate(jogadores, start=1):
        r = RACAS[j["raca"]]
        tabela.add_row(
            str(i),
            f"[{j['cor']}]{j['nome']}[/]",
            f"[{r['cor']}]{r['emoji']} {j['raca']}[/]",
            str(j["hp_max"]),
            str(j["dano_fisico"]),
            str(j["dano_magico"]),
        )
    console.print(tabela)


# ----------------------------------------------------------------------
# Lógica do jogo
# ----------------------------------------------------------------------
def vivos(jogadores):
    return [j for j in jogadores if j["vivo"]]


def pausar(mensagem="Pressione Enter para continuar..."):
    console.input(f"\n[bright_black]⏎ {mensagem}[/]")


def sortear_ordem(jogadores, excluido_primeiro=None):
    """Sorteia a ordem da rodada. Quem foi 1º na rodada anterior não pode ser 1º de novo."""
    ordem = vivos(jogadores)
    random.shuffle(ordem)
    if excluido_primeiro is not None and len(ordem) > 1 and ordem[0] is excluido_primeiro:
        i = random.randrange(1, len(ordem))
        ordem[0], ordem[i] = ordem[i], ordem[0]
    return ordem


def painel_roleta(texto, cor="yellow"):
    return Align.center(
        Panel(
            Text(texto, justify="center", style=f"bold {cor}"),
            title="🎲 SORTEANDO QUEM COMEÇA 🎲",
            box=box.HEAVY,
            border_style="yellow",
            padding=(1, 10),
        )
    )


def animar_roleta(ordem):
    """Animação de roleta passando pelos nomes e desacelerando até o sorteado."""
    participantes = list(ordem)
    random.shuffle(participantes)
    atraso = 0.05
    with Live(console=console, refresh_per_second=30, transient=True) as live:
        for i in range(28):
            j = participantes[i % len(participantes)]
            live.update(painel_roleta(f"👉  {j['nome']}  👈", j["cor"]))
            time.sleep(atraso)
            atraso *= 1.09
    primeiro = ordem[0]
    console.print(painel_roleta(f"🏁  {primeiro['nome']} começa!  🏁", primeiro["cor"]))


def mostrar_ordem(ordem, rodada):
    texto = Text()
    for i, j in enumerate(ordem, start=1):
        if i > 1:
            texto.append("  ➜  ", style="bright_black")
        texto.append(f"{i}º ", style="bold white")
        texto.append(j["nome"], style=f"bold {j['cor']}")
    console.print()
    console.print(
        Panel(
            Align.center(texto),
            title=f"📋 ORDEM DA RODADA {rodada}",
            box=box.ROUNDED,
            border_style="yellow",
            padding=(1, 4),
        )
    )


def barra_hp(hp, hp_max, tamanho=12):
    proporcao = hp / hp_max if hp_max else 0
    cheios = round(proporcao * tamanho)
    if hp > 0:
        cheios = max(1, cheios)
    cor = "green" if proporcao > 0.5 else "yellow" if proporcao > 0.25 else "red"
    return f"[{cor}]{'█' * cheios}[/][bright_black]{'░' * (tamanho - cheios)}[/] {hp}/{hp_max}"


def linha_recurso(j):
    """Recurso/habilidade da raça para o cabeçalho do turno e do Comerciante."""
    raca = j["raca"]
    if raca == "Bárbaro":
        texto = f"🔥 Fúria {pips(j['furia'], 'red')}"
        if j["furia"] >= MAX_PIPS:
            texto += "  [bold red]ATIVA: o próximo ataque causa +50%![/]"
        elif j["furia_bloqueio"] > 0:
            texto += "  [bright_black](desabilitada nesta rodada)[/]"
        return texto
    if raca == "Feiticeiro":
        texto = f"🔮 Mana {pips(j['mana'], 'cyan')}"
        if j["escudo_mana"]:
            texto += "  [cyan]Escudo de Mana ativo[/]"
        return texto
    if raca == "Goblin":
        estado = "[green]pronto[/]" if j["pechinchar_pronto"] else "[bright_black]desabilitado[/]"
        return f"🪙 Pechinchar: {estado}"
    if raca == "Ferreiro":
        estado = "[bright_black]já usada nesta visita[/]" if j["forja_usada"] else "[green]disponível com o Comerciante[/]"
        return f"🔨 A Forja: {estado}"
    return ""


def linha_buffs(j):
    """Efeitos temporários criados por itens (para o cabeçalho do turno)."""
    partes = []
    if j["buff_dano"] > 1:
        partes.append(f"💪 ×{j['buff_dano']:g} no próximo ataque")
    if j["buff_rolagem"]:
        partes.append(f"🍀 +{j['buff_rolagem']} na rolagem")
    if j["arma_envenenada"]:
        partes.append(f"🐍 arma envenenada ({j['arma_envenenada']}/rod.)")
    if j["defesa_temp"]:
        partes.append(f"🧱 +{j['defesa_temp']} Defesa ({j['defesa_temp_rodadas']} rod.)")
    if j["escudo_pv"]:
        partes.append(f"🧿 escudo {j['escudo_pv']}")
    if j["invisivel"]:
        partes.append("👻 invisível")
    if j["veneno"]:
        partes.append(f"🐍 [red]envenenado {j['veneno']['dano']}/rod. ({j['veneno']['rodadas']} rod.)[/]")
    return "   ".join(partes)


def tabela_arena(jogadores, ativo):
    tabela = Table(
        title="🏰 STATUS DA ARENA",
        box=box.ROUNDED,
        border_style="bright_black",
        header_style="bold white",
    )
    tabela.add_column("Jogador", style="bold")
    tabela.add_column("Raça")
    tabela.add_column("💖 Vida")
    tabela.add_column("💰", justify="right")
    tabela.add_column("Status")
    for j in jogadores:
        r = RACAS[j["raca"]]
        marcador = "▶ " if j is ativo else "  "
        if not j["vivo"]:
            status = "[red]💀 Eliminado[/]"
        else:
            partes = []
            if j["atacado_na_rodada"]:
                partes.append("[red]💢 Já atacado nesta rodada[/]")
            if j["invisivel"]:
                partes.append("[bright_black]👻 Invisível[/]")
            if j["postura"]:
                partes.append("[blue]🔰 Postura defensiva[/]")
            if j["escudo_mana"]:
                partes.append("[cyan]🔮 Escudo de Mana[/]")
            if j["escudo_pv"]:
                partes.append(f"[cyan]🧿 Escudo {j['escudo_pv']}[/]")
            if j["veneno"]:
                partes.append(f"[green]🐍 Envenenado ({j['veneno']['dano']}/rod.)[/]")
            status = "\n".join(partes) or "[green]✔ Em pé[/]"
        nome = f"[{j['cor']}]{marcador}{j['nome']}[/]"
        if not j["vivo"]:
            nome = f"[bright_black strike]{marcador}{j['nome']}[/]"
        tabela.add_row(
            nome,
            f"[{r['cor']}]{r['emoji']} {j['raca']}[/]",
            barra_hp(j["hp"], j["hp_max"]),
            f"[yellow]{j['ouro']}[/]",
            status,
        )
    return tabela


def tela_turno(rodada, jogador, jogadores, aviso=None):
    console.clear()
    r = RACAS[jogador["raca"]]
    faltam = INTERVALO_LOJA - ((rodada - 1) % INTERVALO_LOJA)  # rodadas até o Comerciante, contando esta
    rodada_loja = rodada + faltam - 1
    fase_loja_nome = TIERS[shop.fase_da_rodada(rodada_loja)][0]
    if faltam == 1:
        info_loja = f"🧳 [bold yellow]O Comerciante chega ao fim desta rodada![/] [bright_black](itens {fase_loja_nome})[/]"
    else:
        info_loja = (
            f"🧳 O Comerciante chega ao fim da rodada {rodada_loja} "
            f"[bright_black](em {faltam} • itens {fase_loja_nome})[/]"
        )
    defesa_txt = f"🔰 Defesa {jogador['defesa']}"
    if jogador["defesa_temp"]:
        defesa_txt += f" [bright_black](+{jogador['defesa_temp']} temp.)[/]"
    cabecalho = Table.grid(padding=(0, 3))
    cabecalho.add_column()
    cabecalho.add_column()
    cabecalho.add_row(
        f"{r['emoji']} [bold {r['cor']}]{jogador['raca']}[/]",
        f"💖 {barra_hp(jogador['hp'], jogador['hp_max'])}",
    )
    cabecalho.add_row(
        f"💰 [bold yellow]{jogador['ouro']} moedas[/]",
        f"🔪 Físico {jogador['dano_fisico']}   🌠 Mágico {jogador['dano_magico']}   {defesa_txt}",
    )
    cabecalho.add_row(linha_recurso(jogador), "")
    buffs = linha_buffs(jogador)
    if buffs:
        cabecalho.add_row(buffs, "")
    cabecalho.add_row(info_loja, "")
    console.print(
        Panel(
            cabecalho,
            title=f"[bold]🔔 RODADA {rodada}  |  TURNO DE [{jogador['cor']}]{jogador['nome'].upper()}[/][/]",
            box=box.DOUBLE,
            border_style=jogador["cor"],
            padding=(1, 3),
        )
    )
    if aviso:
        console.print(f"  {aviso}")
    console.print()
    console.print(tabela_arena(jogadores, jogador))
    console.print()
    menu = (
        "[bold red]1.[/] 🔪 Atacar Oponente"
        + (" [bright_black](custa 1/3 de mana)[/]" if jogador["raca"] == "Feiticeiro" else "")
        + "\n[bold blue]2.[/] 🔰 Adotar Postura Defensiva "
        f"[bright_black](bloqueia, reflete {round(REFLEXO_POSTURA * 100)}% e dá bônus racial)[/]\n"
        "[bold green]3.[/] 🎒 Inventário e Itens\n"
        "[bold yellow]4.[/] ⏩ Passar a Vez"
    )
    if jogador["raca"] == "Feiticeiro":
        menu += "\n[bold magenta]5.[/] 🔮 Escudo de Mana [bright_black](custa 2/3 de mana)[/]"
    console.print(
        Panel(menu, title="📜 ESCOLHA SUA AÇÃO", box=box.ROUNDED, border_style="white", padding=(1, 3))
    )


def alvos_disponiveis(atacante, jogadores):
    """Oponentes vivos que podem ser atacados: ainda não foram atacados nesta rodada e não estão invisíveis."""
    return [
        j for j in vivos(jogadores)
        if j is not atacante and not j["atacado_na_rodada"] and not j["invisivel"]
    ]


def alvos_afetaveis(jogador, jogadores):
    """Oponentes vivos que podem ser alvo de habilidades que não são ataques (só invisíveis ficam de fora)."""
    return [j for j in vivos(jogadores) if j is not jogador and not j["invisivel"]]


def escolher_alvo(atacante, jogadores, alvos=None, titulo="🎯 ESCOLHA O ALVO"):
    """Com 1 alvo possível escolhe sozinho; com 2 ou mais mostra um menu só com os alvos válidos."""
    if alvos is None:
        alvos = alvos_disponiveis(atacante, jogadores)
    if len(alvos) == 1:
        return alvos[0]
    tabela = Table(title=titulo, box=box.ROUNDED, border_style="red")
    tabela.add_column("#", justify="center", style="bold")
    tabela.add_column("Jogador", style="bold")
    tabela.add_column("💖 Vida")
    for i, a in enumerate(alvos, start=1):
        tabela.add_row(str(i), f"[{a['cor']}]{a['nome']}[/]", barra_hp(a["hp"], a["hp_max"]))
    console.print()
    console.print(tabela)
    escolha = ler_inteiro(f"[bold red]👉 Alvo (1-{len(alvos)}):[/] ", 1, len(alvos))
    return alvos[escolha - 1]


def painel_dado(titulo, valor, cor):
    return Align.center(
        Panel.fit(
            Text(f"🎲  {valor}", style=f"bold {cor}", justify="center"),
            title=titulo,
            box=box.ROUNDED,
            border_style=cor,
            padding=(0, 8),
        )
    )


def animar_dado(titulo, resultado, cor, duracao=3.0):
    """Mostra o D10 'rolando' por `duracao` segundos (desacelerando) e só então fixa o resultado."""
    atrasos = [0.05 * 1.08 ** i for i in range(24)]
    fator = duracao / sum(atrasos)
    with Live(console=console, refresh_per_second=30, transient=True) as live:
        for atraso in atrasos:
            live.update(painel_dado(titulo, random.randint(1, 10), cor))
            time.sleep(atraso * fator)
    console.print(painel_dado(titulo, resultado, cor))


def executar_ataque(atacante, alvo):
    """Ataque infalível com D10. Fúria do Bárbaro, bônus de itens (crítico, penetração, veneno, vampirismo...),
    postura do alvo (D10 + reflexo), Escudo de Mana, escudos de item, espinhos e Defesa fixa."""
    b = atacante["bonus"]
    linhas = [f"🔪 [bold {atacante['cor']}]{atacante['nome']}[/] ataca [bold {alvo['cor']}]{alvo['nome']}[/]!", ""]

    bonus_rolagem = atacante["buff_rolagem"]
    ataque = dice.resultado_ataque(b.get("crit", 0), bonus_rolagem)
    atacante["buff_rolagem"] = 0
    animar_dado(f"D10 DE ATAQUE • {atacante['nome']}", ataque["rolagem"], atacante["cor"])
    enfurecido = atacante["raca"] == "Bárbaro" and atacante["furia"] >= MAX_PIPS
    mult_furia = FURIA_MULT if enfurecido else 1
    buff_dano = atacante["buff_dano"]
    atacante["buff_dano"] = 1.0
    fisico, magico = atacante["dano_fisico"], atacante["dano_magico"]
    poder = fisico + magico
    dano = round(poder * ataque["fator"] * mult_furia * buff_dano)
    extra_dado = f" ({ataque['base']} +{bonus_rolagem} 🍀)" if bonus_rolagem else ""
    linhas.append(
        f"🎲 D10 de ataque: [bold]{ataque['rolagem']}[/]{extra_dado} → {ataque['emoji']} [bold]{ataque['nome']}[/] (×{ataque['fator']:g})"
    )
    if enfurecido:
        linhas.append(f"🔥 [bold red]FÚRIA![/] O dano é multiplicado por ×{FURIA_MULT:g}")
    if buff_dano > 1:
        linhas.append(f"💪 Bônus de dano ×{buff_dano:g}")
    composicao = f" (🔪 {fisico:g} + 🌠 {magico:g})" if fisico and magico else ""
    linhas.append(f"   Dano base {poder:g}{composicao} → [bold]{dano}[/]")
    if ataque["ouro"]:
        atacante["ouro"] += ataque["ouro"]
        linhas.append(f"💰 [bold yellow]{atacante['nome']} ganhou +{ataque['ouro']} moedas[/] de bônus!")
    if b.get("ouro_ataque"):
        atacante["ouro"] += b["ouro_ataque"]
        linhas.append(f"🪙 [yellow]+{b['ouro_ataque']} moedas saqueadas[/]")

    refletido = 0
    if alvo["postura"]:
        defesa = dice.resultado_defesa()
        animar_dado(f"D10 DE DEFESA • {alvo['nome']}", defesa["rolagem"], alvo["cor"])
        fator_def = defesa["fator"] + (POSTURA_FERREIRO if alvo["raca"] == "Ferreiro" else 0)
        fator_def += alvo["bonus"].get("bloqueio_postura", 0)
        fator_def = min(0.95, fator_def)
        bloqueado = round(dano * fator_def)
        dano -= bloqueado
        refletido = round(bloqueado * REFLEXO_POSTURA)
        alvo["postura"] = False  # a postura expira quando o impacto é processado
        linhas.append("")
        linhas.append(
            f"🎲 D10 de defesa de {alvo['nome']}: [bold]{defesa['rolagem']}[/] → {defesa['emoji']} "
            f"[bold]{defesa['nome']}[/] (bloqueia {round(fator_def * 100)}%)"
        )
        linhas.append(f"   🔰 Bloqueou [bold blue]{bloqueado}[/] de dano")
        if defesa["ouro"]:
            alvo["ouro"] += defesa["ouro"]
            linhas.append(f"💰 [bold yellow]{alvo['nome']} ganhou +{defesa['ouro']} moedas[/] pelo bloqueio épico!")

    if alvo["escudo_mana"]:
        mitigado = round(dano * ESCUDO_MANA)
        dano -= mitigado
        alvo["escudo_mana"] = False  # expira no impacto
        linhas.append("")
        linhas.append(f"🔮 O Escudo de Mana de {alvo['nome']} mitigou [bold cyan]{mitigado}[/] de dano!")

    # a parte mágica do dano ignora 50% da Defesa (proporcional à parte mágica do ataque); itens somam penetração
    parte_magica = magico / poder if poder else 0
    penetracao = min(0.9, PENETRACAO_MAGICA * parte_magica + b.get("penetracao", 0))
    defesa_alvo = alvo["defesa"] + alvo["defesa_temp"]
    defesa_efetiva = defesa_alvo * (1 - penetracao)
    dano_final = max(1, round(dano - defesa_efetiva))
    absorvido = dano - dano_final
    if penetracao > 0 and defesa_alvo > 0:
        icone = "🌠" if parte_magica >= 0.5 else "⚡"
        linhas.append(
            f"{icone} A penetração ignorou [bold magenta]{round(defesa_alvo - defesa_efetiva, 1):g}[/] da Defesa de {alvo['nome']}"
        )
    if absorvido > 0:
        linhas.append(f"🔰 A Defesa de {alvo['nome']} absorveu [bold blue]{absorvido}[/]")

    if alvo["escudo_pv"] > 0:
        absorve = min(alvo["escudo_pv"], dano_final)
        alvo["escudo_pv"] -= absorve
        dano_final -= absorve
        linhas.append(f"🧿 O escudo de {alvo['nome']} absorveu [bold cyan]{absorve}[/] de dano")

    hp_antes = alvo["hp"]
    alvo["hp"] = max(0, alvo["hp"] - dano_final)
    perdido = hp_antes - alvo["hp"]
    alvo["atacado_na_rodada"] = True
    linhas.append("")
    linhas.append(f"💥 {alvo['nome']} sofreu [bold red]{dano_final}[/] de dano. 💖 {alvo['hp']}/{alvo['hp_max']}")

    # Vampirismo: cura uma parte do dano que realmente tirou de vida
    if b.get("vampirismo") and perdido > 0 and atacante["hp"] < atacante["hp_max"]:
        curou = min(atacante["hp_max"] - atacante["hp"], max(1, round(perdido * b["vampirismo"])))
        atacante["hp"] += curou
        linhas.append(f"🩸 {atacante['nome']} drenou [bold green]{curou}[/] de vida. 💖 {atacante['hp']}/{atacante['hp_max']}")

    if alvo["hp"] == 0:
        alvo["vivo"] = False
        alvo["postura"] = False
        alvo["escudo_mana"] = False
        alvo["veneno"] = None
        linhas.append(f"💀 [bold red]{alvo['nome']} foi eliminado![/]")
    else:
        # Veneno: da arma envenenada (poção) ou dos itens equipados; só se o golpe feriu de verdade
        veneno = max(b.get("veneno", 0), atacante["arma_envenenada"])
        atacante["arma_envenenada"] = 0
        if veneno and perdido > 0:
            shop.aplicar_veneno(alvo, veneno)
            linhas.append(
                f"🐍 {alvo['nome']} foi envenenado: [bold green]{alvo['veneno']['dano']}[/] por rodada durante {shop.VENENO_RODADAS} rodadas"
            )
        # Espinhos do alvo: nunca eliminam o atacante (deixam no mínimo 1 de vida)
        espinhos = min(alvo["bonus"].get("espinhos", 0), atacante["hp"] - 1)
        if espinhos > 0:
            atacante["hp"] -= espinhos
            linhas.append(
                f"🌵 Os espinhos de {alvo['nome']} causaram [bold blue]{espinhos}[/] de dano em {atacante['nome']}. "
                f"💖 {atacante['hp']}/{atacante['hp_max']}"
            )
        if refletido > 0:
            # o reflexo da postura nunca elimina o atacante (deixa no mínimo 1 de vida)
            refletido = min(refletido, atacante["hp"] - 1)
            if refletido > 0:
                atacante["hp"] -= refletido
                linhas.append(
                    f"🔁 A postura de {alvo['nome']} refletiu [bold blue]{refletido}[/] de dano em {atacante['nome']}. "
                    f"💖 {atacante['hp']}/{atacante['hp_max']}"
                )

    # Fúria do Bárbaro: gasta ao atacar enfurecido; senão enche 1/3 (se não estiver desabilitada)
    if enfurecido:
        atacante["furia"] = 0
        atacante["furia_usada"] = True
        linhas.append("🔥 A Fúria foi zerada e fica desabilitada por 1 rodada.")
    elif atacante["raca"] == "Bárbaro" and atacante["furia_bloqueio"] == 0 and atacante["furia"] < MAX_PIPS:
        atacante["furia"] = min(MAX_PIPS, atacante["furia"] + 1 + b.get("furia_extra", 0))
        linhas.append(f"🔥 Fúria {pips(atacante['furia'], 'red')}")

    console.print()
    console.print(Panel("\n".join(linhas), title="💥 RESULTADO", box=box.HEAVY, border_style="red", padding=(1, 3)))


def dano_direto(atacante, alvo, dano, item):
    """Dano fixo de bombas e raios: ignora Defesa, postura e Escudo de Mana, mas o escudo de item ainda absorve.
    Conta como um ataque (o alvo não pode ser atacado de novo na rodada)."""
    linhas = [
        f"{item['nome']} • [bold {atacante['cor']}]{atacante['nome']}[/] atinge [bold {alvo['cor']}]{alvo['nome']}[/]!",
        "",
        f"   Dano fixo: [bold]{dano}[/]",
    ]
    if alvo["escudo_pv"] > 0:
        absorve = min(alvo["escudo_pv"], dano)
        alvo["escudo_pv"] -= absorve
        dano -= absorve
        linhas.append(f"🧿 O escudo de {alvo['nome']} absorveu [bold cyan]{absorve}[/] de dano")
    alvo["hp"] = max(0, alvo["hp"] - dano)
    alvo["atacado_na_rodada"] = True
    linhas.append("")
    linhas.append(f"💥 {alvo['nome']} sofreu [bold red]{dano}[/] de dano. 💖 {alvo['hp']}/{alvo['hp_max']}")
    if alvo["hp"] == 0:
        alvo["vivo"] = False
        alvo["postura"] = False
        alvo["escudo_mana"] = False
        alvo["veneno"] = None
        linhas.append(f"💀 [bold red]{alvo['nome']} foi eliminado![/]")
    console.print()
    console.print(Panel("\n".join(linhas), title="💥 RESULTADO", box=box.HEAVY, border_style="red", padding=(1, 3)))


def aplicar_item_com_alvo(jogador, item, alvo):
    """Usa um item que precisa de alvo (bomba, raio ou roubo) e gasta o item."""
    e = item["efeitos"]
    shop.gastar_item(jogador, item)
    if "roubo" in e:
        roubado = min(e["roubo"], alvo["ouro"])
        alvo["ouro"] -= roubado
        jogador["ouro"] += roubado
        console.print()
        console.print(
            Panel(
                f"{item['nome']} • [bold {jogador['cor']}]{jogador['nome']}[/] roubou [bold yellow]{roubado}[/] moedas "
                f"de [bold {alvo['cor']}]{alvo['nome']}[/]!",
                title="🧤 FURTO", box=box.HEAVY, border_style="yellow", padding=(1, 3),
            )
        )
        return
    dano_direto(jogador, alvo, e.get("bomba", e.get("raio", 0)), item)


def atacar(jogador, alvo):
    """Ação de ataque: o Feiticeiro paga 1/3 de mana e depois o golpe é resolvido."""
    if jogador["raca"] == "Feiticeiro":
        jogador["mana"] -= 1
        jogador["mana_gasta"] = True
    executar_ataque(jogador, alvo)


def assumir_postura(jogador):
    """Ativa a postura defensiva e aplica o bônus racial. Devolve a mensagem para exibir."""
    jogador["postura"] = True
    msg = f"🔰 [bold blue]{jogador['nome']}[/] assumiu a postura defensiva!"
    raca = jogador["raca"]
    if raca == "Bárbaro" and jogador["furia_bloqueio"] == 0 and jogador["furia"] < MAX_PIPS:
        jogador["furia"] = min(MAX_PIPS, jogador["furia"] + 1 + jogador["bonus"].get("furia_extra", 0))
        msg += f" 🔥 Fúria {pips(jogador['furia'], 'red')}"
    elif raca == "Feiticeiro" and jogador["mana"] < MAX_PIPS:
        jogador["mana"] += 1
        msg += f" 🔮 Mana {pips(jogador['mana'], 'cyan')}"
    elif raca == "Goblin":
        jogador["ouro"] += OURO_POSTURA_GOBLIN
        msg += f" 💰 +{OURO_POSTURA_GOBLIN} moedas"
    elif raca == "Ferreiro":
        msg += f" 🔨 Bloqueio reforçado (+{round(POSTURA_FERREIRO * 100)}%)"
    return msg


def ouro_do_turno(jogador):
    """Ouro recebido no início do turno. Devolve (total, extra_goblin, extra_itens)."""
    extra_goblin = OURO_GOBLIN if jogador["raca"] == "Goblin" else 0
    extra_itens = jogador["bonus"].get("ouro_turno", 0)
    total = OURO_POR_TURNO + extra_goblin + extra_itens
    jogador["ouro"] += total
    return total, extra_goblin, extra_itens


def inicio_de_turno(jogador):
    """Efeitos do início do turno (ouro, regeneração, fim da invisibilidade e do escudo). Devolve o aviso."""
    jogador["livre_usado"] = False
    jogador["invisivel"] = False
    jogador["escudo_pv"] = 0
    total, extra_goblin, extra_itens = ouro_do_turno(jogador)
    aviso = f"💰 [bold yellow]+{OURO_POR_TURNO} moedas[/] pelo início do turno!"
    if extra_goblin:
        aviso += f"  [green]👺 +{extra_goblin} do Goblin[/]"
    if extra_itens:
        aviso += f"  [yellow]🪙 +{extra_itens} dos itens[/]"
    cura = jogador["bonus"].get("cura_turno", 0)
    if cura and jogador["hp"] < jogador["hp_max"]:
        curou = min(cura, jogador["hp_max"] - jogador["hp"])
        jogador["hp"] += curou
        aviso += f"  [green]🌿 +{curou} de vida[/]"
    return aviso


def legenda_slots(jogador):
    partes = []
    for tipo, limite in shop.LIMITE_SLOTS.items():
        usados = len(shop.itens_do_slot(jogador, tipo))
        partes.append(f"{shop.ROTULO_SLOT[tipo].capitalize()} {usados}/{limite}")
    return "   ".join(partes)


def mostrar_inventario(jogador, jogadores):
    """Mostra o inventário e permite usar consumíveis e itens ativos.
    Devolve (encerra_turno, aviso): itens de ação livre não encerram o turno e devolvem um aviso."""
    while True:
        tabela = Table(
            title=f"🎒 INVENTÁRIO DE {jogador['nome'].upper()}",
            box=box.ROUNDED,
            border_style="green",
            header_style="bold white",
            caption=f"💰 {jogador['ouro']} moedas   •   Espaços: {legenda_slots(jogador)}",
        )
        tabela.add_column("#", justify="center", style="bold")
        tabela.add_column("Item")
        tabela.add_column("Tipo")
        tabela.add_column("Efeito")
        tabela.add_column("Estado")
        for i, item in enumerate(jogador["itens"], start=1):
            rotulo, cor = TIPOS_ITEM[item["tipo"]]
            efeitos = "\n".join(
                shop.descrever_efeitos(shop.efeitos_efetivos(jogador, item), item.get("magico", False))
            ) or "[bright_black]—[/]"
            forja = item.get("forja", 0)
            nome_item = item["nome"] + (f" [yellow]🔨+{round(forja * 5)}%[/]" if forja else "")
            if item["tipo"] == "consumivel" and item.get("usos", 1) > 1:
                nome_item += f" [bold]×{item['usos']}[/]"
            if item["tipo"] == "ativo":
                estado = "[green]pronto[/]" if item.get("recarga_atual", 0) == 0 else f"[yellow]⏳ {item['recarga_atual']} rod.[/]"
            elif item["tipo"] == "consumivel":
                estado = f"[green]{item.get('usos', 1)} uso(s)[/]"
            else:
                estado = "[bright_black]equipado[/]"
            tabela.add_row(str(i), nome_item, f"[{cor}]{rotulo}[/]", efeitos, estado)
        console.print()
        console.print(tabela)

        if not any(item["tipo"] in ("consumivel", "ativo") for item in jogador["itens"]):
            pausar("Pressione Enter para voltar ao menu...")
            return False, None

        escolha = ler_inteiro(
            "[bold green]👉 Número do item para usar (0 = voltar):[/] ", 0, len(jogador["itens"])
        )
        if escolha == 0:
            return False, None
        item = jogador["itens"][escolha - 1]
        pode, mensagem = shop.pode_usar(jogador, item)
        if not pode:
            erro(mensagem[2:])
            continue

        if shop.exige_alvo(item):
            if "roubo" in item["efeitos"]:
                alvos, titulo = alvos_afetaveis(jogador, jogadores), "🧤 DE QUEM ROUBAR?"
            else:
                alvos, titulo = alvos_disponiveis(jogador, jogadores), "🎯 ESCOLHA O ALVO"
            if not alvos:
                erro("Nenhum alvo disponível agora (já atacados nesta rodada ou invisíveis).")
                continue
            alvo = escolher_alvo(jogador, jogadores, alvos, titulo)
            aplicar_item_com_alvo(jogador, item, alvo)
            pausar()
            return True, None

        usou, mensagem = shop.usar_item(jogador, item)
        if not usou:
            erro(mensagem[2:])
            continue
        if item["efeitos"].get("livre"):
            return False, mensagem  # ação livre: o turno continua
        console.print(f"\n  {mensagem}")
        pausar()
        return True, None


def turno(rodada, jogador, jogadores):
    """Turno de um jogador. Ver inventário e usar itens de ação livre não encerram o turno."""
    aviso = inicio_de_turno(jogador)
    feiticeiro = jogador["raca"] == "Feiticeiro"
    maximo = 5 if feiticeiro else 4
    while True:
        tela_turno(rodada, jogador, jogadores, aviso)
        aviso = None
        escolha = ler_inteiro(f"[bold]👉 Escolha (1-{maximo}):[/] ", 1, maximo)
        if escolha == 1:
            if not alvos_disponiveis(jogador, jogadores):
                aviso = "[bold red]✖ Todos os oponentes vivos já foram atacados nesta rodada (ou estão invisíveis)![/]"
                continue
            if feiticeiro and jogador["mana"] < 1:
                aviso = "[bold red]✖ Sem mana para atacar! Escolha outra ação.[/]"
                continue
            alvo = escolher_alvo(jogador, jogadores)
            atacar(jogador, alvo)
            pausar()
            return
        if escolha == 2:
            console.print(f"\n  {assumir_postura(jogador)}")
            pausar()
            return
        if escolha == 3:
            encerra, mensagem = mostrar_inventario(jogador, jogadores)
            if encerra:
                return
            aviso = mensagem
            continue
        if escolha == 5:  # Escudo de Mana (só Feiticeiro)
            if jogador["mana"] < 2:
                aviso = "[bold red]✖ Mana insuficiente para o Escudo de Mana (precisa de 2/3).[/]"
                continue
            if jogador["escudo_mana"]:
                aviso = "[bold red]✖ O Escudo de Mana já está ativo.[/]"
                continue
            jogador["mana"] -= 2
            jogador["mana_gasta"] = True
            jogador["escudo_mana"] = True
            console.print(f"\n  🔮 [bold magenta]{jogador['nome']}[/] ergueu um Escudo de Mana!")
            pausar()
            return
        console.print(f"\n  ⏩ [bold yellow]{jogador['nome']}[/] passou a vez.")
        pausar()
        return


def fim_de_rodada(jogadores):
    """Efeitos de fim de rodada: veneno, recargas de itens, Defesa temporária, Fúria do Bárbaro e mana do
    Feiticeiro. Devolve a lista de eventos (textos) para exibir."""
    eventos = []
    for j in jogadores:
        j["atacado_na_rodada"] = False  # nova rodada: todos podem ser atacados de novo
    for j in vivos(jogadores):
        veneno = j["veneno"]
        if veneno:
            dano = min(veneno["dano"], j["hp"] - 1)  # o veneno nunca elimina
            if dano > 0:
                j["hp"] -= dano
                eventos.append(f"🐍 [bold {j['cor']}]{j['nome']}[/] sofreu [bold green]{dano}[/] de veneno. 💖 {j['hp']}/{j['hp_max']}")
            veneno["rodadas"] -= 1
            if veneno["rodadas"] <= 0:
                j["veneno"] = None
                eventos.append(f"🌿 O veneno de [bold {j['cor']}]{j['nome']}[/] passou.")
        if j["defesa_temp"]:
            j["defesa_temp_rodadas"] -= 1
            if j["defesa_temp_rodadas"] <= 0:
                j["defesa_temp"] = 0
        shop.avancar_recargas(j)
        if j["furia_usada"]:
            j["furia_usada"] = False
            j["furia_bloqueio"] = 1  # desabilitada durante a próxima rodada
        elif j["furia_bloqueio"] > 0:
            j["furia_bloqueio"] -= 1
        if j["raca"] == "Feiticeiro":
            regen = MANA_REGEN + (0 if j["mana_gasta"] else MANA_REGEN_EXTRA) + j["bonus"].get("mana_regen", 0)
            j["mana"] = min(MAX_PIPS, j["mana"] + regen)
            j["mana_gasta"] = False
    return eventos


# ----------------------------------------------------------------------
# O Comerciante
# ----------------------------------------------------------------------
def tabela_estoque(estoque, jogador=None):
    tabela = Table(
        title=f"🧳 ESTOQUE DE {jogador['nome'].upper()}" if jogador else "🧳 ESTOQUE DO COMERCIANTE",
        box=box.ROUNDED,
        border_style="yellow",
        header_style="bold white",
        show_lines=True,
    )
    tabela.add_column("#", justify="center", style="bold")
    tabela.add_column("Item", style="bold")
    tabela.add_column("Tipo")
    tabela.add_column("Fase")
    tabela.add_column("Efeitos")
    tabela.add_column("💰 Preço", justify="right")
    for i, item in enumerate(estoque, start=1):
        rotulo, cor = TIPOS_ITEM[item["tipo"]]
        nome_fase, cor_fase = TIERS[item["tier"]]
        efeitos = shop.efeitos_efetivos(jogador, item) if jogador else item["efeitos"]
        magico = item.get("magico", False)
        texto_efeitos = "\n".join(shop.descrever_efeitos(efeitos, magico, item.get("usos", 1)))
        nome = f"{item['emoji']} {item['nome']}"
        if item["disponivel"]:
            tabela.add_row(
                str(i), f"[{cor}]{nome}[/]", f"[{cor}]{rotulo}[/]", f"[{cor_fase}]{nome_fase}[/]",
                texto_efeitos, f"[bold yellow]{item['preco']}[/]",
            )
        else:
            tabela.add_row(
                str(i), f"[bright_black strike]{nome}[/]", f"[bright_black]{rotulo}[/]",
                f"[bright_black]{nome_fase}[/]", "[bright_black]—[/]", "[bold red]VENDIDO[/]",
            )
    return tabela


def painel_item(item, jogador):
    rotulo, cor = TIPOS_ITEM[item["tipo"]]
    nome_fase, cor_fase = TIERS[item["tier"]]
    efeitos = shop.efeitos_efetivos(jogador, item)
    magico = item.get("magico", False)
    corpo = Table.grid()
    corpo.add_column()
    corpo.add_row(f"[italic]{item['descricao']}[/]")
    corpo.add_row("")
    corpo.add_row("[bold underline]Detalhes[/]")
    corpo.add_row(f"  🔖 Tipo: [{cor}]{rotulo}[/]   📅 Fase: [{cor_fase}]{nome_fase}[/]")
    for linha in shop.descrever_efeitos(efeitos, magico, item.get("usos", 1)):
        corpo.add_row(f"  ✨ {linha}")
    if item["tipo"] in shop.EQUIPAVEIS and jogador.get("mult_equip", 1.0) > 1:
        corpo.add_row(f"  🔨 [bright_black]Já inclui o bônus de +{round((jogador['mult_equip'] - 1) * 100)}% do Ferreiro[/]")
    pode = jogador["ouro"] >= item["preco"]
    cor_preco = "green" if pode else "red"
    corpo.add_row(f"  💰 Preço: [bold {cor_preco}]{item['preco']} moedas[/] [bright_black](você tem {jogador['ouro']})[/]")
    if jogador["raca"] == "Goblin" and jogador["pechinchar_pronto"]:
        corpo.add_row(
            f"  🪙 [green]Pechinchar pronto: {round(shop.CHANCE_PECHINCHA * 100)}% de chance de "
            f"{round(shop.DESCONTO_PECHINCHA * 100)}% de desconto ao comprar[/]"
        )
    if item["tipo"] == "consumivel":
        corpo.add_row("  🎒 [bright_black]Vai para o inventário e é usado pelo menu de itens (ação livre ou gasta o turno, conforme o item).[/]")
    else:
        usados = len(shop.itens_do_slot(jogador, item["tipo"]))
        limite = shop.LIMITE_SLOTS[item["tipo"]]
        corpo.add_row(f"  🔧 [bright_black]Bônus aplicado enquanto estiver equipado (espaço de {shop.ROTULO_SLOT[item['tipo']]}: {usados}/{limite}).[/]")
        if item["tipo"] == "ativo":
            corpo.add_row("  💡 [bright_black]Use pelo Inventário; depois de usado, entra em recarga.[/]")
        if shop.slot_cheio(jogador, item["tipo"]):
            corpo.add_row("  🔁 [bold yellow]Espaço cheio: você vai escolher qual item equipado substituir.[/]")
    return Panel(
        corpo,
        title=f"[bold {cor}]{item['emoji']} {item['nome'].upper()}[/]",
        box=box.HEAVY,
        border_style=cor,
        padding=(1, 3),
    )


def escolher_substituicao(jogador, item):
    """Espaço cheio: o jogador escolhe qual item equipado será descartado. Devolve o item ou None (cancelou)."""
    candidatos = shop.itens_do_slot(jogador, item["tipo"])
    limite = shop.LIMITE_SLOTS[item["tipo"]]
    tabela = Table(
        title=f"🔁 ESPAÇO DE {shop.ROTULO_SLOT[item['tipo']].upper()} CHEIO ({len(candidatos)}/{limite}) • qual item substituir?",
        box=box.ROUNDED,
        border_style="yellow",
        header_style="bold white",
    )
    tabela.add_column("#", justify="center", style="bold")
    tabela.add_column("Item")
    tabela.add_column("Efeitos atuais")
    for i, c in enumerate(candidatos, start=1):
        efeitos = "\n".join(shop.descrever_efeitos(shop.efeitos_efetivos(jogador, c), c.get("magico", False)))
        forja = c.get("forja", 0)
        nome_c = c["nome"] + (f" [yellow]🔨+{round(forja * 5)}%[/]" if forja else "")
        tabela.add_row(str(i), nome_c, efeitos)
    console.print()
    console.print(tabela)
    escolha = ler_inteiro(f"[bold yellow]👉 Substituir qual item? (1-{len(candidatos)}, 0 = cancelar):[/] ", 0, len(candidatos))
    return None if escolha == 0 else candidatos[escolha - 1]


def menu_forja(jogador):
    """Ferreiro: escolhe 1 item de combate físico para melhorar. Devolve uma mensagem (ou None se voltou)."""
    if jogador["forja_usada"]:
        return "[bold red]✖ A Forja já foi usada nesta visita do Comerciante.[/]"
    equipaveis = [i for i in jogador["itens"] if i["tipo"] in shop.EQUIPAVEIS]
    if not equipaveis:
        return "[bold red]✖ Você não tem armas ou armaduras para forjar.[/]"
    forjaveis = [i for i in equipaveis if i.get("forja", 0) < shop.MAX_FORJA]
    if not forjaveis:
        return f"[bold red]✖ Todos os seus itens já estão no nível máximo da Forja ({shop.MAX_FORJA}).[/]"
    tabela = Table(
        title=f"🔨 A FORJA • melhora 1 item em +{round(shop.BONUS_FORJA * 100)}% (máx. {shop.MAX_FORJA} níveis por item)",
        box=box.ROUNDED,
        border_style="yellow",
        header_style="bold white",
    )
    tabela.add_column("#", justify="center", style="bold")
    tabela.add_column("Item")
    tabela.add_column("Efeitos atuais")
    tabela.add_column("Forja", justify="center")
    for i, item in enumerate(forjaveis, start=1):
        efeitos = "\n".join(shop.descrever_efeitos(shop.efeitos_efetivos(jogador, item), item.get("magico", False)))
        nivel = item.get("forja", 0)
        tabela.add_row(str(i), item["nome"], efeitos, f"+{round(nivel * 5)}% ({nivel}/{shop.MAX_FORJA})")
    console.print()
    console.print(tabela)
    escolha = ler_inteiro(f"[bold yellow]👉 Item para forjar (1-{len(forjaveis)}, 0 = voltar):[/] ", 0, len(forjaveis))
    if escolha == 0:
        return None
    sucesso, mensagem = shop.forjar(jogador, forjaveis[escolha - 1])
    return f"[bold green]{mensagem}[/]" if sucesso else f"[bold red]✖ {mensagem[2:]}[/]"


def loja_jogador(jogador, estoque):
    """Vez de um jogador no Comerciante (à vista de todos). Cada jogador compra no máximo 1 item."""
    ferreiro = jogador["raca"] == "Ferreiro"
    limite_compras = shop.compras_permitidas(jogador)
    compras = 0
    comprados = []  # nomes dos itens comprados nesta visita
    comprou = False  # True quando já esgotou as compras permitidas
    aviso = None
    while True:
        console.clear()
        r = RACAS[jogador["raca"]]
        cabecalho = Table.grid(padding=(0, 3))
        cabecalho.add_column()
        cabecalho.add_column()
        cabecalho.add_row(
            f"{r['emoji']} [bold {r['cor']}]{jogador['raca']}[/]   💰 [bold yellow]{jogador['ouro']} moedas[/]",
            f"🔪 Físico {jogador['dano_fisico']}   🌠 Mágico {jogador['dano_magico']}   🔰 Defesa {jogador['defesa']}   💖 {jogador['hp']}/{jogador['hp_max']}",
        )
        cabecalho.add_row(f"🎽 Espaços: {legenda_slots(jogador)}", "")
        recurso = linha_recurso(jogador) if jogador["raca"] in ("Goblin", "Ferreiro") else ""
        if recurso:
            cabecalho.add_row(recurso, "")
        console.print(
            Panel(
                cabecalho,
                title=f"[bold]🧳 O COMERCIANTE  |  VEZ DE [{jogador['cor']}]{jogador['nome'].upper()}[/][/]",
                box=box.DOUBLE,
                border_style="yellow",
                padding=(1, 3),
            )
        )
        if aviso:
            console.print(f"  {aviso}")
            aviso = None
        if comprou:
            console.print("  [bright_black]Você já fez as suas compras desta visita.[/]")
        else:
            console.print(
                f"  [bright_black]Este estoque foi sorteado só para {jogador['nome']}. "
                f"Compras restantes: {limite_compras - compras} de {limite_compras}.[/]"
            )
        console.print()
        console.print(tabela_estoque(estoque, jogador))
        console.print("\n  [bold yellow]0.[/] 🚪 Sair do Comerciante")
        n_itens = 0 if comprou else len(estoque)
        maximo = n_itens + (1 if ferreiro else 0)
        if ferreiro:
            console.print(f"  [bold yellow]{maximo}.[/] 🔨 Usar A Forja")
        escolha = ler_inteiro(f"[bold]👉 Escolha (0-{maximo}):[/] ", 0, maximo)
        if escolha == 0:
            return comprados
        if ferreiro and escolha == maximo:
            aviso = menu_forja(jogador)
        else:
            item = estoque[escolha - 1]
            if not item["disponivel"]:
                aviso = "[bold red]✖ Esse item já foi vendido![/]"
                continue
            console.print()
            console.print(painel_item(item, jogador))
            console.print("  [bold green]1.[/] ✅ Comprar     [bold red]2.[/] 🔙 Voltar")
            if ler_inteiro("[bold]👉 Escolha (1-2):[/] ", 1, 2) == 1:
                substituir = None
                if item["tipo"] != "consumivel" and shop.slot_cheio(jogador, item["tipo"]) and jogador["ouro"] >= item["preco"]:
                    substituir = escolher_substituicao(jogador, item)
                    if substituir is None:
                        continue
                sucesso, mensagem = shop.comprar(jogador, item, substituir)
                if sucesso:
                    compras += 1
                    comprados.append(f"{item['emoji']} {item['nome']}")
                    comprou = compras >= limite_compras
                    aviso = f"[bold green]{mensagem}[/]"
                else:
                    aviso = f"[bold red]✖ {mensagem[2:]}[/]"
        # Compra feita e nada mais a fazer (só o Ferreiro ainda pode usar A Forja): encerra a vez
        if comprou and (not ferreiro or jogador["forja_usada"]):
            if aviso:
                console.print(f"\n  {aviso}")
            pausar()
            return comprados


def fase_loja(jogadores, ordem, rodada=INTERVALO_LOJA):
    """Rodada exclusiva do Comerciante: cada jogador vivo compra em sequência, num estoque só dele (sorteado à
    parte, então os itens podem se repetir entre jogadores). O estoque só tem itens da fase da rodada:
    Early até a rodada 15, Mid até a 30 e Late depois."""
    fase = shop.fase_da_rodada(rodada)
    compradores = [j for j in ordem if j["vivo"]]
    for j in compradores:
        j["ouro"] += OURO_LOJA + (OURO_GOBLIN if j["raca"] == "Goblin" else 0)
        j["forja_usada"] = False
        j["pechinchar_pronto"] = True

    console.clear()
    abertura = Text(justify="center")
    abertura.append("🧳  O COMERCIANTE CHEGOU!  🧳\n\n", style="bold yellow")
    abertura.append(f"Rodada exclusiva de compras • cada jogador recebe +{OURO_LOJA} moedas\n", style="white")
    abertura.append(
        f"Cada jogador tem um estoque próprio de {shop.ITENS_POR_JOGADOR} itens, sorteado só para ele • 1 compra por jogador!\n",
        style="bright_black",
    )
    nome_fase, cor_fase = TIERS[fase]
    abertura.append(f"Rodada {rodada} • só itens da fase ", style="bright_black")
    abertura.append(nome_fase, style=f"bold {cor_fase}")
    abertura.append(" (Early até a rodada 15, Mid até a 30, Late depois)", style="bright_black")
    console.print()
    console.print(Align.center(Panel(Align.center(abertura), box=box.DOUBLE, border_style="yellow", padding=(1, 6))))
    mostrar_ordem(compradores, "DE COMPRAS")
    pausar("Pressione Enter para abrir o Comerciante...")

    resumo = []
    for jogador in compradores:
        estoque = shop.sortear_estoque(rodada)
        comprados = loja_jogador(jogador, estoque)
        resumo.append(f"[{jogador['cor']}]{jogador['nome']}[/]: {', '.join(comprados) if comprados else 'não comprou nada'}")

    for j in jogadores:
        j["pechinchar_pronto"] = True  # Pechinchar volta ao normal quando o Comerciante parte
        j["forja_usada"] = False

    console.clear()
    console.print()
    console.print(
        Panel(
            "Compras desta visita:\n" + "\n".join(f"  • {linha}" for linha in resumo) + "\n\nO combate será retomado!",
            title="🧳 O COMERCIANTE PARTIU",
            box=box.DOUBLE,
            border_style="yellow",
            padding=(1, 4),
        )
    )
    pausar("Pressione Enter para voltar ao combate...")


def jogar(jogadores):
    """Loop de rodadas. Devolve o vencedor quando restar apenas 1 jogador vivo."""
    rodada = 1
    primeiro_anterior = None
    while True:
        console.clear()
        ordem = sortear_ordem(jogadores, primeiro_anterior)
        if rodada == 1:
            console.print()
            animar_roleta(ordem)
        mostrar_ordem(ordem, rodada)
        pausar("Pressione Enter para iniciar a rodada...")
        primeiro_anterior = ordem[0]

        for jogador in ordem:
            if not jogador["vivo"]:
                continue
            turno(rodada, jogador, jogadores)
            sobreviventes = vivos(jogadores)
            if len(sobreviventes) == 1:
                return sobreviventes[0]
        eventos = fim_de_rodada(jogadores)
        if eventos:
            console.print()
            console.print(
                Panel("\n".join(eventos), title=f"🌙 FIM DA RODADA {rodada}", box=box.ROUNDED,
                      border_style="green", padding=(1, 3))
            )
            pausar()
        if rodada % INTERVALO_LOJA == 0:
            fase_loja(jogadores, shop.ordem_compras(jogadores), rodada)
        rodada += 1


def tela_vitoria(vencedor):
    console.clear()
    r = RACAS[vencedor["raca"]]
    corpo = Text(justify="center")
    corpo.append("🏆  VENCEDOR  🏆\n\n", style="bold yellow")
    corpo.append(f"{r['emoji']} {vencedor['nome']}\n", style=f"bold {vencedor['cor']}")
    corpo.append(f"{vencedor['raca']} • 💖 {vencedor['hp']}/{vencedor['hp_max']} • 💰 {vencedor['ouro']}", style="white")
    console.print()
    console.print(Align.center(Panel(Align.center(corpo), box=box.DOUBLE, border_style="yellow", padding=(2, 10))))


def main():
    jogadores = configurar_jogadores()
    tela_resumo(jogadores)
    pausar("Pressione Enter para começar o jogo...")
    vencedor = jogar(jogadores)
    tela_vitoria(vencedor)


if __name__ == "__main__":
    main()
