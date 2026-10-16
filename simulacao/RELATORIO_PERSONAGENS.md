# Relatório: novos personagens (Hemomante, Alquimista, Mosqueteiro)

Data: 16/10/2026. Versão simulada: a atual da pasta local (7 personagens). A versão anterior está salva no GitHub na etiqueta `v2-antes-personagens`.

> Nada do que está aqui foi corrigido depois da simulação. Os pontos encontrados estão só destacados, para decidirmos juntos.

## Resumo

1. **O jogo roda do começo ao fim sem erros de código.** Das 6.000 partidas simuladas, 141 (2,4%) passaram de 150 rodadas sem vencedor. Nenhuma exceção, nenhum valor inválido de vida, ouro, mana, Fúria ou munição.
2. **As partidas estão longas demais: 55 rodadas em média com 4 jogadores**, com 93% passando de 30. **Isso começou antes das mudanças de hoje**: a versão de ontem (`v2`) já tinha 36 rodadas em média e 3% de partidas sem fim. O motivo é que **a cura por rodada está quase igual ao dano por turno**, e a morte súbita na rodada 35 não basta.
3. **Hemomante muito fraco:** vence 11% das partidas de 4 jogadores (o justo seria 25%) e só **13% dos duelos**. O Pacto de Sangue, usado em 1 de cada 3 turnos, custa mais vida do que rende.
4. **Alquimista forte em mesa cheia e fraco no 1 contra 1:** vence 31–37% com 4 a 6 jogadores, mas só 39% dos duelos. Ele se cura quase o dobro dos outros e quase não morre, mas é quem menos causa dano.
5. **Mosqueteiro no meio:** 20% com 4 jogadores, 1,13× o esperado com 5–6 e 35% nos duelos. Ele gasta muitos turnos recarregando, mas o Na mira dobra o dano do disparo.
6. **Goblin é o mais forte:** 37,5% com 4 jogadores e **79% dos duelos**. Em partidas longas o ouro extra pesa muito, e ele ainda termina com 111 moedas paradas.
7. **Brecha encontrada:** dá para misturar uma Mistura com outra coisa de novo em visitas seguintes, acumulando efeitos num único item.

## Como a simulação foi feita

- **Mesmo simulador** dos relatórios anteriores (`simulacao/simular.py`). Os robôs passam pelos mesmos menus que uma pessoa, agora incluindo as habilidades novas, a Mistura no Comerciante e a recarga do Mosqueteiro.
- **Escolha de alvo nova, como você pediu:**
  - se algum alvo está com 12% da vida ou menos, o robô ataca ele, para eliminar;
  - fora isso, mira em quem tem **mais vida** (45% das vezes) ou em quem tem **mais dano** (40%), e escolhe ao acaso no resto.
- **Como os robôs usam as habilidades:**
  - **Hemomante:** usa o Pacto sempre que vai atacar e está com mais de 40% da vida.
  - **Mosqueteiro:** usa o Na mira sempre que está pronto e tem munição, e assume a postura quando a munição zera.
  - **Bárbaro:** usa o Fôlego quando a Fúria está cheia e a vida abaixo de 45%.
  - **Alquimista:** compra mais consumíveis e faz a Mistura sempre que pode.
- **Cenários (6.000 partidas):**

  | Cenário | Partidas |
  |---|---|
  | 4 jogadores, personagens sorteados entre os 7, sem repetir | 3.600 |
  | Duelos (os 21 pares possíveis) | 1.428 |
  | 5–6 jogadores, personagens sorteados, podendo repetir | 972 |

- **Limites:** robôs não jogam como pessoas. Os números mostram tendências, não verdades. Os duelos têm cerca de 68 partidas por par, então cada porcentagem de par tem margem de erro de uns ±12 pontos.

Os números brutos ficam em `simulacao/resultados_personagens.json`. Para rodar de novo:

```bash
python simulacao/simular.py massa 6000 _personagens
```

## 1. Vitórias por personagem

### 4 jogadores (3.518 partidas que terminaram)

O justo seria 25%.

| Personagem | Vitórias nas partidas em que jogou | 1º eliminado | Cai em média na rodada |
|---|---|---|---|
| 👺 Goblin | **37,5%** | 14% | 40 |
| ⚗️ Alquimista | **31,5%** | 7% | **49** |
| 🪓 Bárbaro | 30,6% | 10% | 45 |
| 🔮 Feiticeiro | 24,6% | 15% | 40 |
| 🔨 Ferreiro | 20,4% | **30%** | **29** |
| 🎯 Mosqueteiro | 19,6% | 12% | 42 |
| 🩸 Hemomante | **11,0%** | 11% | 41 |

### 5–6 jogadores (925 partidas)

Vitórias divididas pelo esperado (1,00 = justo).

| Personagem | Atual | |
|---|---|---|
| Alquimista | **1,58×** | forte |
| Goblin | 1,29× | |
| Bárbaro | 1,25× | |
| Mosqueteiro | 1,13× | |
| Feiticeiro | 0,91× | |
| Hemomante | 0,51× | fraco |
| Ferreiro | **0,39×** | fraco |

### Duelos (1 contra 1)

Porcentagem de vitória nos duelos que cada um jogou: **Goblin 79%**, Ferreiro 65%, Bárbaro 64%, Feiticeiro 54%, Alquimista 39%, Mosqueteiro 35%, **Hemomante 13%**.

| Duelo | Vencedor | Duelo | Vencedor |
|---|---|---|---|
| Goblin × Hemomante | Goblin 96% | Bárbaro × Goblin | Goblin 69% |
| Bárbaro × Hemomante | Bárbaro 91% | Alquimista × Bárbaro | Bárbaro 69% |
| Feiticeiro × Hemomante | Feiticeiro 90% | Feiticeiro × Goblin | Goblin 71% |
| Ferreiro × Hemomante | Ferreiro 88% | Feiticeiro × Ferreiro | Ferreiro 71% |
| Goblin × Mosqueteiro | Goblin 84% | Bárbaro × Feiticeiro | Bárbaro 66% |
| Hemomante × Mosqueteiro | Mosqueteiro 82% | Ferreiro × Goblin | Goblin 66% |
| Alquimista × Ferreiro | Ferreiro 82% | Alquimista × Feiticeiro | Feiticeiro 63% |
| Alquimista × Goblin | Goblin 92% | Alquimista × Mosqueteiro | Alquimista 63% |
| Feiticeiro × Mosqueteiro | Feiticeiro 78% | Alquimista × Hemomante | Alquimista 75% |
| Bárbaro × Mosqueteiro | Bárbaro 76% | Bárbaro × Ferreiro | Bárbaro 52% |
| Ferreiro × Mosqueteiro | Ferreiro 69% | | |

## 2. Duração: o problema principal

| Versão | Média de rodadas (4 jogadores) | Mais de 30 rodadas | Partidas sem fim |
|---|---|---|---|
| `v2` (ontem, robôs antigos) | 36 | 50% | 3,3% |
| Atual, só os 4 personagens antigos, robôs com a mira antiga | 46 | 81% | 0,1% |
| Atual, só os 4 antigos, robôs com a mira nova | 50 | 89% | 0,1% |
| Atual, os 7 personagens, robôs com a mira antiga | 50 | 82% | 3,0% |
| **Atual, os 7 personagens, robôs com a mira nova** | **55** | **93%** | **2,4%** |

As variações de 1.500 partidas serviram só para separar as causas.

**O que a tabela mostra:**
- **A versão de ontem já estava longa.**
- **Mudanças de hoje:** o −1 no dado por arma de alcance diferente, o Fôlego e a Besta Leve somam cerca de 10 rodadas.
- **A mira nova dos robôs** (bater em quem tem mais vida) soma cerca de 5: o dano se espalha entre todos, e ninguém cai cedo.
- **Os 3 personagens novos** somam mais 5, principalmente pela cura do Alquimista.

**Por que ninguém morre:** por rodada viva, cada personagem cura em média **cerca de 5 de vida**:

| Fonte de cura | Por rodada |
|---|---|
| Comerciante | 2,4 |
| Poções e itens | 2,2 |
| Regeneração e roubo de vida | ~0,5 |

Ao mesmo tempo, **recebe cerca de 7 de dano**. Sobram só ~2 de dano líquido por rodada contra 110–120 de vida. A morte súbita (curas pela metade a partir da rodada 35) ajuda, mas vem tarde e é fraca.

## 3. Dano e habilidades

| Personagem | Dano por turno (média de todos os turnos) | Dano por ataque | % dos turnos atacando |
|---|---|---|---|
| Ferreiro | **7,2** | 12,1 | 59% |
| Feiticeiro | 5,9 | 10,5 | 56% |
| Bárbaro | 5,5 | 10,2 | 54% |
| Goblin | 5,4 | 11,0 | 50% |
| Mosqueteiro | 4,9 | **12,6** | **39%** |
| Hemomante | 4,8 | 9,3 | 52% |
| Alquimista | **4,0** | 8,4 | 48% |

- **Pacto de Sangue (Hemomante):** usado em **32,5%** dos turnos. Com o dano baixo dele (6 no começo), pagar 6 de vida por +50% raramente compensa, e o roubo de vida devolve só 1,3 por rodada.
- **Na mira (Mosqueteiro):** usado em 23,7% dos turnos, praticamente sempre que fica pronto. O disparo na mira tira **15,6** em média, contra 8,2 sem ela. A munição faz ele passar **29% dos turnos em postura** recarregando.
- **Fôlego de Batalha (Bárbaro):** usado em só 4% dos turnos, porque os robôs só usam com pouca vida e a Fúria cheia. Cura cerca de 1 de vida por rodada viva.
- **Mistura (Alquimista):** feita em cerca de 10% dos turnos dele, quase sempre juntando curas (Poção Simples + Poção Simples, Elixir Dourado + Elixir Dourado).
- **Fúria do Bárbaro:** só 1,7% dos ataques saem enfurecidos.
- **Arma de alcance diferente:** os robôs quase não compram, só 1–4% dos ataques, exceto o Goblin (12%). O −1 no dado funciona como desestímulo.

## 4. Curas por personagem (por rodada viva)

| Personagem | Total | Poções e itens | Comerciante | Roubo de vida | Outros |
|---|---|---|---|---|---|
| ⚗️ Alquimista | **9,4** | **6,6** | 2,4 | 0,2 | 0,2 |
| 👺 Goblin | 6,4 | 3,2 | 2,7 | 0,4 | 0,2 |
| 🪓 Bárbaro | 6,2 | 2,2 | 2,5 | 0,3 | 1,3 (Fôlego e regeneração) |
| 🩸 Hemomante | 5,5 | 1,6 | 2,3 | **1,3** | 0,3 |
| 🔮 Feiticeiro | 5,2 | 2,3 | 2,3 | 0,2 | 0,3 |
| 🔨 Ferreiro | 4,7 | 1,8 | 2,4 | 0,3 | 0,3 |
| 🎯 Mosqueteiro | 4,8 | 2,2 | 2,2 | 0,2 | 0,3 |

O Alquimista se cura quase o dobro dos outros, e é por isso que ele é o último a cair (rodada 49).

## 5. Ouro e Comerciante

- **Ouro ganho por rodada viva:** Goblin **19,8**; Alquimista 15,1; os outros entre 11,5 e 13,4. O Goblin ganha cerca de 1,55× os outros e ainda **termina com 111 moedas paradas**, contra cerca de 50 dos demais.
- **Compras por visita:** Goblin 1,6; Alquimista 1,4 (ele pode comprar 2 consumíveis); os outros cerca de 1,05.
- **Fases:** com partidas tão longas, **93% delas chegam ao Late**, e o item mais comprado é o **Elixir Dourado** (cura 70).
- **Itens ativos mais usados:** Olho Protetor (escudo), Capa da Invisibilidade e Cajado Relâmpago. São itens de defesa e de dano garantido, o que reforça o arrasto das partidas.

## 6. Bugs, brechas e inconsistências (não corrigidos)

| # | Problema | Situação |
|---|---|---|
| B1 | **Mistura de Mistura:** uma Mistura pode virar ingrediente de outra nas visitas seguintes, e os efeitos se acumulam num único item. Na simulação apareceram itens como "Mistura (Poção Reforçada + Mistura (Elixir Dourado + Poção Reforçada))". | **Nova.** Sugestão: uma Mistura não pode ser misturada de novo. |
| B2 | **Luvas do Ladrão** são ação livre, mas encerram o turno. | Continua (já estava no primeiro relatório). |
| B3 | **Bombas e Cajado Relâmpago** ignoram postura e Escudo de Mana sem consumi-los. | Continua; falta decidir se é intencional. |
| B4 | **Partidas sem fim:** 2,4%, mesmo com a morte súbita. | Continua (vem da duração). |

## 7. Desbalanceamentos

| # | Ponto | Evidência |
|---|---|---|
| D1 | **Duração** | 55 rodadas em média e 2,4% sem fim. A cura (~5 por rodada) quase anula o dano recebido (~7). |
| D2 | **Hemomante fraco** | 11% com 4 jogadores, 13% nos duelos, perde até para o Mosqueteiro (18%). Dano baixo, Pacto caro, poções pela metade. |
| D3 | **Alquimista cura demais** | 9,4 de cura por rodada; em mesa cheia vence 1,58× o esperado. Ao mesmo tempo é o que menos causa dano (4,0 por turno). |
| D4 | **Goblin forte** | 37,5% com 4 jogadores e 79% nos duelos. Ouro 1,55× mais o crítico ladrão, em partidas longas em que tudo do Late fica acessível para ele. |
| D5 | **Ferreiro cai cedo em mesa cheia** | 1º eliminado em 30% das partidas de 4 jogadores e 0,39× o esperado com 5–6, embora vença 65% dos duelos. |
| D6 | **Mosqueteiro perde muitos turnos** | Ataca em só 39% dos turnos, e 29% são postura para recarregar. É salvo pelo Na mira. |

## 8. Sugestões

1. **Duração primeiro**, porque mexe em tudo. Em ordem de impacto:
   - cura do Comerciante de 10% para **0–5%**;
   - **Elixir Dourado** de 70 para 45 de cura, ou o preço de 55 para 75;
   - **morte súbita mais cedo e mais forte:** a partir da rodada 25, curas a 50%, e a partir da 35 sem nenhuma cura;
   - se ainda ficar longo, +1 de dano para todos a cada visita do Comerciante depois da rodada 20 (a "arena esquenta").
2. **Hemomante:**
   - Pacto de Sangue custando **4** de vida, ou ×1,5 com o roubo de vida dobrado naquele ataque;
   - roubo de vida de 20% para **30%**;
   - poções a **75%** em vez de 50%.
3. **Alquimista:** escolher **só uma** das vantagens da bolsa (2 consumíveis por visita **ou** +1 uso), e proibir Mistura de Mistura (B1). Isso derruba a cura dele perto da média sem tirar a identidade.
4. **Goblin:** crítico ladrão de 4 para **2 moedas**, ou trocar o Pechinchar por outra coisa. Em partidas mais curtas (item 1) o ouro extra também pesa menos.
5. **Mosqueteiro:** está razoável. Se quiser deixá-lo mais fluido, a munição pode ir para **3/3**, ou a postura pode recarregar 1 mesmo sem a barra zerada.
6. **Ferreiro:** é o principal alvo nas mesas cheias. Uma opção é ele começar com uma armadura leve (+1 de Defesa, +10 de vida), que também pode forjar.
7. **Teste com pessoas:** a mira dos robôs sozinha mudou a duração em cerca de 5 rodadas. Vale conferir nas suas partidas se as pessoas realmente espalham o dano entre os mais fortes.
