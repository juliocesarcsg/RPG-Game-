# Tabelas da Arena de Combate

Gerado automaticamente a partir do código (`main.py` e `shop.py`).

## Raças

| Raça | Vida | Dano físico | Dano mágico | Defesa | Dano inicial total | Item inicial |
|---|---|---|---|---|---|---|
| 🪓 Bárbaro | 120 | 3 | 0 | 0 | 6 | 🔪 Espada Curta (+3 físico) |
| 👺 Goblin | 115 | 3 | 0 | 0 | 6 | 🔪 Adaga cega (+3 físico) |
| 🔮 Feiticeiro | 110 | 0 | 5 | 0 | 8 | 📖 Livro velho (+3 mágico) |
| 🔨 Ferreiro | 110 | 3 | 0 | 0 | 6.3 | 🔨 Martelo desgastado (+3 físico) |

| Raça | Passiva | Habilidade | Postura defensiva |
|---|---|---|---|
| 🪓 Bárbaro | Fúria: barra 4/4. Cada ataque enche 1/4. Cheia, o próximo ataque rola 2 D10 de ataque e soma o dano dos dois golpes; depois zera a barra e a desabilita por 1 rodada. | — | Postura: sem bônus racial (não enche a Fúria). |
| 👺 Goblin | Ganancioso: ganha 50% a mais de ouro no turno (+3; +4 depois da rodada 10; +5 depois da rodada 20) e no Comerciante (+5). | Pechinchar: ao comprar do Comerciante, 35% de chance de 15% de desconto. Depois do desconto, fica desabilitada até a próxima visita. | Postura: sem bônus racial (não dá ouro). |
| 🔮 Feiticeiro | Mana: barra 3/3. Cada ataque custa 1/3. Ao fim de toda rodada restaura 1/3 (+1/3 se não gastou mana). Seu dano é mágico: ignora 75% da Defesa do alvo. | Escudo de Mana: gasta 2/3 da mana e mitiga 60% do dano do próximo ataque recebido. | Postura: recupera +1/3 de mana. |
| 🔨 Ferreiro | Mestre do Metal: armas e armaduras são 10% mais eficientes nele. | A Forja: quando o Comerciante chega, melhora 1 item de combate físico em +10% e ainda +1 de Dano (arma) ou +1 de Defesa e +10 de Vida máxima (armadura) por nível (1 uso por visita, até 3 níveis por item). | Postura: bloqueia +10% a mais do dano. |

## Itens

Fases do Comerciante: Early até a rodada 9, Mid a partir da 10, Late a partir da 20. Por visita: 1 equipamento e 1 consumível. Dano de item fora da afinidade da raça rende 50% (mágico em quem não é Feiticeiro; físico no Feiticeiro).

### Poções fixas (sempre à venda)

| Item | Disponível | Preço | Efeitos |
|---|---|---|---|
| 🩹 Poção Simples | até a rodada 15 | 10 | 💚 Cura 15 de vida |
| 🧴 Poção Reforçada | a partir da rodada 20 | 20 | 💚 Cura 30 de vida |

### Armas (13)

| Item | Fase | Preço | Tipo de dano | Efeitos |
|---|---|---|---|---|
| 🔪 Espada de Aço | Early | 25 | físico | 🔪 +4 de Dano |
| 🔮 Orbe Mágico | Early | 25 | mágico | 🌠 +4 de Dano |
| 🪓 Machadinha | Early | 30 | físico | 🔪 +4 de Dano; 🎯 +1 na faixa de crítico |
| 🥊 Manoplas do Saqueador | Early | 30 | físico | 🔪 +3 de Dano; 🪙 +2 moedas por ataque |
| 🐍 Presa de Víbora | Mid | 46 | físico | 🔪 +3 de Dano; 🐍 Ataques envenenam (3/rodada por 3 rodadas) |
| 🏹 Arco Longo | Mid | 50 | físico | 🔪 +5 de Dano; 🎯 +1 na faixa de crítico |
| 🔨 Maça Estilhaçadora | Mid | 50 | físico | 🔪 +5 de Dano; ⚡ Ignora 30% da Defesa do alvo |
| 🪓 Machado Sedento | Mid | 52 | físico | 🔪 +5 de Dano; 🩸 Cura 15% do dano causado |
| 🌟 Cajado Arcano | Mid | 55 | mágico | 🌠 +5 de Dano; ⚡ Ignora 25% da Defesa do alvo |
| 🔱 Lança Rúnica | Mid | 60 | físico | 🔪 +7 de Dano |
| 🌙 Lâmina Lunar | Late | 90 | híbrido | 🔪🌠 +7 de Dano (metade físico, metade mágico); 🎯 +2 na faixa de crítico |
| 📖 Grimório Sombrio | Late | 95 | mágico | 🌠 +7 de Dano; ⚡ Ignora 15% da Defesa do alvo; 🩸 Cura 15% do dano causado |
| 🔫 Mosquete | Late | 100 | físico | 🔪 +9 de Dano; ⚡ Ignora 40% da Defesa do alvo |

### Armaduras (8)

| Item | Fase | Preço | Efeitos |
|---|---|---|---|
| 🧥 Gibão Acolchoado | Early | 26 | 🔰 +1 de Defesa; 💖 +20 de Vida máxima; 🌿 Regenera 1 de vida por turno |
| 🥋 Armadura de Couro | Early | 30 | 🔰 +1 de Defesa; 💖 +35 de Vida máxima |
| 🦺 Cota de Malha | Mid | 42 | 🔰 +2 de Defesa; 💖 +45 de Vida máxima; 🌵 Reflete 1 de dano em quem te atacar |
| 🔰 Armadura de Placas | Mid | 50 | 🔰 +3 de Defesa; 💖 +65 de Vida máxima |
| 🧙 Manto Arcano | Mid | 52 | 🔰 +1 de Defesa; 💖 +40 de Vida máxima; 🌿 Regenera 1 de vida por turno; 🔮 +1 de mana por rodada (Feiticeiro) |
| 🌵 Couraça de Espinhos | Mid | 55 | 🔰 +2 de Defesa; 💖 +45 de Vida máxima; 🌵 Reflete 2 de dano em quem te atacar |
| 💎 Armadura de Mithril | Late | 100 | 🔰 +5 de Defesa; 💖 +70 de Vida máxima |
| 🐲 Escamas de Dragão | Late | 105 | 🔰 +3 de Defesa; 💖 +75 de Vida máxima; 🌵 Reflete 1 de dano em quem te atacar; 🔰 +15% de bloqueio na postura |

### Joias (16)

| Item | Fase | Preço | Tipo de dano | Efeitos |
|---|---|---|---|---|
| 💍 Anel do Vigor | Early | 16 | — | 💖 +15 de Vida máxima |
| 💍 Anel de Ferro | Early | 18 | — | 🔰 +1 de Defesa; 💖 +10 de Vida máxima |
| 💍 Anel do Lucro | Early | 22 | — | 💖 +10 de Vida máxima; 🪙 +2 moedas por turno |
| 💍 Anel de Espinhos | Early | 24 | — | 💖 +10 de Vida máxima; 🌵 Reflete 3 de dano em quem te atacar |
| 💍 Anel da Sorte | Mid | 36 | físico | 🔪 +1 de Dano; 🎯 +2 na faixa de crítico |
| 💍 Anel do Bruto | Mid | 36 | físico | 🔪 +4 de Dano |
| 💍 Anel Arcano | Mid | 36 | — | 💖 +15 de Vida máxima; ⚡ Ignora 25% da Defesa do alvo; 🔮 +1 de mana por rodada (Feiticeiro) |
| 💍 Anel do Mago | Mid | 36 | mágico | 🌠 +4 de Dano |
| 💍 Anel da Fúria | Mid | 38 | físico | 🔪 +3 de Dano; 💖 +10 de Vida máxima; 🔥 Fúria enche +1 a mais (Bárbaro) |
| 💍 Anel Perfurante | Mid | 40 | físico | 🔪 +2 de Dano; ⚡ Ignora 50% da Defesa do alvo |
| 💍 Anel Regenerador | Mid | 40 | — | 🌿 Regenera 2 de vida por turno |
| 💍 Anel Sanguessuga | Mid | 42 | — | 💖 +10 de Vida máxima; 🩸 Cura 25% do dano causado |
| 💍 Anel Venenoso | Late | 70 | — | 🐍 Ataques envenenam (4/rodada por 3 rodadas); ⏳ Recarga de 3 rodadas |
| 📿 Amuleto da Fortuna | Late | 75 | — | 💖 +20 de Vida máxima; 🎯 +2 na faixa de crítico; 🪙 +3 moedas por turno |
| 📿 Amuleto Arcano | Late | 80 | mágico | 🌠 +6 de Dano; 💖 +20 de Vida máxima |
| 📿 Amuleto do Vampiro | Late | 85 | — | 💖 +40 de Vida máxima; 🩸 Cura 20% do dano causado |

### Itens ativos (6)

| Item | Fase | Preço | Efeitos |
|---|---|---|---|
| 🧤 Luvas do Ladrão | Mid | 35 | 🧤 Rouba até 10 moedas de um oponente; 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 2 rodadas |
| 🏺 Cálice Vital | Mid | 45 | 💚 Cura 20 de vida; ⏳ Recarga de 4 rodadas |
| 🧿 Olho Protetor | Mid | 50 | 🧿 Escudo de 20 de dano até o seu próximo turno; 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 2 rodadas |
| 📯 Chifre de Guerra | Mid | 55 | 💪 Próximo ataque causa ×2 de dano; 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 3 rodadas |
| 👻 Capa da Invisibilidade | Late | 75 | 💪 Próximo ataque causa ×1.5 de dano; 👻 Invisível até o seu próximo turno (ninguém pode te escolher); 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 3 rodadas |
| ⚡ Cajado Relâmpago | Late | 75 | ⚡ Raio de 16 de dano fixo (ignora Defesa e postura); ⏳ Recarga de 3 rodadas |

### Consumíveis (11)

| Item | Fase | Preço | Efeitos |
|---|---|---|---|
| 🌿 Antídoto | Early | 10 | 💚 Cura 10 de vida; 🌿 Remove veneno |
| 🔥 Poção de Fúria | Early | 20 | 💪 Próximo ataque causa ×2 de dano; 🆓 Ação livre (não gasta o turno) |
| 🧨 Bombinha | Early | 22 | 💣 10 de dano fixo (ignora Defesa e postura) |
| 🧪 Poção de Cura | Early | 24 | 💚 Cura 30 de vida |
| 🐍 Frasco de Veneno | Early | 24 | 🐍 Próximo ataque envenena (2/rodada por 3 rodadas); 🆓 Ação livre (não gasta o turno) |
| 🍀 Trevo da Sorte | Mid | 18 | 🍀 +4 na rolagem do próximo ataque; 🆓 Ação livre (não gasta o turno) |
| 🧱 Pele de Pedra | Mid | 30 | 🧱 +4 de Defesa por 2 rodadas; 🆓 Ação livre (não gasta o turno) |
| 💣 Bomba de Pólvora | Mid | 34 | 💣 14 de dano fixo (ignora Defesa e postura) |
| 🍷 Elixir Maior | Mid | 40 | 💚 Cura 60 de vida |
| 🦂 Essência de Escorpião | Late | 42 | 🐍 Próximo ataque envenena (4/rodada por 3 rodadas); 🆓 Ação livre (não gasta o turno) |
| 🍶 Elixir Dourado | Late | 55 | 💚 Cura 70 de vida; 🌿 Remove veneno |
