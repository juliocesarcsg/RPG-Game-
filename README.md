# Arena de Combate

RPG PvP de terminal, em turnos, escrito em Python. De 2 a 6 jogadores se revezam no mesmo teclado (hot-seat) até sobrar um vivo.

> Versões anteriores guardadas no repositório: [`v1-original`](https://github.com/juliocesarcsg/RPG-Game-/tree/v1-original) (antes dos ajustes de balanceamento) e [`v2-antes-personagens`](https://github.com/juliocesarcsg/RPG-Game-/tree/v2-antes-personagens) (4 raças, antes do Hemomante, do Alquimista e do Mosqueteiro). Para rodar uma delas: `git checkout <nome da etiqueta>`.

## Como rodar

**Janela do jogo (recomendado):** dê dois cliques em `dist\ArenaDeCombate.exe`. O jogo abre numa janela própria, e dá para jogar 100% no teclado: números escolhem (inclusive A Forja, a Mistura e Sair do Comerciante), 0 volta, Enter continua, e na criação do personagem as setas ↑ ↓ trocam o personagem enquanto você digita o nome. Tab e Enter também funcionam em qualquer botão. **F11** liga e desliga a tela cheia (também há um botão no canto da caixa de cima).

O executável não fica no repositório. Para gerá-lo (ou gerar de novo depois de mudar o código):

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
gerar_exe.bat
```

Sem gerar o executável, dá para abrir a mesma janela direto pelo Python: `.venv\Scripts\python.exe app.py`.

**Versão de terminal (a original):** continua funcionando, com as mesmas regras.

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
| `main.py` | Personagens, combate e turnos, e a versão de terminal (telas com `rich`). As regras do ataque ficam em `resolver_ataque` e `resolver_dano_direto`, que não mostram nada: o terminal e a janela usam as mesmas funções. |
| `shop.py` | Lógica sem interface: catálogo de itens por fase, estoque, compra, uso de itens e cálculo de status. |
| `dice.py` | Faixas do D10 de ataque e de defesa. `resultado_ataque(bonus_crit, bonus_rolagem)` aplica os bônus de crítico (o crítico nunca começa abaixo de 6) e de rolagem (o resultado fica sempre entre 1 e 10). |
| `partida.py` | Motor da janela: o fluxo da partida (escolha, rodadas, Comerciante, fim) sem `input()` nem `print()`. Recebe cada clique em `Partida.agir` e devolve o estado da tela em `Partida.estado`. |
| `app.py` | Abre a janela (pywebview). Com `--navegador`, serve a mesma interface em `http://localhost:8765/?navegador` para testes. |
| `interface/` | A tela do jogo (`index.html`, `estilo.css`, `jogo.js`): três caixas como nas mesas de RPG online, dados animados um de cada vez (3 s cada, como no terminal) e até 6 jogadores na caixa de cima. Visual em `estilo.css`: paleta, fontes, espaços e componentes centralizados em variáveis. |
| `PLANO_MULTIPLAYER.md` | Plano detalhado do modo em rede (mesma tela para todos, cada um joga só na sua vez). Ainda não implementado. |
| `gerar_exe.bat` | Gera `dist\ArenaDeCombate.exe` com o PyInstaller, já com o ícone do jogo. |
| `icone/` | Ícone do jogo: `icone.ico` (16 a 256 px, usado no `.exe` e na janela) e `icone.png` (512 px). A aba do navegador usa `interface/icone.png`. |
| `interface/classes/` | Ícone de cada personagem (`barbaro.png`, `goblin.png`, `feiticeiro.png`, `ferreiro.png`, `hemomante.png`, `alquimista.png`, `mosqueteiro.png`; 256 px, fundo transparente). A janela usa no lugar do emoji do personagem; o terminal continua com o emoji. |
| `prototipo/telas.html` | Protótipo aprovado das telas (só visual, com dados de exemplo). |

## Regras atuais

### Turno e rodada

A ordem da rodada é **sorteada livremente a cada rodada** (qualquer um pode abrir, inclusive duas rodadas seguidas). No início do turno o jogador ganha **6 moedas**, que sobem para **8 depois do fim da rodada 10**, para **10 depois do fim da rodada 20** e para **12 depois do fim da rodada 30** (com aviso na tela; o valor atual e o próximo aumento aparecem sempre no cabeçalho do turno). Depois escolhe uma entre:

1. Atacar
2. Postura defensiva (no Feiticeiro, que não tem postura, esta opção é o **Escudo de Mana**)
3. Inventário e itens
4. Passar a vez
5. Habilidade de ação livre do personagem (só Bárbaro, Hemomante e Mosqueteiro)

No Mosqueteiro sem munição, a opção 1 vira **Recarregar** (no lugar de Atacar).

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
- A postura dura até a próxima vez do jogador (ela termina quando chega a vez dele de agir) ou até ele ser atingido, o que vier primeiro. Para continuar protegido, ele escolhe a postura de novo. **Mecânica secreta** (não aparece nos textos do jogo): a postura escolhida no 3º turno seguido falha (o turno é gasto e não protege nem recarrega a munição); qualquer outra ação no meio quebra a sequência. A postura **não reflete** dano. O Feiticeiro não tem postura.

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
| Hemomante | 110 | mágico 3 (ataque inicial 6 com o Frasco de sangue) | à distância, mágico | **Vampirismo:** cura 35% do dano causado (soma com itens, até 50%), mas curas de consumíveis rendem só 75%. **Pacto de Sangue** (ação livre, 1 vez por turno): paga 5 de vida para o próximo ataque causar ×1,5; não pode matar a si mesmo e não acumula com outros bônus de dano (vale o maior). |
| Alquimista | 110 | físico 2 e mágico 2 (ataque inicial 6 com o Par de luvas) | híbrido, híbrido | **Bolsa de poções:** compra até 2 consumíveis por visita e cada consumível comprado vem com +1 uso. **Mistura** (1 vez por visita do Comerciante): junta 2 consumíveis num só, com os efeitos dos dois (bombas não entram). Não sofre penalidade de afinidade nem de alcance. **Fraqueza:** só 1 espaço de arma. |
| Mosqueteiro | 105 | físico 4 (ataque inicial 7 com o Estilingue) | à distância, físico | **Recarregar:** munição 3/3; cada disparo gasta 1; com a munição zerada, a ação **Recarregar** entra no lugar do ataque: gasta o turno, enche a barra e **não protege** (ele fica exposto; a postura não recarrega mais). **Na mira** (ação livre, recarga de 3 turnos): o próximo disparo ignora a Defesa e a postura do alvo e causa +2 de dano + 50% do dano físico das armas à distância. |

Cada personagem começa com uma arma inicial (+3 de dano; o Par de luvas do Alquimista dá +2).

### Comerciante

Chega ao fim de cada 5 rodadas.

- Cada jogador recebe +10 moedas, **recupera 10% da vida máxima** e vê um estoque próprio de 5 itens, sorteado só para ele, mais uma poção fixa que está sempre à venda: **💊 Poção Simples** (cura 15, 10 moedas, gasta o turno) até a rodada 15 e **🧴 Poção Reforçada** (cura 30, 20 moedas, gasta o turno) a partir da rodada 20.
- O estoque depende da fase: **Early** até a rodada 14, **Mid** a partir da rodada 15, **Late** a partir da 25. Na prática: visitas das rodadas 5 e 10 são Early, das rodadas 15 e 20 são Mid, e da 25 em diante são Late.
- **Itens de outras fases:** a última visita de cada fase traz uma prévia da seguinte, e o Late sempre mistura itens Mid, para o fim da partida não ficar repetitivo. Dos 5 itens sorteados: rodada 5 = 5 Early; rodada 10 = 4 Early + 1 Mid; rodada 15 = 5 Mid; rodada 20 = 4 Mid + 1 Late; rodada 25 em diante = 3 ou 4 Late + 1 ou 2 Mid. A garantia de 1 item de cada tipo vale para a parte da fase da visita.
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
  - **🏰 Armadura da Provação** (125): +4 de Defesa, +65 de vida, **Última Provação**: um golpe que mataria (ataque, bomba, raio) deixa o portador com 1 de vida, com qualquer vida antes do golpe, e o próximo ataque dele é crítico garantido. Depois de usada, só volta na próxima visita do Comerciante (não acumula): até lá, o próximo golpe que mataria mata. Substituiu as Escamas de Dragão. É a armadura de técnica; a Mithril continua sendo a de defesa bruta.
  - **🤺 Espada da Provação** (135): +9 de dano físico, corpo a corpo, +1 na faixa de crítico, **ignora a postura** do alvo.
  - **👑 Coroa da Provação** (80, ativo): **Sentença**, ação livre, recarga de 4 turnos seus: marca um oponente; até o próximo turno dele, todos os ataques que ele receber (de qualquer jogador, inclusive bombas e raios) causam +45% de dano.
- **🧪 Frasco de Ácido** (Late, 38, consumível): arremessado num oponente, tira 3 de Defesa dele por 3 turnos dele (usar de novo renova a duração, não acumula). Gasta o turno.
- **Itens Late para fechar partidas e para os personagens mais fracos:**
  - **☠️ Óleo Necrótico** (40, consumível, ação livre): o próximo ataque que ferir abre uma **Ferida**: as curas do alvo (poções, vampirismo, regeneração, Comerciante, Fôlego) rendem 50% por 3 turnos dele.
  - **🛢️ Barril de Pólvora** (45, consumível): 8 de dano fixo em **todos** os oponentes, até protegidos e invisíveis (ignora Defesa, postura e Escudo de Mana; o escudo de item absorve, a Sentença soma). Não conta como ataque: ninguém fica protegido por causa dele. Gasta o turno.
  - **🗡️ Lâmina do Filho da Puta** (110, arma corpo a corpo física): +7 de dano e **Execução**: +50% de dano em alvo com 20% da vida ou menos.
  - **🎒 Bandoleira do Atirador** (70, joia): +2 de dano físico; no Mosqueteiro, munição 4/4.
  - **🩸 Relicário de Sangue** (75, joia mágica): +3 de dano mágico; no Hemomante, o Pacto de Sangue custa 2 de vida a menos e as curas de consumíveis rendem 100%.
- **Efeitos de status:** veneno (nunca elimina), Ferida (curas pela metade), invisibilidade, escudo, Defesa temporária.
- **Anel Venenoso:** envenena (4 por turno do alvo, durante 3 turnos) e depois recarrega por 3 turnos.
- **Turnos x rodadas:** o que é do jogador conta nos **turnos dele**: recarga de itens ativos, do Anel Venenoso e do Na mira, e o veneno, que tira vida no começo do turno de quem está envenenado. O que vale para a rodada inteira conta em **rodadas**: Defesa temporária (Pele de Pedra), Escudo de Mana, Fúria desabilitada, mana do Feiticeiro, economia e Comerciante.
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
- Oitava rodada de ajustes: saiu a morte súbita (as curas rendiam 50% a partir da rodada 35); Mosqueteiro recarrega com uma ação própria, Recarregar, no lugar do ataque quando a munição zera (antes: a postura recarregava), e fica sem defesa nesse turno; Pacto de Sangue custa 5 de vida (antes 4); a Armadura da Provação perdeu a Leitura de Combate (críticos contra ela voltam a contar); postura em 3 turnos seguidos falha (mecânica secreta). Janela: jogável 100% no teclado (setas na escolha do personagem; números para Forja, Mistura e Sair do Comerciante; Enter/espaço no botão com foco). Loja: itens de outras fases (prévia da próxima fase nas rodadas 10 e 20; 1 a 2 itens Mid em toda visita do Late). Fases do Comerciante: Mid a partir da rodada 15 e Late a partir da 25 (antes: 10 e 20). Itens Late novos: Óleo Necrótico (Ferida), Barril de Pólvora (dano em área), Lâmina do Filho da Puta (Execução), Bandoleira do Atirador e Relicário de Sangue; Cajado Relâmpago com raio de 20 (antes 16) e Espada da Provação custando 135 (antes 120). Depois: Execução da Lâmina só com o alvo a 20% da vida ou menos (antes 25%); a Última Provação vale com qualquer vida (antes exigia pelo menos 5% da vida); Armadura de Mithril custa 95 (antes 100). Cura pelo dano causado: itens de loja curam 5 pontos percentuais a menos (Machado Sedento e Grimório Sombrio 10%, Anel Sanguessuga 20%, Amuleto do Vampiro 15%) e o Vampirismo do Hemomante sobe para 35% (antes 30%), mais que qualquer item. Janela: nova identidade visual (minimalismo medieval: moldura escura, painéis marrons, área de leitura em pergaminho, dourado só na seleção e na ação principal); quem ataca e quem é atacado aparecem acima dos dados desde o começo da rolagem (no terminal, a linha sai antes do dado); cada opção numerada mantém o número da sua posição mesmo bloqueada (ações, alvos, inventário, estoque, Forja, Mistura e Sair).

## Propostas e pontos em aberto

| Proposta | Situação |
|---|---|
| Dado para acertar ou errar (D20) | Fica para depois. |
| Tirar a Fúria do Bárbaro ao defender | Feito: a postura não enche mais a Fúria. |
| Resistência Mágica | Não será feita por enquanto. |
| Poção simples com D4 para passar ou não a vez | Boa ideia. Poções fortes e ativos sempre gastariam o turno; precisa ser conciliado com o sistema atual de ação livre. |
| Goblin com +5 de ouro e roubo de moedas no crítico | Precisa de refinamento: cai para 18–20% de vitórias. Roubo de D10 ou manter o +5 resolve. |
| Modo em rede (mesma tela, cada um na sua vez) | Planejado em `PLANO_MULTIPLAYER.md`. |
| Postura acaba no fim da rodada | Substituída: a postura agora acaba na próxima vez do jogador. |

Outras questões:

- O Mestre do Metal e a Forja valem para armas mágicas? (Hoje valem para qualquer arma ou armadura.) O Escudo de Mana protege só contra dano mágico? (Hoje protege contra tudo.)
- A Armadura de Placas supera a de Couro, e as armaduras ainda ficam atrás das armas.
- O Ferreiro continua abaixo das outras raças mesmo com a Forja mais forte (veja `simulacao/RELATORIO_AJUSTES.md`).
- Multiplicadores se acumulam: Poção de Fúria ou Chifre de Guerra (×2) com Fúria (dois dados) e críticos podem gerar picos muito altos de dano.
