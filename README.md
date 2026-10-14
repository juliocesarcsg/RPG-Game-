# Arena de Combate

RPG PvP de terminal, em turnos, escrito em Python. De 2 a 6 jogadores se revezam no mesmo teclado (hot-seat) até sobrar um vivo.

> A versão original (antes dos ajustes de balanceamento) está guardada na etiqueta [`v1-original`](https://github.com/juliocesarcsg/RPG-Game-/tree/v1-original) do repositório. Para rodá-la localmente: `git checkout v1-original`.

## Como rodar

```bash
pip install rich
python main.py
```

Use um terminal com suporte a emoji e cores (Windows Terminal, terminal do VS Code etc.).

## Foco do jogo

- **Liberdade de build:** qualquer raça pode montar o personagem que quiser pelas compras. Armas e joias físicas ou mágicas, armaduras, itens ativos, poções e venenos são abertos a todos. A raça dá identidade, não uma limitação.
- **Estratégia e criatividade:** o jogador decide o que comprar, quando poupar ouro, quando atacar, defender, usar um item ou passar a vez.
- **Justiça e equilíbrio:** nenhuma raça nem item deve dominar. Há mecanismos contra bola de neve, como o limite de compras por visita (1 equipamento e 1 consumível).
- **Partidas dinâmicas:** o D10 dá emoção e variância. O jogo não pode ser longo demais (a versão inicial passava de 30 rodadas).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Telas, turnos, combate, raças e interface do Comerciante. |
| `shop.py` | Lógica sem interface: catálogo de itens por fase, estoque, compra, uso de itens e cálculo de status. |
| `dice.py` | Faixas do D10 de ataque e de defesa. `resultado_ataque(bonus_crit, bonus_rolagem)` aplica os bônus de crítico (o crítico nunca começa abaixo de 6) e de rolagem (máximo 10). |

## Regras atuais

### Turno e rodada

A ordem da rodada é **sorteada livremente a cada rodada** (qualquer um pode abrir, inclusive duas rodadas seguidas). No início do turno o jogador ganha **6 moedas**, que sobem para **8 depois do fim da rodada 10** e para **10 depois do fim da rodada 20** (com aviso na tela; o valor atual e o próximo aumento aparecem sempre no cabeçalho do turno). Depois escolhe uma entre:

1. Atacar
2. Postura defensiva
3. Inventário e itens
4. Passar a vez
5. Escudo de Mana (só o Feiticeiro)

Itens de ação livre não gastam o turno.

**Voltar e confirmar:** ao escolher **Atacar**, o jogo pede confirmação; depois, a lista de alvos tem a opção `0 = voltar` (de volta ao menu de ações). Escolhido o alvo, o ataque acontece direto. **Postura**, **Passar a vez** e **Escudo de Mana** pedem uma confirmação simples (1 confirma, 2 volta ao menu). O Inventário já tem a sua própria opção `0 = voltar`.

### Ataque

- O ataque é infalível. O D10 define o multiplicador do dano:

  | D10 | Resultado | Multiplicador |
  |---|---|---|
  | 1–3 | Golpe Fraco | ×0,5 |
  | 4–8 | Golpe Normal | ×1 |
  | 9–10 | Golpe Crítico | ×2 e +3 moedas |

- Quem é atacado fica **protegido no turno seguinte** (não pode ser atacado em dois turnos seguidos), mas pode levar dois ou mais ataques na mesma rodada. A proteção **zera no fim da rodada**: quem foi atacado no último turno pode ser atacado no primeiro turno da rodada seguinte. Bombas e o Cajado Relâmpago contam como ataque.
- O dano passa por esta ordem: postura (D10 de defesa que bloqueia 30%, 60% ou 90% e reflete 75% do bloqueado), Escudo de Mana, Defesa fixa (dano mínimo 1), escudos de item e vida.
- A postura dura até a próxima vez do jogador (ela termina quando chega a vez dele de agir) ou até ele ser atingido, o que vier primeiro. Para continuar protegido, ele escolhe a postura de novo.

### Dano físico e mágico

Todas as raças têm os mesmos três status: vida, dano físico e dano mágico. Raças físicas começam com mágico 0, e o Feiticeiro começa com físico 0. O dano do ataque é a soma dos dois.

**Afinidade de dano:** o dano de itens fora da afinidade da raça rende só **50%**: dano mágico de itens em quem não é Feiticeiro, e dano físico de itens no Feiticeiro (itens híbridos rendem 75%). A loja e o inventário mostram o aviso.

**Penetração mágica é exclusiva do Feiticeiro:** a parte mágica do dano dele ignora **75%** da Defesa do alvo, proporcional à fração mágica do ataque. Outras raças com armas mágicas não ganham essa penetração. Qualquer raça pode ter penetração vinda de itens específicos (Maça Estilhaçadora, Cajado Arcano, Anel Perfurante etc.); o teto total é 90%.

### Raças

| Raça | Vida | Dano inicial | Identidade |
|---|---|---|---|
| Bárbaro | 120 | físico 3 | **Fúria 4/4:** cada ataque enche 1/4. Cheia, o próximo ataque rola **dois D10 de ataque** e soma o dano dos dois golpes; depois a barra zera e fica bloqueada por 1 rodada. A postura **não** enche a Fúria (sem bônus racial de postura). |
| Goblin | 115 | físico 3 | **Ganancioso:** ganha 50% a mais de ouro (1,5x): +3 por turno (+4 depois da rodada 10, +5 depois da rodada 20) e +5 no Comerciante. **Pechinchar** (35% de chance de 15% de desconto; depois do desconto fica desabilitado até a próxima visita). A postura não dá bônus racial. |
| Feiticeiro | 110 | mágico 5 (ataque inicial 8 com o Livro velho) | **Mana 3/3:** cada ataque custa 1/3. **Escudo de Mana** (custa 2/3, mitiga **60%** do próximo ataque recebido). Postura recupera +1/3 de mana. |
| Ferreiro | 110 | físico 3 | **Mestre do Metal** (+10% em armas e armaduras), **A Forja** (por nível: +10% e ainda **+1 de dano** em arma ou **+1 de Defesa e +10 de vida** em armadura; 1 uso por visita, até 3 níveis por item). Postura bloqueia +10%. |

Cada raça começa com uma arma de +3 de dano.

### Comerciante

Chega ao fim de cada 5 rodadas.

- Cada jogador recebe +10 moedas, **recupera 10% da vida máxima** e vê um estoque próprio de 5 itens, sorteado só para ele, mais uma poção fixa que está sempre à venda: **🩹 Poção Simples** (cura 15, 10 moedas, gasta o turno) até a rodada 15 e **🧴 Poção Reforçada** (cura 30, 20 moedas, gasta o turno) a partir da rodada 20.
- O estoque depende da fase: **Early** até a rodada 9, **Mid** a partir da rodada 10, **Late** a partir da 20. Na prática: visita da rodada 5 é Early, das rodadas 10 e 15 é Mid, e da 20 em diante é Late.
- Cada jogador compra até **1 equipamento** (arma, armadura, joia ou ativo) **e 1 consumível** por visita. A ordem de compra é **sorteada a cada visita** (como cada um tem o seu próprio estoque, a ordem não muda o que cada um pode comprar).
- Itens ativos não podem se repetir (não dá para ter dois Olhos Protetores, por exemplo).
- Espaços de equipamento: 2 armas, 1 armadura, 2 joias, 2 ativos. Com o espaço cheio, o jogador escolhe qual item substituir.
- Armaduras só aumentam a vida máxima; não curam a vida atual.

### Itens

- **Consumíveis:** poções, antídoto, bombas, venenos, buffs. Preços cerca de 30% menores que na primeira versão, exceto as curas (Poção de Cura, Elixir Maior e Elixir Dourado), que mantêm o preço original.
- **Armas** físicas, mágicas ou híbridas: algumas dão crítico, penetração, vampirismo ou veneno.
- **Armaduras e joias.**
- **Ativos** reutilizáveis com recarga: Cálice Vital, Olho Protetor, Chifre de Guerra, Luvas do Ladrão, Capa da Invisibilidade, Cajado Relâmpago.
- **Efeitos de status:** veneno (nunca elimina), invisibilidade, escudo, Defesa temporária.
- **Anel Venenoso:** envenena (4 por rodada durante 3 rodadas) e depois recarrega por 3 rodadas.
- **Bônus de crítico:** +1 faz o crítico começar no 8 do D10 (30%), +2 no 7 (40%); o máximo é a partir do 6 (50%).

## Histórico de balanceamento

Antes, o Feiticeiro ganhava só 3% das partidas e o Ferreiro 45%, os itens decidiam tudo e a postura quase não valia a pena. Mudamos regeneração de mana, penetração, preços e valores de itens, Mestre do Metal e Forja, espaços de equipamento, ordem de compra, estoque, reflexo da postura e bônus de postura por raça. Com isso, em partidas de 4 jogadores (uma raça de cada) ficou perto de 25% para cada, com cerca de 32 rodadas. Esses números são de antes das mudanças de itens, lojas, Fúria e Escudo de Mana, então valem como referência, não como medida atual.

### Mudanças mais recentes

- Opção de voltar no ataque e confirmação nas outras ações do turno.
- Escudo de Mana subiu de 40% para 55%.
- Fúria do Bárbaro: em vez de +50% de dano, o ataque enfurecido rola dois D10 e soma os dois golpes. O bônus do Trevo da Sorte vale para os dois dados, e cada crítico dá o seu bônus de moedas.

Ajustes de balanceamento depois da primeira simulação (detalhes em `simulacao/RELATORIO_AJUSTES.md`):

- Postura defensiva termina na próxima vez do jogador (antes durava até ele ser atingido, mesmo que atacasse nesse meio tempo).
- Bárbaro: a Fúria precisa de 4 ataques (antes 3) e a postura não enche mais a Fúria.
- Goblin: ganha 1,5x o ouro das outras raças (antes 2x).
- Comerciante: até 2 compras por visita (antes 1); fases Mid a partir da rodada 10 e Late a partir da 20 (antes 15 e 30).
- Feiticeiro: dano mágico inicial 6 (antes 4); penetração mágica 75% (antes 50%).
- Ferreiro: A Forja dá +15% por nível (antes +5%).

Segunda rodada de ajustes:

- Forja: além dos +15%, cada nível dá pontos inteiros (+1 de dano em arma; +1 de Defesa e +10 de vida em armadura).
- Goblin: a postura não dá mais ouro.
- Escudo de Mana: 60% (antes 55%).
- Consumíveis cerca de 30% mais baratos.
- Penetração mágica só para o Feiticeiro.

Terceira rodada de ajustes:

- Comerciante: 1 equipamento + 1 consumível por visita (antes: 2 itens quaisquer); itens ativos não se repetem.
- Curas voltaram ao preço original.
- Proteção depois de ser atacado: vale só o turno seguinte (antes: o resto da rodada).

Quarta rodada de ajustes (depois do primeiro teste jogado):

- Confirmação ao escolher atacar (escolhido o alvo, o ataque acontece direto).
- A proteção depois de ser atacado zera no fim da rodada.
- Poção Simples sempre à venda no Comerciante (cura 15, 10 moedas).
- Moedas por turno: 6 (8 a partir da rodada 10); crítico dá +3 moedas (antes +6).
- O Comerciante cura 5% da vida máxima de todos os vivos quando chega (valor provisório: 25% deixava as partidas longas demais).
- Quinta rodada de ajustes: Poção Reforçada (fixa a partir da rodada 20); afinidade de dano (50% fora da raça); moedas 6 → 8 (depois da 10ª rodada) → 10 (depois da 20ª); Comerciante cura 10%; Anel Venenoso com recarga de 3 rodadas.
- Sexta rodada de ajustes: Forja +10% por nível (antes +15%); Feiticeiro com dano mágico inicial 5 (ataque inicial 8, antes 9).
- Sorteios: a ordem das rodadas e a ordem de compra no Comerciante são sorteadas livremente (saiu a regra de "quem abriu não abre a próxima" e a ordem "do menos equipado ao mais equipado"); a roleta da rodada 1 agora para no nome sorteado.

## Propostas e pontos em aberto

| Proposta | Situação |
|---|---|
| Dado para acertar ou errar (D20) | Fica para depois. |
| Tirar a Fúria do Bárbaro ao defender | Feito: a postura não enche mais a Fúria. |
| Resistência Mágica | Não será feita por enquanto. |
| Poção simples com D4 para passar ou não a vez | Boa ideia. Poções fortes e ativos sempre gastariam o turno; precisa ser conciliado com o sistema atual de ação livre. |
| Goblin com +5 de ouro e roubo de moedas no crítico | Precisa de refinamento: cai para 18–20% de vitórias. Roubo de D10 ou manter o +5 resolve. |
| Postura acaba no fim da rodada | Substituída: a postura agora acaba na próxima vez do jogador. |

Outras questões:

- O Mestre do Metal e a Forja valem para armas mágicas? (Hoje valem para qualquer arma ou armadura.) O Escudo de Mana protege só contra dano mágico? (Hoje protege contra tudo.)
- A Armadura de Placas supera a de Couro, e as armaduras ainda ficam atrás das armas.
- O Ferreiro continua abaixo das outras raças mesmo com a Forja mais forte (veja `simulacao/RELATORIO_AJUSTES.md`).
- Multiplicadores se acumulam: Poção de Fúria ou Chifre de Guerra (×2) com Fúria (dois dados) e críticos podem gerar picos muito altos de dano.
