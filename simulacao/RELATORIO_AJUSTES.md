# Relatório dos ajustes de balanceamento

Data: 14/10/2026. Compara a versão ajustada com a do primeiro relatório (`RELATORIO.md`, chamada aqui de **"antes"**).

## O que mudou no jogo

| Ajuste | Antes | Agora |
|---|---|---|
| Postura defensiva | durava até o jogador ser atingido, mesmo que ele atacasse nesse meio tempo | termina na próxima vez do jogador (ou quando ele é atingido) |
| Fúria do Bárbaro | enchia em 3 ataques; a postura também enchia | enche em **4 ataques**; a postura não enche |
| Ouro do Goblin | 2x o das outras raças (+5 por turno) | **1,5x** (+2,5 por turno em média, alternando +2 e +3; +5 no Comerciante) |
| Compras por visita | 1 | **2** |
| Dano do Feiticeiro | mágico 4 (ataque inicial 7) | mágico 6 (**ataque inicial 9**) |
| Penetração mágica | 50% da Defesa | **75%** |
| A Forja (Ferreiro) | +5% por nível (máx. +15%) | **+15% por nível** (máx. +45%) |
| Fases do Comerciante | Mid na rodada 20, Late na 35 | **Mid na rodada 10, Late na 20** |

Também foram ajustados os textos ligados a essas regras: descrições das raças, o menu de postura, o aviso "sua postura defensiva terminou" e o nível da Forja, que antes aparecia calculado com 5% fixo.

### Como a decisão das fases foi tomada

Com os outros ajustes já aplicados, uma simulação pequena (2.000 partidas) mostrou que só **43%** das partidas viam a fase Mid e **3,5%** a Late. Como continuava baixo, as fases foram mudadas para Mid na rodada 10 e Late na 20.

### Verificação

- Cada regra nova foi testada isoladamente:
  - o Feiticeiro começa com 9 de dano;
  - a postura não enche a Fúria e termina na vez do jogador;
  - a Fúria enche em 4 ataques e o 5º ataque rola 2 dados;
  - o Goblin recebe 7, 8, 7, 8 por turno;
  - o Comerciante permite 2 compras;
  - a Forja dá +15%.
- Duas partidas completas com a interface renderizada (`partida_teste_1.txt` e `partida_teste_2.txt`) terminaram normalmente.
- **10.000 partidas simuladas, sem nenhum erro ou travamento.** O problema da postura que não expirava sumiu: zero ocorrências, contra 180 mil antes.

Os robôs são os mesmos do primeiro relatório, com os mesmos limites. Em especial, preferem atacar quem tem menos vida, o que favorece raças com mais vida nas partidas com 3 ou mais jogadores.

## Vitórias por raça

### 4 jogadores (uma de cada), 6.000 partidas

O justo seria 25% para cada.

| Raça | Antes | Agora | 1º eliminado (agora) |
|---|---|---|---|
| 🪓 Bárbaro | 55,0% | **40,0%** ±1,2 | 10,2% |
| 👺 Goblin | 23,9% | **35,1%** ±1,2 | 20,2% |
| 🔮 Feiticeiro | 8,3% | **14,6%** ±0,9 | 25,7% |
| 🔨 Ferreiro | 12,8% | **10,3%** ±0,8 | **43,9%** |

### 5–6 jogadores (raças sorteadas), 1.600 partidas

Vitórias divididas pelo esperado (1,00 = justo).

| Raça | Antes | Agora |
|---|---|---|
| Bárbaro | 1,96× | **1,58×** |
| Goblin | 1,12× | **1,42×** |
| Feiticeiro | 0,36× | **0,52×** |
| Ferreiro | 0,57× | **0,49×** |

### Duelos (1 contra 1), 400 partidas por par

| Duelo | Antes | Agora |
|---|---|---|
| Bárbaro × Goblin | Bárbaro 82% | **Goblin 56%** |
| Bárbaro × Feiticeiro | Bárbaro 83% | **Feiticeiro 57%** |
| Bárbaro × Ferreiro | Bárbaro 69% | Bárbaro 60,5% |
| Feiticeiro × Goblin | Goblin 52% | Feiticeiro 58,5% |
| Ferreiro × Goblin | Ferreiro 62% | **Goblin 63%** |
| Feiticeiro × Ferreiro | Ferreiro 65% | **Feiticeiro 68,5%** |

Nos duelos, a taxa de vitória das partidas em que cada raça jogou ficou assim: Feiticeiro 61%, Goblin 54%, Bárbaro 49% e Ferreiro 36%.

### Leitura

- **O Bárbaro deixou de ser absoluto.** Nos duelos ele está no ponto justo (49%). Nas mesas maiores ainda lidera (40%), em parte pela vida de 120 somada à tendência dos robôs de focar o mais fraco.
- **O Goblin virou o segundo mais forte.** Agora o ouro dele se converte em itens, porque em 49% das visitas ele faz as 2 compras; as outras raças fazem 2 compras em só 5–6% das visitas.
- **O Feiticeiro melhorou bastante:** 8% → 15% em 4 jogadores, e é o mais forte nos duelos. É forte em 1 contra 1 e fraco em mesa cheia, onde é focado por ter pouca vida.
- **O Ferreiro piorou e é agora a raça mais fraca:** 10%, primeiro eliminado em 44% das partidas, 36% nos duelos. A Forja mais forte não compensou, porque ela melhora só os números do item, que são pequenos. Uma arma de +4 forjada 3 vezes vira cerca de +6.

## Duração das partidas

| Cenário | Média antes | Média agora | Mediana | 10% mais curtas / 10% mais longas | Mais de 30 rodadas |
|---|---|---|---|---|---|
| 4 jogadores | 20,2 | **23,2** | 21 | 16 / 33 | **12,3%** (antes 1,8%) |
| 5–6 jogadores | 22,2 | **26,9** | 24 | 18 / 38 | **22,2%** (antes 4,0%) |
| Duelos | 16,5 | 16,8 | 15 | 11 / 23 | 3,4% |

As partidas ficaram cerca de 3 rodadas mais longas, porque nenhuma raça atropela as outras. Também ficaram menos apertadas no final: o vencedor termina com 25% da vida ou menos em 44% das partidas, contra 62% antes. Com 5–6 jogadores, uma em cada 5 partidas passa de 30 rodadas.

## Dano dos ataques

| Tipo de golpe | Frequência | Dano final médio antes | Dano final médio agora | Dano bruto médio agora |
|---|---|---|---|---|
| 💨 Fraco | 28,8% | 3,2 | **3,8** | 4,6 |
| 🔪 Normal | 45,5% | 6,5 | **7,9** | 9,3 |
| 💥 Crítico | 21,2% | 13,5 | **16,0** | 19,4 |
| 🔥 Fúria (2 D10) | 4,6% | 12,4 | **14,5** | 19,0 |

- A Fúria agora acontece em **16%** dos ataques do Bárbaro (antes 22,5%). O multiplicador médio dela continua ×2,15.
- **Dano médio por ataque, por raça:** Feiticeiro **10,4** (antes 8,0), Goblin 8,5, Bárbaro 8,2 e Ferreiro 7,9.
- **O dano agora cresce durante a partida:** 8,0 nas rodadas 1–10, 9,7 nas 11–20, 10,0 nas 21–30 e 11,6 depois. Antes ficava parado em cerca de 7,4. É efeito das 2 compras e das fases mais cedo.
- **Postura:** 10,5% dos ataques acertaram alguém em postura (antes 21%), e o dano desses ataques continua caindo pela metade (4,6 contra 9,2).

## Comerciante e ouro

| Raça | Ouro ganho por rodada viva | Ouro na chegada | Compras por visita | Visitas com 2 compras | Visitas sem nada que pudesse pagar | Ouro parado no fim |
|---|---|---|---|---|---|---|
| Goblin | **12,7** | 75 | **1,47** | **48,6%** | 1,3% | 45 (antes 180) |
| Bárbaro | 8,3 | 50 | 0,91 | 5,1% | 13,9% | 34 |
| Ferreiro | 7,8 | 47 | 0,96 | 5,9% | 9,4% | 27 |
| Feiticeiro | 7,7 | 47 | 0,94 | 6,4% | 12,3% | 29 |

- **Só o ouro de turno do Goblin é exatamente 1,5x** o das outras raças. No total, ele ganha **1,6x** por rodada viva, porque soma o +5 da postura, o Pechinchar e itens de ouro.
- **O ouro deixou de sobrar,** e agora existe escolha: as raças que não são Goblin às vezes não conseguem pagar nada (10–14% das visitas, porque os itens Mid e Late são mais caros).
- **A 2ª compra quase só acontece para o Goblin,** o que explica a subida dele.
- **Fases:** 99% das partidas veem a fase Mid e **47%** veem a Late (antes 46% e 1%). Em 4 jogadores são 52,5%; com 5–6 jogadores, 74%; nos duelos, 16%. As visitas ficaram divididas assim: Early 31%, Mid 50% e Late 19%.
- **O Ferreiro termina a partida com 2,5 níveis de Forja em média,** somando todos os itens dele.

## Itens

- **Nunca comprados:** Poção de Fúria, Frasco de Veneno e Bombinha.
- **Maior taxa de vitória do dono:** os itens Late (Grimório Sombrio 53%, Mosquete 52%, Amuleto Arcano 51%), que agora aparecem de verdade.
- **Pior taxa:** 🧤 Luvas do Ladrão (13%; veja o bug abaixo), 🔨 Martelo desgastado (13%, Ferreiro que não trocou a arma inicial) e 📖 Livro velho (20%, antes 6%).

## Bugs e inconsistências que continuam

| # | Problema | Situação |
|---|---|---|
| B1 | **As Luvas do Ladrão encerram o turno** embora sejam ação livre. | Continua. Agora é bem mais frequente (13.941 usos), porque com 2 compras elas são mais compradas. |
| B2 | Postura persistente enquanto o jogador ataca. | **Resolvido** pelo ajuste da postura. |
| B3 | Bombas e Cajado Relâmpago ignoram a postura e o Escudo de Mana sem consumi-los. | Continua (833 casos). Falta decidir se é intencional. |
| C1 | Mestre do Metal e Forja valem para armas mágicas, mas os textos dizem "combate físico". | Continua. |
| C2 | A penetração mágica (agora 75%) vale para a parte mágica do dano de **qualquer raça**, não só do Feiticeiro. Por isso o aumento também fortaleceu quem compra armas mágicas. | Continua; é decisão de design. |
| C4 | Fúria com dois críticos dá ouro em dobro, e o Trevo da Sorte soma nos dois dados. | Continua; falta confirmar se é o desejado. |
| C5 | Nível da Forja aparecia com 5% fixo. | **Resolvido** (agora usa o valor real). |
| C6 | Cabeçalho do Comerciante cortado em terminais estreitos. | Continua (só visual). |
| C7 | A `.venv` da pasta não tem o `rich`. | Continua (problema do ambiente, não do jogo). |

## Sugestões para a próxima rodada

1. **Ferreiro (prioridade):** a Forja só multiplica números pequenos, então rende pouco. Alternativas, da mais simples para a mais forte:
   - a Forja dá um valor fixo por nível (por exemplo, +1 de dano em arma e +1 de Defesa e +10 de vida em armadura), além do percentual;
   - 2 usos da Forja por visita, ou até 5 níveis por item;
   - Mestre do Metal de 10% para 20%;
   - vida inicial de 110 para 120, já que ele é o primeiro eliminado em 44% das partidas.
2. **Goblin:** agora está acima do justo (35% em 4 jogadores). Para manter o ouro dele em exatos 1,5x, dá para tirar o +5 de ouro da postura e trocar por outro bônus de postura. Outra opção é limitar a 2ª compra a itens Early, ou cobrar uma taxa de 10% na 2ª compra.
3. **Bárbaro:** está justo nos duelos e ainda forte nas mesas maiores (40%). Um ajuste leve seria a vida de 120 para 115. Antes de mexer, vale ver se pessoas reais também focam o jogador mais fraco, como os robôs.
4. **Feiticeiro:** está bem nos duelos (61%) e fraco em mesa cheia (15%). Um ajuste que ajuda sem fortalecer o duelo seria o Escudo de Mana durar até o próximo turno dele, protegendo contra todos os ataques da rodada, em vez de só o primeiro.
5. **Duração:** com 5–6 jogadores, 22% das partidas passam de 30 rodadas. Se incomodar, as opções são reduzir o reflexo da postura (75% → 50%), o que acelera o combate, ou dar +1 de dano base a todas as raças.
6. **Itens-armadilha:** consertar as Luvas do Ladrão (B1) e repensar itens que só dão ouro, como as Manoplas e as Luvas, que têm as menores taxas de vitória.
7. **Consumíveis:** Poção de Fúria, Frasco de Veneno e Bombinha nunca são comprados. Baixar o preço ou fazer o pacote vir com 2 usos daria motivo para comprá-los.
8. **Penetração mágica:** decidir se os 75% devem ser só do Feiticeiro (C2). Hoje qualquer raça com arma mágica aproveita.
9. **Partidas com pessoas:** os números estão em uma faixa razoável (todas as raças entre 10% e 40%). O próximo passo mais útil é jogar algumas partidas reais para ver se as sensações batem com a simulação.

## Arquivos

- `simulacao/resultados_ajustes.json`: números brutos destas 10.000 partidas.
- `simulacao/resultados_pequena.json`: simulação pequena, feita antes de mudar as fases.
- `simulacao/resultados.json` e `resultados_regras_antigas.json`: dados do primeiro relatório.
- Para rodar de novo:

```bash
python simulacao/simular.py massa 10000 _nome
```
