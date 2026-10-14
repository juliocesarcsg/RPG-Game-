Arena de Combate: resumo do projeto
O que é

Um RPG PvP de terminal, em turnos, escrito em Python. De 2 a 6 jogadores se revezam no mesmo teclado (hot-seat) até sobrar um vivo. A interface usa a biblioteca rich (pip install rich, depois python main.py).

Foco do jogo
Liberdade de build: qualquer raça pode montar o personagem que quiser pelas compras. Armas e joias físicas ou mágicas, armaduras, itens ativos, poções e venenos são abertos a todos. A raça dá identidade, não uma limitação.
Estratégia e criatividade: o jogador decide o que comprar, quando poupar ouro, quando atacar, defender, usar um item ou passar a vez.
Justiça e equilíbrio: nenhuma raça nem item deve dominar. Há mecanismos contra bola de neve, como a ordem de compra do mais fraco ao mais forte.
Partidas dinâmicas: o D10 dá emoção e variância. O jogo não pode ser longo demais (a versão inicial passava de 30 rodadas).
Arquivos
main.py: telas, turnos, combate, raças, interface do Comerciante.
shop.py: lógica sem interface (catálogo de itens por fase, estoque, compra, uso de itens, cálculo de status).
dice.py: faixas do D10 de ataque e de defesa. Eu não vi a versão atual dele; o main.py espera resultado_ataque(crit, bonus_rolagem).
Regras atuais

Turno e rodada. A ordem da rodada é sorteada, e quem abriu a rodada anterior não abre a seguinte. No início do turno o jogador ganha 5 moedas. Depois escolhe uma entre: atacar, postura defensiva, inventário/itens, passar a vez, e o Escudo de Mana (só o Feiticeiro). Itens de ação livre não gastam o turno.

Ataque.

O ataque é infalível. O D10 define o multiplicador do dano: 1–3 fraco (×0,5), 4–8 normal (×1), 9–10 crítico (×2 e bônus de ouro).
Cada jogador só pode ser atacado uma vez por rodada.
O dano passa por esta ordem: postura (D10 de defesa que bloqueia 30%, 60% ou 90%, e reflete 75% do bloqueado), Escudo de Mana, Defesa fixa (dano mínimo 1), escudos de item e vida.
A postura dura até o alvo ser atingido.

Dano físico e mágico. Todas as raças têm os mesmos três status: vida, dano físico e dano mágico. Raças físicas começam com mágico 0, e o Feiticeiro começa com físico 0. O dano do ataque é a soma dos dois. Por decisão recente, só o Feiticeiro tem penetração racial: a parte mágica do dano dele ignora 50% da Defesa.

Raça	Vida	Dano inicial	Identidade
Bárbaro	120	físico 3	Fúria 3/3: cada ataque enche 1/3, cheia dá +50% no próximo e depois bloqueia por 1 rodada
Goblin	115	físico 3	+5 de ouro por turno, Pechinchar (35% de chance de 15% de desconto), postura dá ouro
Feiticeiro	110	mágico 4	Mana 3/3, Escudo de Mana (mitiga 40%), penetração
Ferreiro	110	físico 3	Mestre do Metal (+10% em armas e armaduras), A Forja (+5% por visita, até 3 níveis por item)

Cada raça começa com uma arma de +3 de dano.

Comerciante. Chega ao fim de cada 5 rodadas.

Cada jogador recebe +10 moedas e vê um estoque próprio de 5 itens, sorteado só para ele.
O estoque depende da fase: Early até a rodada 15, Mid até a 30, Late depois.
Cada jogador faz 1 compra por visita, na ordem do menos equipado ao mais equipado.
Espaços de equipamento: 2 armas, 1 armadura, 2 joias, 2 ativos. Com o espaço cheio, o jogador escolhe qual item substituir.
Armaduras só aumentam a vida máxima; não curam a vida atual.

Itens.

Consumíveis: poções, antídoto, bombas, venenos, buffs.
Armas, físicas, mágicas ou híbridas: algumas dão crítico, penetração, vampirismo ou veneno.
Armaduras e joias.
Ativos reutilizáveis com recarga: Cálice Vital, Olho Protetor, Chifre de Guerra, Luvas do Ladrão, Capa da Invisibilidade, Cajado Relâmpago.
Efeitos de status: veneno (nunca elimina), invisibilidade, escudo, Defesa temporária.
O que o balanceamento já mudou

Antes, o Feiticeiro ganhava só 3% das partidas e o Ferreiro 45%, os itens decidiam tudo e a postura quase não valia a pena. Mudamos regeneração de mana, penetração, preços e valores de itens, Mestre do Metal e Forja, espaços de equipamento, ordem de compra, estoque, reflexo da postura e bônus de postura por raça. Com isso, em partidas de 4 jogadores (uma raça de cada) ficou perto de 25% para cada, com cerca de 32 rodadas. Esses números são da versão anterior às suas mudanças de itens e lojas, então valem como referência, não como medida atual.

Propostas debatidas e ainda não implementadas
Proposta	Conclusão
Dado para acertar ou errar	Boa. Sugiro D20: erro 1–2, fraco 3–6, normal 7–16, crítico 17–20. A distribuição é igual a D10 com erro no 1, e itens de +1 valem 5%. O mesmo dado decide acerto e dano.
Escudo de Mana a 70%	Exagero: o Feiticeiro sobe para cerca de 29%. Sugiro 55–60%.
Opção de voltar no painel de ações	Necessária, é correção de usabilidade.
Fúria do Bárbaro com D10	Boa. Sugiro multiplicador 1 + D10/10. Cuidado com combinações que chegam a ×4.
Poção simples com D4 para passar ou não a vez	Boa. Poções fortes e ativos sempre gastariam o turno. Isso precisa ser conciliado com o sistema atual de ação livre.
Goblin com +5 de ouro e roubo de moedas no crítico	Precisa de refinamento: cai para 18–20%. Roubo de D10 ou manter o +5 resolve.
Postura acaba no fim da rodada	Perigosa. Quem joga por último nunca consegue se defender. Só funciona com reflexo perto de 100% e ordem bem visível.
Tirar a Fúria do Bárbaro ao defender	Concordo.
Pontos abertos
O dano mágico das outras raças hoje só aparece no status. A diferença real é a penetração do Feiticeiro. Para dar contrajogo, falta algo como Resistência Mágica.
O Mestre do Metal e a Forja valem para armas mágicas? A Fúria multiplica os dois tipos de dano? O Escudo de Mana protege só contra mágico?
Com 5 ou 6 jogadores o Goblin fica muito fraco (cerca de 5%).
A Armadura de Placas supera a de Couro, e as armaduras ainda ficam atrás das armas.
Sem a cura embutida, o Ferreiro (que depende de armaduras) perdeu força.
