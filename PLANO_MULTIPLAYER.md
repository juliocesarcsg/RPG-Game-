# Plano: modo em rede (mesma tela para todos)

> Situação: **planejado, ainda não implementado.** Este documento é o roteiro para implementar no computador principal.

## 1. O que queremos

- Cada jogador abre o jogo **no próprio computador**, sem Parsec nem compartilhamento de tela.
- **Todos veem exatamente a mesma tela**, a mesma de hoje: cartões, ficha, dados rolando, registro.
- **Cada pessoa só consegue agir na sua vez.** Fora da vez, teclado e cliques não fazem nada: a pessoa assiste.
- Quem não quiser jogar em rede continua jogando como hoje (hot-seat, todos no mesmo teclado).

Fora do escopo desta etapa (ver o item 11): telas diferentes por jogador, informação escondida (ouro e itens dos outros),
loja simultânea, várias salas ao mesmo tempo, servidor na nuvem e tempo limite de turno.

## 2. Como vai funcionar para os jogadores

1. **O anfitrião** (quem tem o jogo) abre o jogo em modo rede:
   - executável: `jogar_em_rede.bat` (ou `ArenaDeCombate.exe --rede`);
   - pelo Python: `python app.py --rede` (janela) ou `python app.py --navegador --rede` (navegador).
2. A tela inicial mostra os **endereços para os outros jogadores**, por exemplo
   `http://192.168.0.10:8765` (mesma casa) e `http://26.14.3.22:8765` (Radmin VPN).
3. **Os outros** abrem esse endereço no navegador (Chrome, Edge, Firefox). Não instalam o jogo.
4. **Escolha dos personagens:** a quantidade de jogadores pode ser escolhida em qualquer aparelho. Cada pessoa digita o
   **seu** nome e escolhe o **seu** personagem no **seu** aparelho. O aparelho que fez a entrada passa a ser o dono daquele
   jogador. Qualquer um aperta "Começar a partida".
5. **Durante a partida:** a tela é a mesma para todos. Em cima da área principal aparece uma faixa:
   - no aparelho de quem está na vez: **"⭐ Sua vez"**;
   - nos outros: **"👀 Vez de ● Ana: você está assistindo"**.
6. O anfitrião tem um botão **"Assumir a vez de Ana"** para quando alguém cair ou fechar o navegador (item 7).
7. Se uma pessoa criar vários jogadores no mesmo aparelho, ela controla todos eles. Com todos os jogadores num PC só, o
   jogo funciona exatamente como hoje.

## 3. Como conectar os computadores

O jogo só precisa que os computadores "se enxerguem" na porta **8765**.

| Situação | Como fazer | Quem instala algo |
|---|---|---|
| Mesma casa (mesmo Wi-Fi/roteador) | Usar o endereço `192.168.x.x:8765` que o jogo mostra | Ninguém |
| Cada um na sua casa, **recomendado** | VPN de jogos: **Radmin VPN** (grátis, Windows, comum para jogar LAN) ou **Tailscale** (grátis, Windows/Mac/Linux/celular). Todos entram na mesma rede da VPN e usam o IP da VPN que o jogo mostra (Radmin: `26.x.x.x`; Tailscale: `100.x.x.x`) | Todos instalam a VPN |
| Cada um na sua casa, só o anfitrião instala | Túnel: **Cloudflare Tunnel** (`cloudflared tunnel --url http://localhost:8765` gera um link `https://….trycloudflare.com`) ou **ngrok**. Os outros abrem o link | Só o anfitrião |

Cuidados:

- **Firewall do Windows:** na primeira vez, o Windows pergunta se libera o Python / ArenaDeCombate. Marcar **redes privadas**.
  Redes de VPN às vezes ficam como "pública". Se os outros não conseguirem entrar, liberar a porta (PowerShell como
  administrador):
  `netsh advfirewall firewall add rule name="Arena de Combate" dir=in action=allow protocol=TCP localport=8765`
- **Túnel = link público:** qualquer pessoa com o link entra na tela de escolha. Só compartilhar com o grupo. A VPN é
  mais fechada.
- Não precisa abrir porta no roteador (port forwarding) em nenhuma das três opções.

## 4. Como o jogo funciona hoje (o que vamos aproveitar)

- `partida.py` (`Partida`) é a **única fonte da verdade**: guarda a partida e aplica as regras. A tela não calcula nada.
- `interface/jogo.js` só faz duas coisas: manda ações (`agir("acao", {id: "atacar"})`) e desenha o que volta de `estado()`.
- `app.py` liga as duas partes:
  - **janela** (pywebview): o JavaScript chama `window.pywebview.api.agir(...)`;
  - **navegador** (`--navegador`): o JavaScript faz `POST /api/agir` num servidor HTTP em `127.0.0.1:8765`.
- O estado da tela (qual menu está aberto, item selecionado, painel do resultado) **já fica no servidor**, dentro de
  `Partida`. Por isso a mesma tela para todos sai quase de graça: basta todos os aparelhos lerem o mesmo `estado()`.

O que falta:

1. aceitar conexões de outros computadores;
2. saber qual aparelho é dono de qual jogador;
3. recusar ações de quem não está na vez;
4. avisar as outras telas quando o estado muda;
5. mostrar na tela de quem é a vez e os endereços de entrada.

## 5. Quem pode agir em cada momento

O servidor decide pelo **dono da vez**: o jogador que pode agir agora. Se não há dono da vez, qualquer aparelho pode agir.

| Momento (tela / modo) | Dono da vez |
|---|---|
| Escolha (quantidade, nome, personagem, começar, refazer, trocar quantidade) | ninguém: qualquer aparelho |
| Painel "Rodada N" / roleta da rodada 1 | 1º jogador **vivo** da ordem da rodada |
| Turno: ações, alvo, inventário, voltar | jogador da vez |
| Painel do resultado da ação (Continuar) | jogador da vez (quem agiu) |
| Painel "Fim da rodada" | ninguém: qualquer aparelho |
| Painel "O Comerciante chegou" | 1º comprador |
| Estoque, item selecionado, comprar, substituir, Forja, Mistura, sair | comprador da vez |
| Painel "O Comerciante partiu" | ninguém: qualquer aparelho |
| Fim de jogo (Jogar de novo) | ninguém: qualquer aparelho |

Em código (`partida.py`), isso é uma função só, porque `Partida` já sabe de quem é a vez (`self.ordem`/`self.vez` no turno e
`comprador()` na loja):

```python
def dono_da_vez(self):
    """Jogador que pode agir agora (na partida em rede, só o aparelho dele age). None: qualquer um pode
    (escolha dos personagens, fim de jogo, fim de rodada e saída do Comerciante)."""
    if self.tela == "turno":
        vivos = [j for j in self.ordem[self.vez:] if j["vivo"]]
        return vivos[0] if vivos else None
    if self.tela == "loja":
        return self.comprador()
    return None
```

> Por que "1º vivo a partir de `self.vez`" e não `self.atual()`: no painel "Rodada N", `self.vez` é 0 e o primeiro da
> ordem pode estar eliminado (`comecar_turno` só pula os eliminados depois do clique). No painel "Fim da rodada",
> `self.vez` passou do fim da lista, então ninguém é dono.

## 6. Mudanças por arquivo

### 6.1 `partida.py`

1. **`estado()` sem efeito colateral.** Hoje `estado()` apaga `self.aviso` ("o aviso aparece uma vez só"). Com várias telas
   lendo o estado, a primeira leitura apagaria o aviso para as outras. Mudança:
   - tirar `self.aviso = None` de `estado()`;
   - colocar `self.aviso = None` no começo de `agir()`, antes de executar a ação.
   Assim o aviso vale até a próxima ação, e todas as telas o veem igual.
2. **`dono_da_vez()`**: o código do item 5.

Nada mais muda nas regras.

### 6.2 `app.py` (o servidor)

**Classe `Api`** (os atributos com `_` não são expostos ao JavaScript na janela):

```python
class Api:
    def __init__(self, rede=False):
        self._partida = Partida()
        self._janela = None
        self._trava = threading.Lock()   # um pedido de cada vez (janela + todos os navegadores)
        self._tela_cheia = False
        self._donos = {}                 # índice do jogador -> token do aparelho que o criou
        self._versao = 0                 # muda quando o estado muda: as outras telas sabem que precisam redesenhar
        self._rede = enderecos_da_rede() if rede else []
```

- **Token do aparelho:** cada aba do navegador (e a janela) gera um código aleatório e o manda em todo pedido. O servidor
  não precisa de login: o token só diz "este pedido veio do mesmo aparelho que criou a Ana".
- **`estado(token=None)`**: devolve `self._partida.estado()` mais:
  - `versao`: `self._versao`;
  - `dono`: índice do dono da vez (ou `None`);
  - `meus`: índices dos jogadores deste token;
  - `rede`: lista de endereços (vazia fora do modo rede, para a tela de hot-seat não mudar);
  - `anfitriao`: se o pedido veio do próprio computador do jogo (ver abaixo).
- **`versao()`**: devolve só `self._versao`. As telas consultam isso a cada ~0,7 s, porque é barato, e só buscam o estado
  inteiro quando o número muda.
- **`agir(acao, dados=None, token=None)`**, dentro da trava:
  1. `dono = partida.dono_da_vez()`. Se há dono, o token dele está em `_donos` e é diferente do token do pedido, **recusa**:
     não chama `partida.agir` e devolve o estado com `negado: "Agora é a vez de Ana."`.
  2. Guarda `antes = partida.estado()`, chama `partida.agir(acao, dados)` e guarda `depois = partida.estado()`.
  3. Se a ação foi `entrar` e a lista de jogadores cresceu, `_donos[novo_indice] = token`.
  4. Limpa `_donos` dos índices que não existem mais (`refazer`, `trocar_quantidade` e `novo_jogo` esvaziam a lista).
  5. Se `depois != antes`, faz `_versao += 1`. Ação que não mudou nada não mexe na versão, para não reiniciar a animação
     dos dados nas outras telas.
  6. Devolve o estado com os campos extras.
  - `token=None` (chamadas antigas, testes) sempre pode agir: mantém o comportamento de hoje.
- **`assumir(token)`** (só o anfitrião): passa o jogador dono da vez para o token do anfitrião, para quando alguém cair.
  Faz `_versao += 1`.
- **Quem é o anfitrião:** pedidos que vêm pela janela (pywebview chama a `Api` direto) ou por HTTP de `127.0.0.1` / `::1`.
  No servidor HTTP, o handler sabe o IP de quem pediu (`self.client_address[0]`) e passa isso para a `Api`. Na janela, as
  chamadas são sempre do anfitrião.

**Servidor HTTP** (hoje está dentro de `modo_navegador`): separar numa função reaproveitável.

```python
def criar_servidor(api, host="127.0.0.1", porta=PORTA_NAVEGADOR):
    """Serve a interface e a Api por HTTP. host="0.0.0.0" aceita outros computadores (modo rede)."""
    class Pedido(SimpleHTTPRequestHandler):
        ...  # igual ao de hoje, aceitando os métodos "estado", "agir", "versao" e "assumir"
        def do_POST(self):
            metodo = self.path.strip("/").split("/")[-1]
            local = self.client_address[0] in ("127.0.0.1", "::1")
            ...  # chama o método da api com os argumentos do JSON e o "local"
    return ThreadingHTTPServer((host, porta), Pedido)
```

- `--navegador` sem `--rede`: `criar_servidor(api, "127.0.0.1")` e `serve_forever()` (igual a hoje).
- `--navegador --rede`: `criar_servidor(api, "0.0.0.0")`.
- Janela com `--rede`: a janela continua com `js_api=api` e, **na mesma `Api`**, abre o servidor HTTP em `0.0.0.0` numa
  thread: `threading.Thread(target=servidor.serve_forever, daemon=True).start()` antes de `webview.start(...)`.
  Assim a janela do anfitrião e os navegadores dos outros mexem na mesma partida.
- **Porta ocupada** (`OSError` ao criar o servidor): mostrar uma mensagem clara ("a porta 8765 já está em uso: feche a outra
  cópia do jogo").

**Endereços para mostrar na tela:**

```python
def enderecos_da_rede():
    """IPs deste computador que os outros podem usar (Wi-Fi, cabo e VPNs como Radmin e Tailscale)."""
    try:
        ips = socket.gethostbyname_ex(socket.gethostname())[2]
    except OSError:
        ips = []
    return [f"http://{ip}:{PORTA_NAVEGADOR}" for ip in ips if not ip.startswith("127.")]
```

### 6.3 `interface/jogo.js` (a tela)

1. **Detectar o modo navegador** também sem o `?navegador` no endereço, para os amigos poderem abrir só
   `http://IP:8765`: `const NAVEGADOR = params.has("navegador") || location.port === "8765";`
2. **Token do aparelho**, guardado no `localStorage` para sobreviver a recarregar a página e a fechar e reabrir o
   navegador, com `try/catch` porque o armazenamento pode estar bloqueado:
   ```js
   const TOKEN = (() => {
     const novo = () => Math.random().toString(36).slice(2) + Date.now().toString(36);
     try {
       let t = localStorage.getItem("arena-token");
       if (!t) { t = novo(); localStorage.setItem("arena-token", t); }
       return t;
     } catch { return novo(); }
   })();
   ```
   Para testar duas pessoas no mesmo PC, use uma janela normal e uma **janela anônima**, que não dividem o `localStorage`.
3. **Mandar o token:** `chamar("estado", TOKEN)` e `chamar("agir", acao, extra, TOKEN)`.
4. **Acompanhar as outras jogadas**, depois de `iniciar()`:
   ```js
   async function acompanhar() {
     try {
       if (E && !ocupado) {
         const v = await chamar("versao");
         if (v !== E.versao && !ocupado) { anterior = E; E = await chamar("estado", TOKEN); desenhar(); }
       }
     } catch (erro) { /* servidor fora do ar: tenta de novo */ }
     setTimeout(acompanhar, 700);
   }
   ```
   - O `anterior = E` faz quem assiste também ver os cartões **de antes do golpe** enquanto os dados rolam, igual a quem
     atacou (a lógica de `desenharTurno` já usa `anterior`).
   - Na tela de escolha, redesenhar mantém o nome digitado (`nomeDigitado`) e o foco no campo, que já é o comportamento de
     hoje. Conferir no teste que digitar enquanto outra pessoa entra não perde letras.
5. **Bloquear fora da vez:**
   ```js
   const minhaVez = () => !E || E.dono == null || E.meus.includes(E.dono);
   ```
   - No `click`: se a ação não é `local:` (tela cheia, marcar personagem, entrar) e não é minha vez, ignora e mostra
     "Agora é a vez de Ana".
   - No `keydown`: depois de F11 e Esc, se não é minha vez e o foco não está num campo de texto, ignora.
   - O servidor recusa de qualquer jeito (item 6.2). O bloqueio na tela só evita cliques que não fazem nada.
6. **Faixa de vez** (só quando `E.rede.length > 0`, para a tela de hot-seat ficar igual): no topo da área principal,
   - minha vez: `⭐ Sua vez`;
   - assistindo: `👀 Vez de ● Ana: você está assistindo`;
   - anfitrião assistindo: mais o botão `Assumir a vez de Ana` (chama `assumir`).
   No `<body>`, a classe `assistindo` deixa os botões da área principal sem reação ao mouse (`pointer-events: none`), sem
   mudar a aparência: a tela continua igual para todos.
7. **Ação recusada:** se o estado voltar com `negado`, mostrar o texto numa faixa só neste aparelho (não muda a partida).
8. **Endereços** (`E.rede`): na tela inicial (quantos jogadores), um bloco "🌐 Outros jogadores entram em:" com cada
   endereço. Na escolha dos personagens, uma linha discreta com o primeiro endereço.

### 6.4 `interface/estilo.css`

- `.faixa-vez` (cartão claro com borda à esquerda) e `.faixa-vez.minha` (borda e fundo com o dourado `--ouro`);
- `.assistindo #principal button { pointer-events: none; }`;
- `.enderecos code` (endereço em fonte monoespaçada, fácil de ditar);
- faixa de recusa: reaproveitar `.aviso-faixa.erro`.

### 6.5 Atalhos e executável

- Novo `jogar_em_rede.bat`:
  ```bat
  @echo off
  cd /d "%~dp0"
  if exist "dist\ArenaDeCombate.exe" (start "" "dist\ArenaDeCombate.exe" --rede) else (python app.py --rede)
  ```
- `gerar_exe.bat` não muda: o `.exe` recebe o `--rede` como argumento normal.
- O `.exe` precisa ser gerado de novo depois da mudança.

### 6.6 `README.md`

Seção "Jogar em rede": como abrir (item 2), como conectar (tabela do item 3), firewall e o que fazer se alguém cair.
Atualizar a tabela de arquivos (`app.py` e `jogar_em_rede.bat`).

## 7. Casos difíceis (e o que fazer)

| Caso | Comportamento planejado |
|---|---|
| Alguém recarrega a página | Mesmo token (`localStorage`): continua dono dos seus jogadores |
| Alguém fecha o navegador ou o PC trava | Se voltar no mesmo navegador, continua dono. Se não der, o anfitrião usa **Assumir a vez** e joga por ele (ou passa a vez) |
| Duas pessoas apertam "Entrar" ao mesmo tempo | A trava do servidor ordena: uma vira o Jogador N e a outra o N+1 |
| Alguém tenta agir fora da vez (teclado, clique ou pedido direto) | A tela ignora; o servidor recusa com "Agora é a vez de X" |
| Jogador eliminado | Continua assistindo; nunca mais é dono da vez |
| Mensagem de erro (ex.: "nome vazio") | Aparece para todos até a próxima ação (é a mesma tela) |
| Dados rolando | Quem assiste vê os mesmos dados com até ~0,7 s de atraso. O "Continuar" de quem atacou só aparece depois da animação (3 s por dado), então todos veem o resultado |
| Refazer / trocar quantidade / jogar de novo | Os donos são apagados junto com os jogadores; cada um entra de novo |
| Anfitrião fecha o jogo | A partida acaba para todos (o servidor é o PC do anfitrião). Fora do escopo: salvar e retomar |
| Várias cópias do jogo no mesmo PC | A segunda não consegue abrir a porta 8765: mensagem clara (item 6.2) |
| Todos os jogadores no mesmo PC (hot-seat) | Um token só é dono de todos: funciona como hoje |

## 8. Segurança

- Sem senha: pensado para amigos numa rede de confiança (casa ou VPN).
- Quem tem o endereço consegue entrar na escolha de personagens e assistir. Depois que a partida começa, só os donos agem.
- Com túnel público (Cloudflare/ngrok), o link funciona para qualquer pessoa: não postar o link.
- Melhoria futura simples: código de sala de 4 dígitos mostrado na tela do anfitrião e pedido na entrada.

## 9. Testes

**No mesmo PC** (`python app.py --navegador --rede`): janela normal em `http://localhost:8765` e janela anônima em
`http://<IP mostrado>:8765`.

- [ ] Os endereços aparecem na tela inicial.
- [ ] Cada janela cria o seu jogador; as duas veem os dois prontos.
- [ ] Na vez do jogador A, a janela B mostra "👀 Vez de A" e ignora teclas e cliques.
- [ ] Mandar `agir` direto pelo console da janela B, fora da vez: o servidor recusa e a partida não muda.
- [ ] Ataque: as duas janelas mostram o confronto e os dados rolando, e depois o mesmo resultado.
- [ ] Comerciante: só o comprador da vez compra, usa a Forja/Mistura e sai.
- [ ] Recarregar a janela B no meio da partida: continua dona do jogador B.
- [ ] Fechar a janela B: o anfitrião usa "Assumir a vez" e a partida continua.
- [ ] Fim de jogo e "Jogar de novo" em qualquer janela: as duas voltam para a escolha.
- [ ] Hot-seat (sem `--rede`, um PC): nada mudou na tela nem no teclado.

**Em dois PCs** na mesma rede e depois **pela VPN** (Radmin ou Tailscale): repetir os principais itens acima e conferir
o firewall.

**Regressão:**

- [ ] `python simulacao/simular.py teste` e `python main.py`: o terminal não muda.
- [ ] Uma partida inteira na janela sem rede.

## 10. Ordem de implementação (≈ 3 a 5 horas)

1. `partida.py`: `estado()` sem efeito colateral e `dono_da_vez()` (15 min). Testar uma partida comum.
2. `app.py`: `criar_servidor`, flag `--rede`, `enderecos_da_rede`, token, `_donos`, `_versao`, recusa fora da vez
   (1 h 30). Testar com `curl`/console do navegador.
3. `jogo.js`: token, `acompanhar()`, bloqueio fora da vez, faixa de vez, endereços (1 h 30).
4. `estilo.css`: faixa, assistindo, endereços (20 min).
5. "Assumir a vez" no anfitrião (30 min).
6. `jogar_em_rede.bat`, README, gerar o `.exe` de novo (20 min).
7. Testes do item 9 (1 h).

## 11. Depois desta etapa (ideias)

- **Loja simultânea:** cada um já tem o próprio estoque. Em rede, todos podem comprar ao mesmo tempo, o que acelera muito a
  partida (exige que `Partida` guarde um modo/seleção por comprador, não um só).
- **Telas por jogador:** a pessoa vê o próprio inventário e a própria ficha enquanto assiste.
- **Informação escondida:** ouro e itens dos outros ocultos.
- **Tempo de turno** (ex.: 60 s) com passar a vez automático.
- **Salvar e retomar** a partida se o anfitrião cair.
- **Servidor na nuvem** com várias salas. Exige tirar o estado global da partida: hoje `main.ELIMINADOS` e
  `main.RODADA_ATUAL` são do programa inteiro, então só cabe uma partida por processo.

## Anexo: outras pendências desta rodada de ajustes (fora do modo em rede)

- **Partidas sem fim:** sem a morte súbita, ~10% das partidas simuladas passam de 150 rodadas. Decidir uma proteção que
  só entre em partidas muito longas (ex.: curas rendendo 5% a menos por rodada a partir da rodada 50; na simulação, a
  versão a partir da rodada 25 deixou as partidas com ~44 rodadas simuladas, ≈ 35 reais, e nenhuma travou).
- **Rodar a simulação de novo** com as fases novas (Mid na 15, Late na 25), que ainda não foram simuladas:
  `python simulacao/simular.py massa 3000 _fases`. Comparar com `simulacao/resultados_loja.json`.
- **Equilíbrio na última simulação** (antes da mudança das fases; vitórias ÷ esperado, 4 jogadores): Bárbaro 1,55,
  Goblin 1,34, Feiticeiro 1,04, Ferreiro 0,98, Alquimista 0,78, Hemomante 0,74, Mosqueteiro 0,57.
  O Mosqueteiro caiu com o Recarregar sem defesa.
- **Poção Reforçada** continua entrando na rodada 20 (era o início do Late antigo). Decidir se passa para a 25 (constante
  `RODADA_POCAO_REFORCADA` em `shop.py`).
- **Armadura da Provação** perdeu a Leitura de Combate e continua custando 125 (a Mithril custa 100).
- **Inventário na janela:** os itens guardam o emoji dentro do nome, então o cartão do inventário não tem o espaço
  separado do ícone que os outros cartões têm.
- **Simulador:** aviso conhecido "bomba/raio atinge alvo em postura ou com Escudo de Mana sem consumir a defesa".
- **Gerar o `.exe` de novo** (`gerar_exe.bat`) para ele ter todas as mudanças.
