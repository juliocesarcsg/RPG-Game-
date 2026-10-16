# Arena de Combate

RPG PvP de terminal, em turnos, escrito em Python. De 2 a 6 jogadores se revezam no mesmo teclado (hot-seat) até sobrar um vivo.

> Versões anteriores guardadas no repositório: [`v1-original`](https://github.com/juliocesarcsg/RPG-Game-/tree/v1-original) (antes dos ajustes de balanceamento) e [`v2-antes-personagens`](https://github.com/juliocesarcsg/RPG-Game-/tree/v2-antes-personagens) (4 raças, antes do Hemomante, do Alquimista e do Mosqueteiro). Para rodar uma delas: `git checkout <nome da etiqueta>`.

## Como rodar

```bash
pip install rich
python main.py
```

Use um terminal com suporte a emoji e cores (Windows Terminal, terminal do VS Code etc.).

## Foco do jogo

- **Liberdade de build:** qualquer personagem pode comprar qualquer item. Armas e joias físicas ou mágicas, armaduras, itens ativos, poções e venenos são abertos a todos; itens fora do estilo do personagem só rendem menos. O personagem dá identidade, não uma limitação.
- **Estratégia e criatividade:** o jogador decide o que comprar, quando poupar ouro, quando atacar, defender, usar um item ou passar a vez.
- **Justiça e equilíbrio:** nenhum personagem nem item deve dominar. Há mecanismos contra bola de neve, como o limite de compras por visita (1 equipamento e 1 consumível).
- **Partidas dinâmicas:** o D10 dá emoção e variância. O jogo não pode ser longo demais (a versão inicial passava de 30 rodadas).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Telas, turnos, combate, personagens e interface do Comerciante. |
| `shop.py` | Lógica sem interface: catálogo de itens por fase, estoque, compra, uso de itens e cálculo de status. |
| `dice.py` | Faixas do D10 de ataque e de defesa. `resultado_ataque(bonus_crit, bonus_rolagem)` aplica os bônus de crítico (o crítico nunca começa abaixo de 6) e de rolagem (o resultado fica sempre entre 1 e 10). |

## Regras atuais

### Turno e rodada

A ordem da rodada é **sorteada livremente a cada rodada** (qualquer um pode abrir, inclusive duas rodadas seguidas). No início do turno o jogador ganha **6 moedas**, que sobem para **8 depois do fim da rodada 10**, para **10 depois do fim da rodada 20** e para **12 depois do fim da rodada 30** (com aviso na tela; o valor atual e o próximo aumento aparecem sempre no cabeçalho do turno). Depois escolhe uma entre:

1. Atacar
2. Postura defensiva (no Feiticeiro, que não tem postura, esta opção é o **Escudo de Mana**)
3. Inventário e itens
4. Passar a vez
5. Habilidade de ação livre do personagem (só Bárbaro, Hemomante e Mosqueteiro)

Itens de ação livre não gastam o turno.

**Voltar e confirmar:** ao escolher **Atacar**, o jogo pede confirmação; depois, a lista de alvos tem a opção `0 = voltar` (de volta ao menu de ações). Escolhido o alvo, o ataque acontece direto. **Postura**, **Passar a vez**, **Escudo de Mana** e as habilidades de ação livre pedem uma confirmação simples (1 confirma, 2 volta ao menu). O Inventário já tem a sua própria opção `0 = voltar`.

### Ataque

- O ataque é infalível. O D10 define o multiplicador do dano:

  | D10 | Resultado | Multiplicador |
  |---|---|---|
  | 1–3 | Golpe Fraco | ×0,5 |
  | 4–8 | Golpe Normal | ×1 |
  | 9–10 | Golpe Crítico | ×2 e +3 moedas |

- **Crítico ladrão do Goblin:** no Goblin, cada crítico rouba 2 moedas do alvo, no lugar das +3 moedas.
- Quem é atacado fica **protegido no turno seguinte** (não pode ser atacado em dois turnos seguidos), mas pode levar dois ou mais ataques na mesma rodada. A proteção **zera no fim da rodada**: quem foi atacado no último turno pode ser atacado no primeiro turno da rodada seguinte. Bombas e o Cajado Relâmpago contam como ataque.
- O dano passa por esta ordem: postura (D10 de defesa, tabela abaixo), Escudo de Mana, Defesa fixa (dano mínimo 1), escudos de item e vida.
- **Morte súbita:** a partir da rodada 35, todas as curas (poções, vampirismo, regeneração, Comerciante, Fôlego) rendem 50%. Aparece um aviso na tela.
- A postura dura até a próxima vez do jogador (ela termina quando chega a vez dele de agir) ou até ele ser atingido, o que vier primeiro. Para continuar protegido, ele escolhe a postura de novo. A postura **não reflete** dano. O Feiticeiro não tem postura.

  | D10 de defesa | 1–2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
  |---|---|---|---|---|---|---|---|---|---|
  | Dano bloqueado | 0% | 10% | 20% | 30% | 40% | 50% | 60% | 70% | 95% (+6 moedas) |

  O bônus de bloqueio do Ferreiro (+10%) soma a esses valores, com teto de 95%.

### Dano físico e mágico, corpo a corpo e à distância

Todos os personagens têm os mesmos três status: vida, dano físico e dano mágico. O dano do ataque é a soma dos dois. Cada personagem tem um **tipo de dano** (físico, mágico ou híbrido) e um **alcance** (corpo a corpo, à distância ou híbrido):

- **Afinidade de dano:** dano de itens de outro tipo rende só **50%** (ex.: arma mágica num personagem físico; itens híbridos rendem 75%). Personagens híbridos aproveitam 100% de tudo.
- **Alcance:** cada arma é corpo a corpo ou à distância. Com uma arma de alcance diferente do personagem equipada, o D10 de ataque leva **−1** (o resultado nunca fica abaixo de 1), o que reduz o dano médio em cerca de 15% e faz o crítico sem bônus só sair no 10. Personagens híbridos não sofrem essa penalidade.
- A loja e o inventário mostram os avisos.

**Penetração mágica é exclusiva do Feiticeiro:** a parte mágica do dano dele ignora **75%** da Defesa do alvo, proporcional à fração mágica do ataque. Outros personagens com armas mágicas não ganham essa penetração. Qualquer personagem pode ter penetração vinda de itens específicos (Maça Estilhaçadora, Cajado Arcano, Anel Perfurante etc.); o teto total é 90%.

### Personagens

| Personagem | Vida | Dano inicial | Estilo | Identidade |
|---|---|---|---|---|
| Bárbaro | 120 | físico 3 | corpo a corpo, físico | **Fúria 4/4:** cada ataque enche 1/4. Cheia, o próximo ataque rola **dois D10 de ataque** e soma o dano dos dois golpes; depois a barra zera e fica bloqueada por 1 rodada. **Fôlego de Batalha** (ação livre, com a Fúria cheia): consome a Fúria e cura 15% da vida máxima. A postura **não** enche a Fúria. |
| Goblin | 115 | físico 2 | corpo a corpo, físico | **Ganancioso:** ganha 50% a mais de ouro (1,5x): +3 por turno (+4 depois da rodada 10, +5 depois da rodada 20, +6 depois da rodada 30) e +5 no Comerciante. **Crítico ladrão:** cada crítico rouba 2 moedas do alvo. **Pechinchar** (35% de chance de 15% de desconto; depois do desconto fica desabilitado até a próxima visita). A postura não dá bônus. |
| Feiticeiro | 110 | mágico 5 (ataque inicial 8 com o Livro velho) | à distância, mágico | **Mana 3/3:** cada ataque custa 1/3. Ao fim de cada rodada recupera 1/3 (+1/3 se não gastou mana). **Escudo de Mana** (custa 2/3, mitiga **50%** do próximo ataque recebido e dura **no máximo 3 rodadas**, contando a rodada em que foi erguido). **Não tem postura defensiva:** o Escudo de Mana ocupa o lugar dela no menu. |
| Ferreiro | 110 | físico 3 | corpo a corpo, físico | **Mestre do Metal** (+10% em armas e armaduras), **A Forja** (por nível: +10% e ainda **+1 de dano** em arma ou **+1 de Defesa e +10 de vida** em armadura; 1 uso por visita, até 3 níveis por item). Postura bloqueia +10%. |
| Hemomante | 110 | mágico 3 (ataque inicial 6 com o Frasco de sangue) | à distância, mágico | **Vampirismo:** cura 30% do dano causado (soma com itens, até 50%), mas curas de consumíveis rendem só 75%. **Pacto de Sangue** (ação livre, 1 vez por turno): paga 4 de vida para o próximo ataque causar ×1,5; não pode matar a si mesmo e não acumula com outros bônus de dano (vale o maior). |
| Alquimista | 110 | físico 2 e mágico 2 (ataque inicial 6 com o Par de luvas) | híbrido, híbrido | **Bolsa de poções:** compra até 2 consumíveis por visita e cada consumível comprado vem com +1 uso. **Mistura** (1 vez por visita do Comerciante): junta 2 consumíveis num só, com os efeitos dos dois (bombas não entram). Não sofre penalidade de afinidade nem de alcance. **Fraqueza:** só 1 espaço de arma. |
| Mosqueteiro | 105 | físico 4 (ataque inicial 7 com o Estilingue) | à distância, físico | **Recarregar:** munição 3/3; cada disparo gasta 1; com a munição zerada, a postura recarrega a barra inteira. **Na mira** (ação livre, recarga de 3 turnos): o próximo disparo ignora a Defesa e a postura do alvo e causa +2 de dano + 50% do dano físico das armas à distância. |

Cada personagem começa com uma arma inicial (+3 de dano; o Par de luvas do Alquimista dá +2).

### Comerciante

Chega ao fim de cada 5 rodadas.

- Cada jogador recebe +10 moedas, **recupera 10% da vida máxima** e vê um estoque próprio de 5 itens, sorteado só para ele, mais uma poção fixa que está sempre à venda: **💊 Poção Simples** (cura 15, 10 moedas, gasta o turno) até a rodada 15 e **🧴 Poção Reforçada** (cura 30, 20 moedas, gasta o turno) a partir da rodada 20.
- O estoque depende da fase: **Early** até a rodada 9, **Mid** a partir da rodada 10, **Late** a partir da 20. Na prática: visita da rodada 5 é Early, das rodadas 10 e 15 é Mid, e da 20 em diante é Late.
- Cada jogador compra até **1 equipamento** (arma, armadura, joia ou ativo) **e 1 consumível** por visita. A ordem de compra é **sorteada a cada visita** (como cada um tem o seu próprio estoque, a ordem não muda o que cada um pode comprar).
- Itens ativos não podem se repetir (não dá para ter dois Olhos Protetores, por exemplo).
- Espaços de equipamento: 2 armas (1 no Alquimista), 1 armadura, 2 joias, 2 ativos. Com o espaço cheio, o jogador escolhe qual item substituir.
- Armaduras só aumentam a vida máxima; não curam a vida atual.

### Itens

- **Consumíveis:** poções, antídoto, bombas, venenos, buffs. Preços cerca de 30% menores que na primeira versão, exceto as curas (Poção de Cura, Elixir Maior e Elixir Dourado), que mantêm o preço original.
- **Armas** físicas, mágicas ou híbridas, corpo a corpo ou à distância: algumas dão crítico, penetração, vampirismo ou veneno. A **Besta Leve** (Early, +4 físico, à distância, 28 moedas) é a primeira arma física à distância.
- **Armaduras e joias.**
- **Ativos** reutilizáveis com recarga (contada nos turnos do dono): Cálice Vital, Olho Protetor, Chifre de Guerra, Luvas do Ladrão, Capa da Invisibilidade, Cajado Relâmpago, Coroa da Provação. Ativos de ação livre que pedem alvo (Luvas, Coroa) não gastam o turno.
- **Itens da Provação (Late):**
  - **🏰 Armadura da Provação** (125): +4 de Defesa, +65 de vida, **Leitura de Combate** (golpes críticos contra o portador contam como golpes normais: sem ×2, sem moedas do crítico e sem crítico ladrão; na Fúria, cada dado crítico vira normal) e **Última Provação**: um golpe que mataria (ataque, bomba, raio) deixa o portador com 1 de vida, se ele estiver com pelo menos 5% da vida, e o próximo ataque dele é crítico garantido. Com 1 de vida, o próximo golpe mata. Recarrega a cada visita do Comerciante (não acumula). Substituiu as Escamas de Dragão. É a armadura de técnica; a Mithril continua sendo a de defesa bruta.
  - **🤺 Espada da Provação** (120): +9 de dano físico, corpo a corpo, +1 na faixa de crítico, **ignora a postura** do alvo.
  - **👑 Coroa da Provação** (80, ativo): **Sentença**, ação livre, recarga de 4 turnos seus: marca um oponente; até o próximo turno dele, todos os ataques que ele receber (de qualquer jogador, inclusive bombas e raios) causam +45% de dano.
- **🧪 Frasco de Ácido** (Late, 38, consumível): arremessado num oponente, tira 3 de Defesa dele por 3 turnos dele (usar de novo renova a duração, não acumula). Gasta o turno.
- **Efeitos de status:** veneno (nunca elimina), invisibilidade, escudo, Defesa temporária.
- **Anel Venenoso:** envenena (4 por turno do alvo, durante 3 turnos) e depois recarrega por 3 turnos.
- **Turnos x rodadas:** o que é do jogador conta nos **turnos dele**: recarga de itens ativos, do Anel Venenoso e do Na mira, e o veneno, que tira vida no começo do turno de quem está envenenado. O que vale para a rodada inteira conta em **rodadas**: Defesa temporária (Pele de Pedra), Escudo de Mana, Fúria desabilitada, mana do Feiticeiro, economia, Comerciante e morte súbita.
- **Bônus de crítico:** +1 faz o crítico começar no 8 do D10 (30%), +2 no 7 (40%); o máximo é a partir do 6 (50%).

## Histórico de balanceamento

Antes, o Feiticeiro ganhava só 3% das partidas e o Ferreiro 45%, os itens decidiam tudo e a postura quase não valia a pena. Mudamos regeneração de mana, penetração, preços e valores de itens, Mestre do Metal e Forja, espaços de equipamento, ordem de compra, estoque, reflexo da postura e bônus de postura por raça. Com isso, em partidas de 4 jogadores (um de cada) ficou perto de 25% para cada, com cerca de 32 rodadas. Esses números são de antes das mudanças de itens, lojas, Fúria e Escudo de Mana, então valem como referência, não como medida atual.

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
- Sétima rodada de ajustes: Escudo de Mana mitiga 50% (antes: 60%) e dura no máximo 3 rodadas (antes: até ser atingido); o Feiticeiro perdeu a postura defensiva (e o +1/3 de mana que ela dava); D10 de defesa da postura por resultado (1–2: 0%, +10% por ponto do 3 ao 9, 10: 95%; antes 30% / 60% / 90% por faixa); a postura não reflete mais dano (antes: 75% do bloqueado); moedas por turno sobem para 12 depois da rodada 30.

- Novos personagens (detalhes em `simulacao/RELATORIO_PERSONAGENS.md`): Hemomante, Alquimista e Mosqueteiro; "raça" passou a se chamar "personagem"; personagens e armas divididos em corpo a corpo e à distância (−1 no D10 com arma de alcance diferente); afinidade de dano por personagem; Besta Leve; Fôlego de Batalha do Bárbaro; crítico ladrão do Goblin; morte súbita a partir da rodada 35.
- Ajustes depois do relatório dos personagens: Hemomante com roubo de vida 30% (antes 20%) e Pacto de Sangue custando 4 de vida (antes 6); Goblin rouba 2 moedas no crítico (antes 4); Mosqueteiro com munição 3/3 (antes 2/2); Elixir Dourado cura 55 (antes 70) e custa 55. Depois: curas de consumíveis do Hemomante rendem 75% (antes 50%); Goblin com dano físico inicial 2 (antes 3).
- Itens novos: Armadura da Provação (no lugar das Escamas de Dragão), Espada da Provação, Coroa da Provação e Frasco de Ácido; recargas descritas como "turnos seus"; corrigido: ativos de ação livre com alvo (Luvas do Ladrão, Coroa) não encerram mais o turno.
- Interface: os equipamentos aparecem no cabeçalho do turno e do Comerciante; a tela final mostra todos os jogadores (colocação, rodada em que cada um foi eliminado e equipamentos); recargas e veneno contados em turnos do jogador.

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
