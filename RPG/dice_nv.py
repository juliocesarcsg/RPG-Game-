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

FAIXAS_DEFESA = [
    {"nome": "Defesa Parcial",  "emoji": "🔹", "min": 1,  "max": 4,  "fator": 0.30, "ouro": 0},
    {"nome": "Defesa Padrão",   "emoji": "🔰", "min": 5,  "max": 9,  "fator": 0.60, "ouro": 0},
    {"nome": "DEFESA PERFEITA", "emoji": "✨", "min": 10, "max": 10, "fator": 0.90, "ouro": OURO_DEFESA_PERFEITA},
]


def _montar(rolagem, faixa, base=None):
    return {
        "rolagem": rolagem,
        "base": rolagem if base is None else base,  # valor puro do dado (antes de bônus)
        "nome": faixa["nome"],
        "emoji": faixa["emoji"],
        "fator": faixa["fator"],
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
    """Rola o D10 de defesa. Devolve dict com rolagem, nome, emoji, fator e ouro."""
    return _resultado(FAIXAS_DEFESA)