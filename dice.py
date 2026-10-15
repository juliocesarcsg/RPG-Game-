"""Dados e faixas de resultado do jogo (D10 de ataque e de defesa)."""

import random

OURO_CRITICO = 3          # bônus de moedas no golpe crítico (antes: 6)
OURO_DEFESA_PERFEITA = 6  # bônus de moedas na defesa perfeita (antes: 10)
CRIT_MINIMO = 6           # nem com muitos bônus o crítico começa abaixo deste valor do D10


def rolar(lados):
    """Rola um dado de `lados` lados e devolve o resultado (1 a lados)."""
    return random.randint(1, lados)


def rolar_d10():
    return rolar(10)


def rolar_d20():
    return rolar(20)


# ----------------------------------------------------------------------
# Faixas do D10 (valores provisórios, ajustar para balancear)
#   fator: no ataque multiplica o dano; na defesa é a fração do dano bloqueada
#   ouro:  bônus de moedas imediato
# ----------------------------------------------------------------------
FAIXAS_ATAQUE = [
    {"nome": "Golpe Fraco",   "emoji": "💨", "min": 1, "max": 3,  "fator": 0.5, "ouro": 0},
    {"nome": "Golpe Normal",  "emoji": "🔪", "min": 4, "max": 8,  "fator": 1.0, "ouro": 0},
    {"nome": "GOLPE CRÍTICO", "emoji": "💥", "min": 9, "max": 10, "fator": 2.0, "ouro": OURO_CRITICO},
]

# Postura defensiva: fração do dano bloqueada para cada resultado do D10 de defesa
# (1–2 não bloqueiam; do 3 ao 9 sobe 10% por ponto; o 10 bloqueia 95%). Antes: 30% / 60% / 90% por faixa.
BLOQUEIO_DEFESA = {1: 0.0, 2: 0.0, 3: 0.10, 4: 0.20, 5: 0.30, 6: 0.40, 7: 0.50, 8: 0.60, 9: 0.70, 10: 0.95}

# Na defesa o fator vem de BLOQUEIO_DEFESA (por resultado); as faixas só dão nome, emoji e ouro
FAIXAS_DEFESA = [
    {"nome": "Defesa Falhou",   "emoji": "💢", "min": 1,  "max": 2,  "ouro": 0},
    {"nome": "Defesa Parcial",  "emoji": "🔹", "min": 3,  "max": 6,  "ouro": 0},
    {"nome": "Defesa Sólida",   "emoji": "🔰", "min": 7,  "max": 9,  "ouro": 0},
    {"nome": "DEFESA PERFEITA", "emoji": "✨", "min": 10, "max": 10, "ouro": OURO_DEFESA_PERFEITA},
]


def texto_bloqueio_defesa():
    """Bloqueio da postura por resultado do D10, para a interface (ex.: '1–2: 0%, 3: 10%, ..., 10: 95%')."""
    partes = []  # [rótulo, porcentagem]; resultados seguidos com a mesma porcentagem viram um intervalo
    for rolagem in range(1, 11):
        pct = round(BLOQUEIO_DEFESA[rolagem] * 100)
        if partes and partes[-1][1] == pct:
            partes[-1][0] = f"{partes[-1][0].split('–')[0]}–{rolagem}"
        else:
            partes.append([str(rolagem), pct])
    return ", ".join(f"{r}: {p}%" for r, p in partes)


def _montar(rolagem, faixa, base=None):
    return {
        "rolagem": rolagem,
        "base": rolagem if base is None else base,  # valor puro do dado (antes de bônus)
        "nome": faixa["nome"],
        "emoji": faixa["emoji"],
        "fator": faixa.get("fator"),
        "ouro": faixa["ouro"],
    }


def _resultado(faixas):
    rolagem = rolar_d10()
    for faixa in faixas:
        if faixa["min"] <= rolagem <= faixa["max"]:
            return _montar(rolagem, faixa)
    raise ValueError(f"Rolagem {rolagem} fora das faixas")


def resultado_ataque(bonus_crit=0, bonus_rolagem=0):
    """Rola o D10 de ataque.

    bonus_crit:    abaixa o valor mínimo do crítico (ex.: +1 faz o crítico começar no 8)
    bonus_rolagem: soma ao resultado do dado (máx. 10)
    Devolve dict com rolagem, base, nome, emoji, fator e ouro."""
    base = rolar_d10()
    rolagem = min(10, base + bonus_rolagem)
    critico = FAIXAS_ATAQUE[2]
    minimo_critico = max(CRIT_MINIMO, critico["min"] - bonus_crit)
    if rolagem >= minimo_critico:
        return _montar(rolagem, critico, base)
    for faixa in FAIXAS_ATAQUE[:2]:
        if faixa["min"] <= rolagem <= faixa["max"]:
            return _montar(rolagem, faixa, base)
    raise ValueError(f"Rolagem {rolagem} fora das faixas")


def resultado_defesa():
    """Rola o D10 de defesa. Devolve dict com rolagem, nome, emoji, fator (fração do dano bloqueada) e ouro."""
    resultado = _resultado(FAIXAS_DEFESA)
    resultado["fator"] = BLOQUEIO_DEFESA[resultado["rolagem"]]
    return resultado