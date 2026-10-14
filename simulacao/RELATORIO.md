# Relatório de simulação: Arena de Combate

Data: 14/10/2026. Versão do jogo: com a Fúria de 2 D10 (soma), o Escudo de Mana a 55% e o voltar/confirmar no turno.

> Nada do que está aqui foi corrigido no jogo. Os pontos encontrados estão só destacados, para decidirmos juntos o que mexer.

## Resumo

1. **O jogo roda do começo ao fim sem erros.** Foram 30.000 partidas simuladas (20.000 com as regras atuais e 10.000 com as anteriores), sem exceções, travamentos ou estados inválidos (vida, ouro, mana, Fúria e espaços de equipamento sempre dentro dos limites).
2. **O Bárbaro domina:** vence **55%** das partidas de 4 jogadores, quando o justo seria 25%. Ele já dominava antes da mudança (52% com a Fúria antiga). A Fúria de dois dados aumentou a vantagem, principalmente nos duelos (de 72% para 82% contra Goblin e Feiticeiro).
3. **O Feiticeiro está muito fraco (8%)**, e o Escudo de Mana a 55% quase não mudou isso (7,8% → 8,3%).
4. **A postura defensiva não expira quando o jogador age.** Quem assume a postura uma vez continua protegido enquanto ataca nos turnos seguintes, até ser atingido. **21% de todos os ataques** acertaram alguém em postura, e o dano desses ataques cai pela metade.
5. **Ouro sobra para todo mundo, e principalmente para o Goblin.** Com 1 compra por visita, o Goblin chega ao Comerciante com 132 moedas em média, sai com 103 e termina a partida com 180 moedas paradas. A identidade "ganancioso" quase não se converte em poder.
6. **Os itens Mid e Late quase nunca aparecem.** As partidas duram cerca de 20 rodadas, então 91% das visitas ao Comerciante são da fase Early. A fase Late aparece em só 1% das partidas.
7. **Bug confirmado:** as Luvas do Ladrão são item de ação livre, mas usá-las **encerra o turno**.

## Como a simulação foi feita

- O simulador está em `simulacao/simular.py`. Robôs respondem aos **mesmos menus que uma pessoa**, pelo `console.input` do `main.py`: escolha de raça, menu de ações, voltar no ataque, confirmações, inventário, alvos, Comerciante, substituição de item e Forja. Ou seja, o fluxo real do jogo foi usado, não uma cópia das regras.
- **Como os robôs jogam (heurística de "jogador comum"):**
  - Atacam na maior parte do tempo.
  - Escolhem o alvo assim: 60% das vezes o de menor vida, 25% o de mais dano e 15% ao acaso; tendem a evitar quem está em postura.
  - Assumem postura de vez em quando ou quando estão com pouca vida.
  - O Feiticeiro usa o Escudo de Mana quando está ferido e assume postura quando fica sem mana.
  - Usam poções de cura quando estão com pouca vida, buffs antes de atacar, e Bombas e Raios em alvos fracos.
  - No Comerciante, compram o melhor item que conseguem pagar (preferindo melhorias de equipamento) e substituem o pior item quando o espaço está cheio. O Ferreiro sempre usa a Forja.
  - Às vezes agem como pessoas indecisas: abrem o ataque e voltam (3% dos turnos) ou cancelam uma confirmação (2%).
- **Cenários:**

  | Cenário | Partidas (regras atuais) | Partidas (regras antigas) |
  |---|---|---|
  | 4 jogadores, uma raça de cada | 12.000 | 6.000 |
  | Duelos (todos os pares de raças, sem espelho) | 4.800 | 2.400 |
  | 5–6 jogadores com raças sorteadas (pode repetir) | 3.200 | 1.600 |

- "Regras antigas" significa Fúria com 1 dado e +50% de dano, e Escudo de Mana a 40%. Serve para separar o efeito das mudanças de hoje.
- **Limites dos robôs (leia antes de tirar conclusões):**
  - Focar no alvo de menor vida favorece raças com mais vida, como o Bárbaro (120). Os **duelos** não têm esse viés, e lá o Bárbaro também domina.
  - Os robôs quase nunca compram consumíveis, porque com só 1 compra por visita um item permanente quase sempre vale mais.
  - Eles não fazem jogadas de longo prazo (poupar ouro, combinar itens, contra-atacar uma build).

  Os números mostram tendências fortes, mas não substituem partidas de teste com pessoas.

Para rodar de novo (na pasta do projeto):

```bash
python simulacao/simular.py teste
```

```bash
python simulacao/simular.py massa 20000
```

```bash
python simulacao/simular.py antigas 10000
```

O modo `teste` joga 2 partidas e salva a tela completa em `simulacao/partida_teste_1.txt` e `partida_teste_2.txt`. Os números brutos ficam em `simulacao/resultados.json` e `resultados_regras_antigas.json`.

## 1. Vitórias por raça

### 4 jogadores (uma de cada), 12.000 partidas

| Raça | Vitórias (atual) | Vitórias (regras antigas) | 1º eliminado |
|---|---|---|---|
| 🪓 Bárbaro | **55,0%** ±0,9 | 52,1% | 7,6% |
| 👺 Goblin | 23,9% ±0,8 | 26,4% | 24,1% |
| 🔨 Ferreiro | 12,8% ±0,6 | 13,7% | 36,2% |
| 🔮 Feiticeiro | **8,3%** ±0,5 | 7,8% | 32,1% |

O justo seria 25% para cada. O "±" é a margem de 95% de confiança.

### 5–6 jogadores (raças sorteadas), 3.200 partidas

A medida aqui é vitórias divididas pelo esperado (1,00 = justo; considera quantas vezes cada raça apareceu e o tamanho da mesa).

| Raça | Atual | Antigas |
|---|---|---|
| Bárbaro | **1,96×** | 1,84× |
| Goblin | 1,12× | 1,23× |
| Ferreiro | 0,57× | 0,59× |
| Feiticeiro | **0,36×** | 0,35× |

Com 5 ou 6 jogadores o Goblin **não** ficou fraco nesta versão (o Readme antigo dizia cerca de 5%). Ele aparece levemente acima do justo.

### Duelos (1 contra 1), 800 partidas por par

| Duelo | Atual | Antigas |
|---|---|---|
| Bárbaro × Goblin | **Bárbaro 82%** | 72% |
| Bárbaro × Feiticeiro | **Bárbaro 83%** | 74% |
| Bárbaro × Ferreiro | Bárbaro 69% | 60% |
| Ferreiro × Goblin | Ferreiro 62% | 60% |
| Feiticeiro × Goblin | Goblin 52% | 57% |
| Feiticeiro × Ferreiro | Ferreiro 65% | 67% |

Nos duelos não existe o viés de escolha de alvo, e mesmo assim o Bárbaro vence 3 de cada 4. **A Fúria de dois dados somou cerca de 10 pontos percentuais em cada duelo do Bárbaro.**

## 2. Duração das partidas

| Cenário | Média | Mediana | 10% mais curtas | 10% mais longas | Mais de 30 rodadas |
|---|---|---|---|---|---|
| 4 jogadores | 20,2 | 20 | 16 | 24 | 1,8% |
| 5–6 jogadores | 22,2 | 21 | 18 | 27 | 4,0% |
| Duelos | 16,5 | 16 | 13 | 20 | 0,4% |

- A meta de partidas curtas está cumprida: cerca de 20 rodadas, contra mais de 30 na versão inicial.
- As partidas são disputadas: em **62%** delas o vencedor termina com 25% da vida ou menos (72% nos duelos).

## 3. Dano dos ataques

Considerando todos os ataques das regras atuais (cerca de 1 milhão):

| Tipo de golpe | Frequência | Multiplicador médio | Dano bruto médio | Dano final médio (vida tirada) | Maior dano bruto |
|---|---|---|---|---|---|
| 💨 Golpe Fraco | 28,1% | ×0,5 | 4,3 | **3,2** | 22 |
| 🔪 Golpe Normal | 44,8% | ×1,0 | 8,3 | **6,5** | 46 |
| 💥 Golpe Crítico | 20,7% | ×2,0 | 17,4 | **13,5** | 93 |
| 🔥 Fúria (2 D10) | 6,3% | ×2,15 | 17,8 | **12,4** | 88 |

- O dano **bruto** é o calculado antes da postura, do Escudo de Mana, da Defesa e dos escudos. O dano **final** é a vida que o alvo realmente perdeu.
- A taxa de crítico real é 20,7%, um pouco acima dos 20% do dado, por causa dos itens de crítico.

### Fúria

- **Um em cada 4,4 ataques do Bárbaro (22,5%) sai com a Fúria cheia.** A postura também enche a barra, o que acelera esse ritmo.
- **Distribuição do multiplicador total da Fúria:**

  | Multiplicador | Combinação dos dados | Frequência |
  |---|---|---|
  | ×1,0 | fraco + fraco | 9,0% |
  | ×1,5 | fraco + normal | 28,8% |
  | ×2,0 | normal + normal | 22,7% |
  | ×2,5 | fraco + crítico | 13,5% |
  | ×3,0 | normal + crítico | 20,8% |
  | ×4,0 | crítico + crítico | 5,3% |

- **A Fúria nova vale ×2,15 em média, contra ×1,61 da antiga (+34%).** Na média, o ataque com Fúria agora vale tanto quanto um crítico, e acontece além dos críticos normais.
- No conjunto, o ataque médio do Bárbaro vale cerca de ×1,32 do dano base. Nas outras raças vale ×1,05.

### Dano médio por ataque, por raça (vida tirada)

| Raça | Por ataque | Fraco | Normal | Crítico | Fúria |
|---|---|---|---|---|---|
| Feiticeiro | **8,0** | 4,0 | 7,4 | 15,0 | — |
| Bárbaro | 7,9 | 2,9 | 6,1 | 12,5 | 12,4 |
| Ferreiro | 7,3 | 3,2 | 6,6 | 14,1 | — |
| Goblin | 6,6 | 2,9 | 6,1 | 12,5 | — |

O Feiticeiro é quem bate mais forte por golpe (penetração mais o dano mágico inicial de 7), mas ataca bem menos: 68% dos turnos, contra 80% das outras raças, porque gasta turnos com o Escudo de Mana e com a postura para recuperar mana. Somando isso à menor vida (110), ele perde.

### Outros números de dano

- **Ataques contra quem está em postura:** 4,1 de dano final em média, contra 8,3 sem postura.
- **O dano quase não cresce durante a partida:** 7,3 nas rodadas 1–10, 7,6 nas 11–20 e 7,4 nas 21–30. A progressão por itens é pequena (veja a seção 5).
- **Cajado Relâmpago:** 12,5 de dano médio (o nominal é 16; o escudo do Olho Protetor absorve uma parte).

## 4. Ações por raça (% dos turnos)

| Raça | Ataque | Postura | Escudo de Mana | Item que gasta o turno | Passar |
|---|---|---|---|---|---|
| Bárbaro | 80,0% | 17,2% | — | 0,8% | 0,8% |
| Goblin | 79,7% | 17,7% | — | 0,6% | 0,8% |
| Ferreiro | 79,8% | 18,5% | — | 0,2% | 0,8% |
| Feiticeiro | 68,5% | 15,8% | 13,8% | 0,4% | 0,7% |

Itens de ação livre foram usados em cerca de 1% dos turnos, sem encerrar a vez.

## 5. Comerciante e ouro (foco no Goblin)

### Ouro ganho e gasto por partida (média por jogador)

| Fonte | Bárbaro | Goblin | Ferreiro | Feiticeiro |
|---|---|---|---|---|
| Turno (5 por turno) | 92,4 | 86,7 | 80,3 | 82,0 |
| Comerciante (+10 por visita) | 31,3 | 29,5 | 27,1 | 27,9 |
| Críticos | 24,8 | 18,7 | 17,0 | 14,8 |
| Manoplas do Saqueador | 8,3 | 6,6 | 5,6 | 4,1 |
| Defesa perfeita | 1,7 | 1,7 | 1,7 | 1,5 |
| Itens de ouro por turno | 0,9 | 3,8 | 0,4 | 0,3 |
| Goblin: +5 por turno | — | **86,7** | — | — |
| Goblin: postura | — | **15,6** | — | — |
| Goblin: +5 no Comerciante | — | **14,8** | — | — |
| Goblin: economia do Pechinchar | — | 4,4 | — | — |
| **Total ganho (aprox.)** | **160** | **264** | **132** | **131** |
| **Gasto no Comerciante** | **95** | **85** | **80** | **82** |
| Parado no fim ou na eliminação | 64 | **180** | 52 | 49 |

### Visitas ao Comerciante

| Raça | Ouro na chegada | Comprou | Preço médio pago | Ouro na saída |
|---|---|---|---|---|
| Bárbaro | 60 | 99,8% | 30 | 30 |
| **Goblin** | **132** | 100% | 29 | **103** |
| Ferreiro | 54 | 99,9% | 29 | 25 |
| Feiticeiro | 54 | 99,8% | 29 | 24 |

### O que isso mostra

- **O Goblin ganha o dobro de ouro, mas gasta o mesmo que os outros.** Ele usa só 32% do que ganha; as outras raças usam cerca de 60%. O limite de 1 compra por visita é o gargalo: o ouro extra vira um número parado na tela.
- **O Pechinchar quase não importa:** dispara em 34,9% das compras (o valor configurado é 35%, então funciona) e economiza 4,4 moedas por partida. Além disso, a regra "depois do desconto fica desabilitado até a próxima visita" nunca faz diferença, porque só há 1 compra por visita.
- **Para todos, o ouro deixa de ser recurso escasso.** Quase toda visita termina em compra (99,8%), e quase nunca falta ouro para algum item do estoque (0,2%). Ouro de crítico, de Manoplas, de Anel do Lucro e de defesa perfeita pouco muda o resultado. **As Manoplas do Saqueador e o Anel do Lucro estão entre os itens mais comprados e entre os de menor taxa de vitória do dono**, porque dão ouro que não tem onde ser gasto.
- **O teto de progressão é baixo:** cada jogador faz em média só cerca de 3 compras por partida (uma a cada 5 rodadas).

### Fases do estoque

| Fase | Visitas |
|---|---|
| Early | 91,5% |
| Mid | 7,9% |
| Late | 0,6% |

- Só **46%** das partidas chegam à primeira visita Mid (rodada 20), e **1%** chegam à Late (rodada 35).
- Como as partidas duram cerca de 20 rodadas, os limites de fase (Early até a rodada 15, Mid até a 30) fazem com que **quase metade do catálogo nunca apareça** na prática: todos os itens Late e boa parte dos Mid.

## 6. Itens

- **Mais comprados:** Armadura de Couro, Manoplas do Saqueador, Machadinha, Orbe Mágico, Gibão Acolchoado e Espada de Aço (todos Early).
- **Nunca comprados pelos robôs:** Antídoto, Trevo da Sorte, Poção de Fúria, Bombinha, Pele de Pedra e Bomba de Pólvora. Parte disso é limitação dos robôs, mas a estrutura também pesa: com 1 compra a cada 5 rodadas, um consumível de uso único dificilmente vale mais que um item permanente.
- **Itens ativos mais usados:** Olho Protetor (7.974 usos), Cálice Vital (5.074) e Chifre de Guerra (4.323).
- **Taxa de vitória de quem tinha o item no fim** (é correlação, não causa, porque depende de quem compra):

  | Item | Taxa de vitória do dono |
  |---|---|
  | 🧿 Olho Protetor | **55,8%** |
  | 🪓 Machado Sedento | 51,7% |
  | 💍 Anel da Fúria | 51,4% |
  | 📯 Chifre de Guerra | 48,7% |
  | 🔮 Orbe Mágico | 23,7% |
  | 🧤 Luvas do Ladrão | **13,6%** |
  | 📖 Livro velho (item inicial do Feiticeiro) | **6,1%** |

  O Olho Protetor é forte: um escudo de 20 de vida a cada 2 rodadas, como ação livre.

## 7. Bugs encontrados (não corrigidos)

| # | Problema | Onde | Como apareceu na simulação |
|---|---|---|---|
| B1 | **Luvas do Ladrão encerram o turno**, embora sejam "ação livre" (a descrição diz "sem nem parar de lutar"). `mostrar_inventario` devolve `encerra_turno=True` para todo item com alvo, sem olhar a flag `livre`. | `main.py`, `mostrar_inventario` | 1.199 usos, e todos encerraram o turno. |
| B2 | **A postura não expira quando o jogador age.** `assumir_postura` liga a postura e ela só é desligada quando o jogador é atingido. Quem assume a postura e depois ataca por vários turnos continua protegido, com bloqueio e reflexo de 75%. | `main.py`, `executar_ataque` e `assumir_postura` | 180 mil ataques foram feitos por jogadores ainda em postura; 21% dos ataques acertaram alguém em postura. |
| B3 | **Bombinha, Bomba de Pólvora e Cajado Relâmpago** ignoram a postura e o Escudo de Mana, mas não os consomem, então a defesa continua guardada para o próximo ataque. Pode ser intencional; vale decidir. | `main.py`, `dano_direto` | 51 casos (esses itens são pouco usados). |

## 8. Contradições e inconsistências

| # | Ponto |
|---|---|
| C1 | **Mestre do Metal e Forja valem para armas mágicas.** Os textos dizem "itens de combate físico" (`shop.EQUIPAVEIS`, mensagem da Forja e descrição do Ferreiro), mas o código aceita qualquer arma. Na partida de teste o Ferreiro forjou um 🔮 Orbe Mágico. |
| C2 | **Penetração mágica para qualquer raça.** O Readme antigo dizia que só o Feiticeiro tinha penetração racial; o código e a tela de raças aplicam a qualquer dano mágico. O README novo já descreve o comportamento do código, mas a decisão de design continua em aberto. |
| C3 | **A regra do Pechinchar "desabilitado até a próxima visita" é inútil** com 1 compra por visita (e `fase_loja` reativa o Pechinchar de qualquer forma). |
| C4 | **Fúria com dois críticos dá o bônus de ouro duas vezes (+12),** e o Trevo da Sorte soma +4 nos dois dados. São efeitos da regra nova; vale confirmar se é o desejado. |
| C5 | **O nível da Forja aparece calculado com `5` fixo** (`round(forja * 5)`) em 3 lugares do `main.py`, em vez de usar `shop.BONUS_FORJA`. Se o bônus mudar, a tela mostra o valor errado. |
| C6 | **Cabeçalho do Comerciante cortado:** com o terminal em cerca de 110 colunas, a linha de espaços sai como "Joias 0/…". É só visual e depende da largura do terminal. |
| C7 | **A `.venv` da pasta não tem o `rich`** (ele foi instalado no Python global). Se o VS Code ou o terminal ativar a `.venv`, `python main.py` falha com `ModuleNotFoundError: No module named 'rich'`. |

## 9. Desbalanceamentos

| # | Ponto | Evidência |
|---|---|---|
| D1 | **Bárbaro forte demais** | 55% em 4 jogadores, 69–83% nos duelos, primeiro eliminado em só 7,6% das partidas. As causas somadas: mais vida (120), Fúria frequente (22,5% dos ataques, enchida também pela postura) e Fúria de dois dados valendo ×2,15. |
| D2 | **Feiticeiro fraco demais** | 8% em 4 jogadores. Ataca em menos turnos por causa da mana, tem menos vida, e o Escudo de Mana a 55% quase não mudou o resultado (+0,5 ponto). O Livro velho (item inicial) tem a pior taxa de vitória de todos os itens. |
| D3 | **Ferreiro abaixo do justo** | 12,8%, e é o primeiro eliminado com mais frequência (36%). O bônus de 10% e a Forja (+5% por visita) pesam pouco com só cerca de 3 compras por partida. |
| D4 | **A postura vale demais** | Ela fica ativa sem custo até o jogador ser atingido (B2), corta o dano pela metade e reflete 75% do que bloqueou. |
| D5 | **Ouro sem uso** | O Goblin acumula 180 moedas paradas, e todos saem do Comerciante com sobra. Itens de ouro (Manoplas, Anel do Lucro, Luvas do Ladrão, Amuleto da Fortuna) são armadilhas: ocupam um espaço e dão um recurso que não vira poder. |
| D6 | **Catálogo Mid e Late inacessível** | As fases (15 e 30) foram pensadas para partidas de mais de 30 rodadas, e hoje elas duram cerca de 20. |
| D7 | **Consumíveis sem espaço na economia** | Com 1 compra por visita, eles competem com equipamento permanente. |
| D8 | **Olho Protetor forte** | 55,8% de vitória do dono, e é o ativo mais usado. |

## 10. Perguntas para decidirmos os próximos passos

1. A postura deve acabar quando o jogador age (ataca ou usa um item), no início do próximo turno dele, ou continuar como está?
2. O Bárbaro precisa de um ajuste além da Fúria? Por exemplo: menos vida, a postura deixar de encher a Fúria (já está na lista "em espera"), ou a Fúria contar o melhor dado em vez da soma.
3. O Goblin e o ouro: liberar mais compras por visita para quem tiver ouro, criar algo para gastar ouro fora do Comerciante, ou reduzir a renda?
4. Os limites de fase devem acompanhar a duração real (por exemplo, Mid a partir da rodada 10 e Late a partir da 20)?
5. O Feiticeiro precisa de um ajuste de base (vida, regeneração de mana ou custo do ataque), já que o Escudo de Mana não resolveu?
