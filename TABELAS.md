# Tabelas da Arena de Combate

Gerado automaticamente a partir do código (`main.py` e `shop.py`).

## Personagens

| Personagem | Vida | Dano físico | Dano mágico | Defesa | Dano inicial total | Estilo | Item inicial |
|---|---|---|---|---|---|---|---|
| 🪓 Bárbaro | 120 | 3 | 0 | 0 | 6 | corpo a corpo, físico | 🔪 Espada Curta (+3 físico, corpo a corpo) |
| 👺 Goblin | 115 | 2 | 0 | 0 | 5 | corpo a corpo, físico | 🔪 Adaga cega (+3 físico, corpo a corpo) |
| 🔮 Feiticeiro | 110 | 0 | 5 | 0 | 8 | à distância, mágico | 📖 Livro velho (+3 mágico, à distância) |
| 🔨 Ferreiro | 110 | 3 | 0 | 0 | 6.3 | corpo a corpo, físico | 🔨 Martelo desgastado (+3 físico, corpo a corpo) |
| 🩸 Hemomante | 110 | 0 | 3 | 0 | 6 | à distância, mágico | 🩸 Frasco de sangue (+3 mágico, à distância) |
| ⚗️ Alquimista | 110 | 2 | 2 | 0 | 6 | híbrido, híbrido | 🧤 Par de luvas (+2 mágico, corpo a corpo) |
| 🎯 Mosqueteiro | 105 | 4 | 0 | 0 | 7 | à distância, físico | 🪨 Estilingue de madeira (+3 físico, à distância) |

| Personagem | Passiva | Habilidade | Postura defensiva |
|---|---|---|---|
| 🪓 Bárbaro | Fúria: barra 4/4. Cada ataque enche 1/4. Cheia, o próximo ataque rola 2 D10 de ataque e soma o dano dos dois golpes; depois zera a barra e a desabilita por 1 rodada. | Fôlego de Batalha (ação livre, com a Fúria cheia): consome a Fúria e cura 15% da vida máxima. A barra zera e fica desabilitada por 1 rodada. | Postura: sem bônus especial (não enche a Fúria). |
| 👺 Goblin | Ganancioso: ganha 50% a mais de ouro no turno (+3; +4 depois da rodada 10; +5 depois da rodada 20; +6 depois da rodada 30) e no Comerciante (+5). Crítico ladrão: cada crítico rouba 2 moedas do alvo (no lugar do bônus de moedas do crítico). | Pechinchar: ao comprar do Comerciante, 35% de chance de 15% de desconto. Depois do desconto, fica desabilitada até a próxima visita. | Postura: sem bônus especial (não dá ouro). |
| 🔮 Feiticeiro | Mana: barra 3/3. Cada ataque custa 1/3. Ao fim de toda rodada restaura 1/3 (+1/3 se não gastou mana). Seu dano é mágico: ignora 75% da Defesa do alvo. | Escudo de Mana: gasta 2/3 da mana e mitiga 50% do dano do próximo ataque recebido. Dura no máximo 3 rodadas (contando a rodada em que foi erguido). | Não usa a postura defensiva: no lugar dela há o Escudo de Mana. |
| 🔨 Ferreiro | Mestre do Metal: armas e armaduras são 10% mais eficientes nele. | A Forja: quando o Comerciante chega, melhora 1 item de combate físico em +10% e ainda +1 de Dano (arma) ou +1 de Defesa e +10 de Vida máxima (armadura) por nível (1 uso por visita, até 3 níveis por item). | Postura: bloqueia +10% a mais do dano. |
| 🩸 Hemomante | Vampirismo: cura 30% do dano causado (soma com itens, até 50%). Em compensação, curas de consumíveis rendem só 75%. | Pacto de Sangue (ação livre, 1 vez por turno): paga 4 de vida para o próximo ataque causar ×1,5. Não pode matar a si mesmo e não acumula com outros bônus de dano (vale o maior). | Postura: sem bônus especial. |
| ⚗️ Alquimista | Bolsa de poções: compra até 2 consumíveis por visita do Comerciante e cada consumível comprado vem com +1 uso. Híbrido: armas de qualquer tipo de dano e alcance rendem 100%. Fraqueza: só 1 espaço de arma. | Mistura (1 vez por visita do Comerciante): junta 2 consumíveis num só, com os efeitos dos dois (bombas não entram). | Postura: sem bônus especial. |
| 🎯 Mosqueteiro | Recarregar: munição 3/3. Cada disparo gasta 1. Com a munição zerada, a postura defensiva recarrega a barra inteira (3/3). | Na mira (ação livre, recarga de 3 turnos seus): o próximo disparo ignora a Defesa e a postura do alvo e causa +2 de dano + 50% do dano físico das armas à distância. | Postura: se a munição estiver zerada, recarrega a barra inteira. |

## Resumo do catálogo

Quantos itens existem em cada fase do Comerciante (sem contar as poções fixas). Cada jogador vê 5 itens sorteados da fase da visita, com pelo menos 1 de cada tipo quando a fase tem.

| Fase | Armas | Armaduras | Joias | Itens ativos | Consumíveis | Total |
|---|---|---|---|---|---|---|
| Early | 5 | 2 | 4 | 0 | 5 | 16 |
| Mid | 6 | 4 | 8 | 4 | 4 | 26 |
| Late | 4 | 2 | 4 | 3 | 3 | 16 |
| **Total** | **15** | **8** | **16** | **7** | **12** | **58** |

### Armas por estilo

Cada personagem rende 100% com armas do seu alcance e do seu tipo de dano (o Alquimista, híbrido, com todas).

| Fase | Corpo a corpo físico | Corpo a corpo mágico | À distância físico | À distância mágico | Híbridas (físico+mágico) |
|---|---|---|---|---|---|
| Early | Espada de Aço, Machadinha, Manoplas do Saqueador | **nenhuma** | Besta Leve | Orbe Mágico | — |
| Mid | Lança Rúnica, Maça Estilhaçadora, Machado Sedento, Presa de Víbora | **nenhuma** | Arco Longo | Cajado Arcano | — |
| Late | Espada da Provação | **nenhuma** | Mosquete | Grimório Sombrio | Lâmina Lunar (corpo a corpo) |

### Personagens que cada estilo de arma atende

| Estilo de arma | Personagens que aproveitam 100% |
|---|---|
| Corpo a corpo físico | Bárbaro, Goblin, Ferreiro, Alquimista |
| Corpo a corpo mágico | Alquimista |
| À distância físico | Alquimista, Mosqueteiro |
| À distância mágico | Feiticeiro, Hemomante, Alquimista |

## Itens

Fases do Comerciante: Early até a rodada 9, Mid a partir da 10, Late a partir da 20. Por visita: 1 equipamento e 1 consumível (o Alquimista compra 2 consumíveis). Dano de item fora da afinidade do personagem rende 50%; arma de alcance diferente do personagem dá −1 no D10 de ataque.

### Poções fixas (sempre à venda)

| Item | Disponível | Preço | Efeitos |
|---|---|---|---|
| 🩹 Poção Simples | até a rodada 15 | 10 | 💚 Cura 15 de vida |
| 🧴 Poção Reforçada | a partir da rodada 20 | 20 | 💚 Cura 30 de vida |

### Armas (15)

| Item | Fase | Preço | Alcance | Tipo de dano | Efeitos |
|---|---|---|---|---|---|
| 🔪 Espada de Aço | Early | 25 | corpo a corpo | físico | 🔪 +4 de Dano |
| 🔮 Orbe Mágico | Early | 25 | à distância | mágico | 🌠 +4 de Dano |
| 🏹 Besta Leve | Early | 28 | à distância | físico | 🔪 +4 de Dano |
| 🪓 Machadinha | Early | 30 | corpo a corpo | físico | 🔪 +4 de Dano; 🎯 +1 na faixa de crítico |
| 🥊 Manoplas do Saqueador | Early | 30 | corpo a corpo | físico | 🔪 +3 de Dano; 🪙 +2 moedas por ataque |
| 🐍 Presa de Víbora | Mid | 46 | corpo a corpo | físico | 🔪 +3 de Dano; 🐍 Ataques envenenam (3 por turno do alvo, durante 3 turnos) |
| 🏹 Arco Longo | Mid | 50 | à distância | físico | 🔪 +5 de Dano; 🎯 +1 na faixa de crítico |
| 🔨 Maça Estilhaçadora | Mid | 50 | corpo a corpo | físico | 🔪 +5 de Dano; ⚡ Ignora 30% da Defesa do alvo |
| 🪓 Machado Sedento | Mid | 52 | corpo a corpo | físico | 🔪 +5 de Dano; 🩸 Cura 15% do dano causado |
| 🌟 Cajado Arcano | Mid | 55 | à distância | mágico | 🌠 +5 de Dano; ⚡ Ignora 25% da Defesa do alvo |
| 🔱 Lança Rúnica | Mid | 60 | corpo a corpo | físico | 🔪 +7 de Dano |
| 🌙 Lâmina Lunar | Late | 90 | corpo a corpo | híbrido | 🔪🌠 +7 de Dano (metade físico, metade mágico); 🎯 +2 na faixa de crítico |
| 📖 Grimório Sombrio | Late | 95 | à distância | mágico | 🌠 +7 de Dano; ⚡ Ignora 15% da Defesa do alvo; 🩸 Cura 15% do dano causado |
| 🔫 Mosquete | Late | 100 | à distância | físico | 🔪 +9 de Dano; ⚡ Ignora 40% da Defesa do alvo |
| ⚔️ Espada da Provação | Late | 120 | corpo a corpo | físico | 🔪 +9 de Dano; 🎯 +1 na faixa de crítico; ⚔️ Ignora a postura defensiva do alvo |

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
| 🛡️ Armadura da Provação | Late | 125 | 🔰 +4 de Defesa; 💖 +65 de Vida máxima; 🧠 Leitura de Combate: golpes críticos contra você contam como golpes normais; 🛡️ Última Provação: um golpe que mataria deixa você com 1 de vida (se estiver com pelo menos 5% da vida) e o seu próximo ataque é crítico garantido; recarrega a cada visita do Comerciante |

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
| 💍 Anel Venenoso | Late | 70 | — | 🐍 Ataques envenenam (4 por turno do alvo, durante 3 turnos); ⏳ Recarga de 3 turnos seus |
| 📿 Amuleto da Fortuna | Late | 75 | — | 💖 +20 de Vida máxima; 🎯 +2 na faixa de crítico; 🪙 +3 moedas por turno |
| 📿 Amuleto Arcano | Late | 80 | mágico | 🌠 +6 de Dano; 💖 +20 de Vida máxima |
| 📿 Amuleto do Vampiro | Late | 85 | — | 💖 +40 de Vida máxima; 🩸 Cura 20% do dano causado |

### Itens ativos (7)

| Item | Fase | Preço | Efeitos |
|---|---|---|---|
| 🧤 Luvas do Ladrão | Mid | 35 | 🧤 Rouba até 10 moedas de um oponente; 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 2 turnos seus |
| 🏺 Cálice Vital | Mid | 45 | 💚 Cura 20 de vida; ⏳ Recarga de 4 turnos seus |
| 🧿 Olho Protetor | Mid | 50 | 🧿 Escudo de 20 de dano até o seu próximo turno; 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 2 turnos seus |
| 📯 Chifre de Guerra | Mid | 55 | 💪 Próximo ataque causa ×2 de dano; 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 3 turnos seus |
| 👻 Capa da Invisibilidade | Late | 75 | 💪 Próximo ataque causa ×1.5 de dano; 👻 Invisível até o seu próximo turno (ninguém pode te escolher); 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 3 turnos seus |
| ⚡ Cajado Relâmpago | Late | 75 | ⚡ Raio de 16 de dano fixo (ignora Defesa e postura); ⏳ Recarga de 3 turnos seus |
| 👑 Coroa da Provação | Late | 80 | ⚖️ Marca um oponente: até o próximo turno dele, os ataques contra ele causam +45% de dano; 🆓 Ação livre (não gasta o turno); ⏳ Recarga de 4 turnos seus |

### Consumíveis (12)

| Item | Fase | Preço | Efeitos |
|---|---|---|---|
| 🌿 Antídoto | Early | 10 | 💚 Cura 10 de vida; 🌿 Remove veneno |
| 🔥 Poção de Fúria | Early | 20 | 💪 Próximo ataque causa ×2 de dano; 🆓 Ação livre (não gasta o turno) |
| 🧨 Bombinha | Early | 22 | 💣 10 de dano fixo (ignora Defesa e postura) |
| 🧪 Poção de Cura | Early | 24 | 💚 Cura 30 de vida |
| 🐍 Frasco de Veneno | Early | 24 | 🐍 Próximo ataque envenena (2 por turno do alvo, durante 3 turnos); 🆓 Ação livre (não gasta o turno) |
| 🍀 Trevo da Sorte | Mid | 18 | 🍀 +4 na rolagem do próximo ataque; 🆓 Ação livre (não gasta o turno) |
| 🧱 Pele de Pedra | Mid | 30 | 🧱 +4 de Defesa por 2 rodadas; 🆓 Ação livre (não gasta o turno) |
| 💣 Bomba de Pólvora | Mid | 34 | 💣 14 de dano fixo (ignora Defesa e postura) |
| 🍷 Elixir Maior | Mid | 40 | 💚 Cura 60 de vida |
| 🧪 Frasco de Ácido | Late | 38 | 🧪 Tira 3 de Defesa de um oponente por 3 turnos dele |
| 🦂 Essência de Escorpião | Late | 42 | 🐍 Próximo ataque envenena (4 por turno do alvo, durante 3 turnos); 🆓 Ação livre (não gasta o turno) |
| 🍶 Elixir Dourado | Late | 55 | 💚 Cura 55 de vida; 🌿 Remove veneno |
