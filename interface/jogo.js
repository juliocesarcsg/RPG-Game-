/* Arena de Combate · interface da janela.
   Desenha o estado que o Python (partida.py) devolve e manda cada clique de volta. Nenhuma regra do jogo fica
   aqui: só o desenho das telas, a animação dos dados e da roleta e os atalhos de teclado. */
"use strict";

let E = null;                  // último estado recebido do Python
let anterior = null;           // estado de antes: os cartões só mostram o resultado depois que os dados param
let ocupado = false;           // ignora cliques enquanto o Python responde
let animacao = 0;              // muda a cada desenho, para uma animação antiga parar
let telaCheia = false;
let personagemMarcado = null;  // tela de escolha: personagem destacado (só na interface, até confirmar)
let nomeDigitado = "";
const NAVEGADOR = new URLSearchParams(location.search).has("navegador");

// Mesmo ritmo do animar_dado do terminal: 24 trocas de número, desacelerando, em 3 segundos por dado
const DURACAO_DADO = 3000;
const ATRASOS_DADO = Array.from({ length: 24 }, (_, i) => 0.05 * 1.08 ** i);
const SOMA_ATRASOS = ATRASOS_DADO.reduce((s, a) => s + a, 0);

const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = x => String(x).replace(".", ",");
const espera = ms => new Promise(r => setTimeout(r, ms));
const d10 = () => 1 + Math.floor(Math.random() * 10);
const dados = obj => esc(JSON.stringify(obj));

/* =====================================================================
   COMUNICAÇÃO COM O PYTHON
   ===================================================================== */
async function chamar(metodo, ...args) {
  if (!NAVEGADOR) return window.pywebview.api[metodo](...args);
  const r = await fetch("/api/" + metodo, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(args),
  });
  return r.json();
}

async function agir(acao, extra = {}) {
  if (ocupado) return;
  ocupado = true;
  try {
    anterior = E;
    E = await chamar("agir", acao, extra);
    desenhar();
  } catch (erro) {
    console.error(erro);
  } finally {
    ocupado = false;
  }
}

async function iniciar() {
  E = await chamar("estado");
  desenhar();
}

async function alternarTelaCheia(ligar) {
  if (NAVEGADOR) {
    if (document.fullscreenElement && ligar !== true) await document.exitFullscreen();
    else if (!document.fullscreenElement && ligar !== false) await document.documentElement.requestFullscreen();
    return;
  }
  telaCheia = await chamar("tela_cheia", ligar === undefined ? null : ligar);
  atualizarBotaoTela();
}

document.addEventListener("fullscreenchange", () => { telaCheia = !!document.fullscreenElement; atualizarBotaoTela(); });

function atualizarBotaoTela() {
  const b = $("btn-tela");
  if (b) b.textContent = telaCheia ? "⛶ Sair da tela cheia (F11)" : "⛶ Tela cheia (F11)";
}

/* =====================================================================
   PEÇAS REUTILIZADAS
   ===================================================================== */
function barraVida(v, max, grossa) {
  const r = max ? v / max : 0;
  const cor = r > .5 ? "var(--vida-alta)" : r > .25 ? "var(--vida-media)" : "var(--vida-baixa)";
  return `<div class="barra ${grossa ? "grossa" : ""}"><div style="width:${Math.max(0, r * 100)}%;background:${cor}"></div></div>`;
}

// Caixa de cima: uma coluna por jogador (cartões mais compactos com 5 ou 6)
function gradeJogadores(cartoes) {
  return `<div class="jogadores ${cartoes.length > 4 ? "muitos" : ""}" style="--n:${cartoes.length}">${cartoes.join("")}</div>`;
}

function cartao(j, ativo) {
  return `<div class="cj ${ativo ? "ativo" : ""} ${j.vivo ? "" : "morto"}" style="--cor:${j.cor}" title="${esc(j.dica)}">
    <div class="cj-cab"><span class="cj-emoji">${j.emoji}</span>
      <div class="cj-nome"><b>${esc(j.nome)}</b><small>${esc(j.personagem)}</small></div></div>
    ${barraVida(j.vida, j.max)}
    <div class="cj-linha"><span>💖 ${j.vida}/${j.max}</span><span>💰 ${j.ouro}</span></div>
    <div class="cj-status">${j.curto.map(esc).join(" · ")}</div>
  </div>`;
}

function linhaOrdem(ordem) {
  return ordem.map((o, i) => `<span class="item ${o.estado}">${i + 1}º ${esc(o.nome)}</span>`)
    .join(`<span class="seta">➜</span>`);
}

// Bolinha com a cor do jogador ao lado do nome (o nome fica na cor do texto, legível em qualquer fundo)
const marca = cor => `<span class="marca" style="--cor:${cor}"></span>`;

// Caixa de cima: título e metadados na mesma linha, depois a ordem da rodada e os jogadores
function desenharTopo(titulo, meta, ordem, jogadores) {
  $("topo").innerHTML = `
    <div class="topo-linha">
      <h1>${titulo}</h1>
      ${meta ? `<span class="meta">${meta}</span>` : ""}
      <button class="btn-tela" id="btn-tela" data-acao="local:tela-cheia"></button>
    </div>
    <div class="ordem">${ordem || ""}</div>
    ${jogadores || ""}`;
  atualizarBotaoTela();
}

const cartoesDaPartida = () => gradeJogadores(E.jogadores.map(j => cartao(j, j.indice === E.atual)));

function avisoHtml() {
  if (!E.aviso) return "";
  const erro = E.aviso.tipo === "erro";
  return `<div class="aviso-faixa ${erro ? "erro" : ""}">${erro ? "✖ " : ""}${E.aviso.texto}</div>`;
}

function registroHtml() {
  return `<ol class="registro">${E.registro.map(l => `<li>${l}</li>`).join("") || `<li>Nada aconteceu ainda.</li>`}</ol>`;
}

let contadorTecla = 0;  // números dos atalhos (1-9) na ordem em que os botões aparecem
// Toda opção numerada conta, mesmo bloqueada (ativa = false: número apagado e a tecla não faz nada),
// para os números das outras opções não mudarem de lugar. O botão leva data-atalho mesmo quando desabilitado.
function tecla(ativa = true) {
  contadorTecla++;
  return contadorTecla <= 9 ? `<span class="tecla ${ativa ? "" : "inativa"}">${contadorTecla}</span>` : "";
}

// Identificação da ficha: espaço do retrato (futura ilustração; hoje o emoji), nome e personagem
function fichaId(nome, emoji, personagem, cor) {
  return `<div class="ficha-id">
      <div class="retrato" title="Retrato do personagem">${emoji}</div>
      <div><h2>${cor ? marca(cor) : ""}${esc(nome)}</h2>${personagem ? `<div class="quem">${esc(personagem)}</div>` : ""}</div>
    </div>`;
}

// Ficha lateral do jogador: identificação, atributos, equipamentos e informações da rodada
function painelJogador(p, tag) {
  const vazio = `<span class="vazio">—</span>`;
  const defesaDica = p.defesa.endsWith("*") ? " (com ácido ou Defesa temporária)" : "";
  return `
    ${tag ? `<div class="vencedor-tag">${tag}</div>` : ""}
    ${fichaId(p.nome, p.emoji, p.personagem, p.cor)}
    <div class="ficha-bloco">
      <div class="ficha-vida"><span class="rotulo">💖 Vida</span><span class="valor">${p.vida}/${p.max}</span></div>
      ${barraVida(p.vida, p.max, true)}
      <dl class="stats">
        <div><dt>🔪 Físico</dt><dd>${num(p.fis)}</dd></div>
        <div><dt>🌠 Mágico</dt><dd>${num(p.mag)}</dd></div>
        <div title="Defesa${defesaDica}"><dt>🔰 Defesa</dt><dd>${num(p.defesa)}</dd></div>
        <div><dt>💰 Ouro</dt><dd>${p.ouro}</dd></div>
      </dl>
      ${p.recurso ? `<p class="ficha-linha">${p.recurso}</p>` : ""}
      ${p.buffs ? `<p class="ficha-linha">${p.buffs}</p>` : ""}
    </div>
    <div class="ficha-bloco">
      <h3 class="ficha-titulo">Equipamentos</h3>
      <dl class="equip">
        ${p.espacos.map(s => `<div><dt>${esc(s.rotulo)} <span>${s.usados}/${s.limite}</span></dt>
          <dd>${s.itens.join("<br>") || vazio}</dd></div>`).join("")}
        <div><dt>Consumíveis</dt><dd>${p.consumiveis.join("<br>") || vazio}</dd></div>
      </dl>
    </div>
    ${p.info.length ? `<div class="ficha-bloco"><ul class="lista">${p.info.map(l => `<li>${l}</li>`).join("")}</ul></div>` : ""}`;
}

function lateralOrdem() {
  return `<h2>Rodada ${E.rodada}</h2>
    <div class="ficha-bloco"><h3 class="ficha-titulo">Ordem da rodada</h3>
    <ul class="lista">${(E.ordem || []).map((o, i) => {
      const j = E.jogadores.find(x => x.nome === o.nome);
      return `<li>${i + 1}º ${marca(j.cor)}${esc(o.nome)} · ${j.emoji} ${esc(j.personagem)}${j.vivo ? "" : " 💀"}</li>`;
    }).join("")}</ul></div>`;
}

/* ---------- painel: resultado de ação, anúncio de rodada, Comerciante ---------- */
// Quem ataca e quem é atacado, acima dos dados (aparece já durante a rolagem)
function confrontoHtml(c) {
  const lado = (j, papel) => `<div class="lado" style="--cor:${j.cor}">
      <span class="icone">${j.emoji}</span>
      <div><span class="papel">${papel}</span><span class="nome-item">${esc(j.nome)}</span><small>${esc(j.personagem)}</small></div>
    </div>`;
  return `<div class="confronto">${lado(c.atacante, "Ataca")}<span class="versus">⚔️</span>${lado(c.alvo, "É atacado")}</div>`;
}

function painelHtml(p) {
  const animado = p.dados.length > 0 || !!p.roleta;
  return `
    <div class="cab"><h2>${p.titulo}</h2></div>
    ${p.confronto ? confrontoHtml(p.confronto) : ""}
    ${p.roleta ? `<div class="roleta" id="roleta">🎲</div>` : ""}
    ${p.dados.length ? `<div class="dados">${p.dados.map((d, i) => `
      <div><div class="dado esperando" id="dado${i}" style="--cor:${d.cor}">?</div>
      <div class="dado-legenda">${esc(d.legenda)}</div></div>`).join("")}</div>` : ""}
    <div class="resultado" id="resultado" ${animado ? "hidden" : ""}>
      ${p.linhas.map(l => l ? `<div>${l}</div>` : `<div class="vazia"></div>`).join("")}
    </div>
    <div class="botoes" id="continuar-box" ${animado ? "hidden" : ""}>
      <button class="btn forte" id="continuar" data-acao="continuar" data-enter>${esc(p.botao)} (Enter)</button>
    </div>`;
}

async function animarPainel(p) {
  const minha = animacao;
  if (p.roleta) await animarRoleta(p.roleta, minha);
  for (let i = 0; i < p.dados.length; i++) {  // um dado de cada vez
    const el = $("dado" + i);
    if (!el || minha !== animacao) return;
    el.classList.remove("esperando");
    el.classList.add("rolando");
    for (const a of ATRASOS_DADO) {
      if (minha !== animacao) return;
      el.textContent = d10();
      await espera(a / SOMA_ATRASOS * DURACAO_DADO);
    }
    el.textContent = p.dados[i].valor;
    el.classList.remove("rolando");
  }
  if (minha !== animacao) return;
  const res = $("resultado"), box = $("continuar-box");
  if (res) res.hidden = false;
  if (box) { box.hidden = false; $("continuar").focus(); }
  if (p.dados.length) desenharTopoTurno(E);  // agora sim: vida e estados depois do golpe
}

// Roleta da rodada 1: os nomes passam desacelerando e param no sorteado (como no terminal)
async function animarRoleta(r, minha) {
  const el = $("roleta");
  const passos = 28, n = r.nomes.length;
  const inicio = ((r.vencedor - (passos - 1)) % n + n) % n;
  let atraso = 50;
  for (let i = 0; i < passos; i++) {
    if (minha !== animacao || !el) return;
    const k = (inicio + i) % n;
    el.innerHTML = `👉 ${marca(r.cores[k])}${esc(r.nomes[k])} 👈`;
    await espera(atraso);
    atraso *= 1.09;
  }
  el.innerHTML = `🏁 ${marca(r.cores[r.vencedor])}${esc(r.nomes[r.vencedor])} começa! 🏁`;
  await espera(500);
}

/* =====================================================================
   TELA 1 — ESCOLHA DOS JOGADORES
   ===================================================================== */
function desenharEscolha() {
  if (!E.quantidade) {
    desenharTopo("⚔️ Arena de Combate", "RPG PvP em turnos · de 2 a 6 jogadores no mesmo teclado", "", "");
    let botoes = "";
    for (let n = E.min; n <= E.max; n++) {
      botoes += `<button class="btn forte grande" data-acao="quantidade" data-dados="${dados({ n })}" data-tecla="${n}">${n}</button>`;
    }
    $("principal").innerHTML = `
      <div class="cab"><h2>Quantos jogadores vão jogar?</h2></div>
      <p class="nota">Todos jogam no mesmo computador, cada um na sua vez. Aperte o número no teclado ou clique.</p>
      <div class="botoes">${botoes}</div>`;
    $("lateral").innerHTML = `
      <div class="boas-vindas">
        <h2>📜 Como jogar</h2>
        <p>⚔️ Cada um escolhe um personagem. Vence quem sobrar vivo.</p>
        <p>🎲 Na sua vez: atacar, defender, usar itens ou passar. O D10 decide a força do golpe.</p>
        <p>🧳 A cada 5 rodadas chega o Comerciante: cada jogador compra 1 equipamento e 1 consumível.</p>
        <p>⌨️ Números escolhem, 0 volta, Enter continua. F11 liga e desliga a tela cheia.</p>
      </div>`;
    return;
  }

  const q = E.quantidade, n = E.jogadores.length;
  const vagas = [];
  for (let i = 0; i < q; i++) {
    const j = E.jogadores[i];
    if (j) {
      vagas.push(`<div class="cj" style="--cor:${j.cor}"><div class="cj-cab"><span class="cj-emoji">${j.emoji}</span>
        <div class="cj-nome"><b>${esc(j.nome)}</b><small>${esc(j.personagem)} · pronto ✔</small></div></div></div>`);
    } else if (i === n) {
      vagas.push(`<div class="cj" style="--cor:${E.cores[i]}"><div class="cj-cab"><span class="cj-emoji">❔</span>
        <div class="cj-nome"><b>Jogador ${i + 1}</b><small>escolhendo...</small></div></div></div>`);
    } else {
      vagas.push(`<div class="cj vaga">Jogador ${i + 1}</div>`);
    }
  }
  desenharTopo("⚔️ Arena de Combate",
    `${q} jogadores · ${n < q ? `jogador <b>${n + 1} de ${q}</b> escolhendo` : "<b>todos prontos</b>"}`,
    "", gradeJogadores(vagas));

  if (n >= q) {
    $("principal").innerHTML = `
      <div class="cab"><h2>Tudo pronto!</h2></div>
      <p class="nota">Os ${q} jogadores escolheram. A roleta vai sortear quem começa.</p>
      <div class="botoes">
        <button class="btn forte grande" data-acao="comecar" data-enter>🎲 Começar a partida (Enter)</button>
        <button class="btn" id="voltar" data-acao="refazer">Refazer as escolhas (0)</button>
      </div>`;
    $("lateral").innerHTML = `<h2>Jogadores</h2><div class="ficha-bloco"><ul class="lista">${
      E.jogadores.map(j => `<li>${marca(j.cor)}${esc(j.nome)} · ${j.emoji} ${esc(j.personagem)}</li>`).join("")}</ul></div>`;
    return;
  }

  if (!E.personagens.some(p => p.nome === personagemMarcado)) personagemMarcado = E.personagens[0].nome;
  $("principal").innerHTML = `
    <div class="cab"><h2>${marca(E.cores[n])}Jogador ${n + 1}</h2>
      <div class="botoes">
        ${n > 0 ? `<button class="btn" data-acao="refazer">Refazer</button>` : ""}
        <button class="btn" data-acao="trocar_quantidade">Trocar a quantidade (${q})</button>
      </div></div>
    ${avisoHtml()}
    <label class="campo">📝 Nome
      <input id="nome" maxlength="20" placeholder="Digite o seu nome" value="${esc(nomeDigitado)}" autocomplete="off"></label>
    <p class="secao">Personagens <span class="nota">· <span class="tecla tecla-texto">↑</span> <span class="tecla tecla-texto">↓</span>
      trocam (ou clique) · Enter entra</span></p>
    <div class="grade">${E.personagens.map(p => `
      <button class="opcao ${personagemMarcado === p.nome ? "selecionada" : ""}" data-acao="local:marcar" data-p="${esc(p.nome)}">
        <div class="topo-opcao"><span class="icone">${p.emoji}</span><span class="nome-item">${esc(p.nome)}</span></div>
        <small>💖 ${p.vida} · ataque ${num(Math.round((p.fis + p.mag) * 10) / 10)} · ${esc(p.estilo)}</small>
        <small>${esc(p.descricao)}</small>
      </button>`).join("")}</div>
    <div class="botoes">
      <button class="btn forte" data-acao="local:entrar" data-enter>✅ Entrar como ${esc(personagemMarcado)} (Enter)</button>
    </div>`;
  const campo = $("nome");
  campo.addEventListener("input", () => { nomeDigitado = campo.value; });
  campo.focus();
  campo.setSelectionRange(campo.value.length, campo.value.length);

  const p = E.personagens.find(x => x.nome === personagemMarcado);
  const barra = (v, max, cor) => `<div class="barra"><div style="width:${Math.min(100, v / max * 100)}%;background:${cor}"></div></div>`;
  const atributo = (rotulo, valor, max, cor) => `<li><div class="ficha-vida"><span class="rotulo">${rotulo}</span>
    <span class="valor">${valor}</span></div>${barra(valor, max, cor)}</li>`;
  $("lateral").innerHTML = `
    ${fichaId(p.nome, p.emoji, p.estilo)}
    <div class="ficha-bloco">
      <ul class="lista">
        ${atributo("💖 Vida", p.vida, 150, "var(--vida-alta)")}
        ${atributo("🔪 Físico", num(p.fis), 10, "#c96a55")}
        ${atributo("🌠 Mágico", num(p.mag), 10, "#a77bc4")}
      </ul>
      <p class="nota" style="margin-top:var(--e2)">Dano já com o item inicial.</p>
    </div>
    <div class="bloco"><span class="rotulo">✨ Passiva</span><p>${p.passiva}</p></div>
    ${p.habilidade ? `<div class="bloco"><span class="rotulo">🌟 Habilidade</span><p>${p.habilidade}</p></div>` : ""}
    <div class="bloco"><span class="rotulo">🔰 Postura defensiva</span><p>${p.postura}</p></div>
    <div class="bloco"><span class="rotulo">🎒 Item inicial</span><p>${p.itens.join("<br>")}</p></div>`;
}

/* =====================================================================
   TELA 2 — TURNO
   ===================================================================== */
// Caixa de cima e caixa da direita do turno. Enquanto os dados rolam, mostram o estado de antes do golpe.
function desenharTopoTurno(base) {
  const cartoes = gradeJogadores(base.jogadores.map(j => cartao(j, j.indice === base.atual)));
  desenharTopo(`Rodada ${E.rodada}`, "", linhaOrdem(E.ordem), cartoes);
  $("lateral").innerHTML = base.lateral ? painelJogador(base.lateral) : lateralOrdem();
}

function desenharTurno() {
  const rolando = E.modo === "painel" && E.painel.dados.length && anterior && anterior.jogadores && anterior.lateral;
  desenharTopoTurno(rolando ? anterior : E);

  if (E.modo === "painel") {
    $("principal").innerHTML = painelHtml(E.painel);
    if (E.painel.dados.length || E.painel.roleta) animarPainel(E.painel);
    else $("continuar").focus();
    return;
  }
  const j = E.jogadores[E.atual];
  const cab = `<div class="cab"><h2>Turno de ${marca(j.cor)}${esc(j.nome)}</h2>
    <span class="etiqueta">${j.emoji} ${esc(j.personagem)}</span></div>`;

  if (E.modo === "acoes") {
    $("principal").innerHTML = cab + registroHtml() + avisoHtml() + `
      <p class="secao">Escolha sua ação</p>
      <div class="acoes">${E.acoes.map(a => `
        <button class="acao ${a.livre ? "livre" : ""}" data-acao="acao" data-dados="${dados({ id: a.id })}"
                data-atalho ${a.bloqueio ? "disabled" : ""}>
          ${tecla(!a.bloqueio)}
          <span class="acao-texto"><strong>${esc(a.nome)}${a.livre ? `<span class="pill-livre">ação livre</span>` : ""}</strong>
          <small>${a.bloqueio ? `<span class="motivo">${esc(a.bloqueio)}</span>` : esc(a.desc)}</small></span>
        </button>`).join("")}</div>`;
  } else if (E.modo === "alvo") {
    $("principal").innerHTML = cab + avisoHtml() + `
      <p class="secao">${esc(E.alvos.titulo)}</p>
      <div class="grade">${E.alvos.lista.map(o => `
        <button class="opcao com-cor" data-acao="alvo" data-dados="${dados({ indice: o.indice })}" style="--cor:${o.cor}"
                data-atalho ${o.bloqueio ? "disabled" : ""}>
          <div class="topo-opcao">${tecla(!o.bloqueio)}<span class="icone">${o.emoji}</span><span class="nome-item">${esc(o.nome)}</span></div>
          ${barraVida(o.vida, o.max)}
          <small>💖 ${o.vida}/${o.max} · 🔰 Defesa ${num(o.defesa)} · 💰 ${o.ouro}</small>
          <small>${o.bloqueio ? `<span class="motivo">${esc(o.bloqueio)}</span>` : o.status.join(" · ")}</small>
        </button>`).join("")}</div>
      <div class="botoes"><button class="btn" id="voltar" data-acao="voltar">🔙 Voltar (0)</button></div>`;
  } else if (E.modo === "inventario") {
    $("principal").innerHTML = cab + avisoHtml() + `
      <p class="secao">🎒 Inventário</p>
      <div class="grade">${E.inventario.map(it => {
        const clicavel = it.usavel && !it.bloqueio;
        const uso = it.usavel ? (it.livre ? " · 🆓 ação livre" : it.alvo ? " · escolhe um alvo" : " · gasta o turno") : "";
        return `<button class="opcao ${it.usavel ? "" : "fixa"}" data-acao="usar" data-dados="${dados({ indice: it.indice })}"
                  ${it.usavel ? "data-atalho" : ""} ${clicavel ? "" : "disabled"}>
          <div class="topo-opcao">${it.usavel ? tecla(clicavel) : ""}${it.emoji ? `<span class="icone">${it.emoji}</span>` : ""}
            <span class="nome-item">${it.nome}</span></div>
          <span class="tipo" style="--tcor:${it.cor}">${esc(it.tipo)}${uso}</span>
          <ul class="efeitos">${it.efeitos.map(l => `<li>${l}</li>`).join("")}</ul>
          <span class="estado">${it.bloqueio ? `<span class="motivo">${esc(it.bloqueio)}</span>` : esc(it.estado)}</span>
        </button>`;
      }).join("") || `<p class="nota">Inventário vazio.</p>`}</div>
      <div class="botoes"><button class="btn" id="voltar" data-acao="voltar">🔙 Voltar (0)</button></div>`;
  }
}

/* =====================================================================
   TELA 3 — COMERCIANTE
   ===================================================================== */
function desenharLoja() {
  const L = E.loja;
  desenharTopo("🧳 O Comerciante", `Rodada ${L.rodada} · fase <b>${esc(L.fase)}</b>`, linhaOrdem(L.ordem), cartoesDaPartida());
  $("lateral").innerHTML = E.lateral ? painelJogador(E.lateral)
    : `<h2>🧳 O Comerciante</h2><p class="nota" style="margin-top:var(--e2)">Todos já passaram pelo Comerciante.</p>`;

  if (E.modo === "painel") {
    $("principal").innerHTML = painelHtml(E.painel);
    $("continuar").focus();
    return;
  }
  const j = E.jogadores[E.atual];
  const cab = `<div class="cab"><h2>Estoque de ${marca(j.cor)}${esc(j.nome)}</h2>
    <div class="chips">${L.compras.map(c => `<span class="chip ${c.feitas >= c.limite ? "esgotado" : ""}">${esc(c.rotulo)} ${c.feitas}/${c.limite}</span>`).join("")}</div></div>`;
  const voltar = `<div class="botoes"><button class="btn" id="voltar" data-acao="voltar">🔙 Voltar (0)</button></div>`;

  if (E.modo === "substituir") {
    $("principal").innerHTML = cab + avisoHtml() + `<p class="secao">${esc(L.substituir.titulo)}</p>
      <div class="grade">${L.substituir.lista.map(c => `
        <button class="opcao" data-acao="substituir" data-dados="${dados({ indice: c.indice })}" data-atalho>
          <div class="topo-opcao">${tecla()}<span class="nome-item">${c.nome}</span></div>
          <ul class="efeitos">${c.efeitos.map(l => `<li>${l}</li>`).join("")}</ul>
        </button>`).join("")}</div>` + voltar;
    return;
  }
  if (E.modo === "forja") {
    $("principal").innerHTML = cab + avisoHtml() + `<p class="secao">${esc(L.forja.titulo)}</p>
      <div class="grade">${L.forja.lista.map(c => `
        <button class="opcao" data-acao="forjar" data-dados="${dados({ indice: c.indice })}" data-atalho>
          <div class="topo-opcao">${tecla()}<span class="nome-item">${c.nome}</span><span class="preco">🔨 ${c.nivel}/${c.max}</span></div>
          <ul class="efeitos">${c.efeitos.map(l => `<li>${l}</li>`).join("")}</ul>
        </button>`).join("")}</div>` + voltar;
    return;
  }
  if (E.modo === "mistura") {
    const esc2 = L.mistura.escolhidos;
    $("principal").innerHTML = cab + avisoHtml() + `
      <p class="secao">🔬 Mistura · escolha 2 consumíveis (${esc2.length}/2)</p>
      <div class="grade">${L.mistura.lista.map(c => {
        const vezes = esc2.filter(x => x === c.indice).length;
        return `<button class="opcao ${vezes ? "selecionada" : ""}" data-acao="ingrediente" data-dados="${dados({ indice: c.indice })}" data-atalho>
          <div class="topo-opcao">${tecla()}<span class="nome-item">${c.nome}</span><span class="preco">${vezes ? `✔ ${vezes > 1 ? "×2" : ""}` : ""}</span></div>
          <span class="tipo">${c.usos} uso(s)</span>
          <ul class="efeitos">${c.efeitos.map(l => `<li>${l}</li>`).join("")}</ul>
        </button>`;
      }).join("")}</div>
      <div class="botoes">
        <button class="btn forte" data-acao="misturar" data-enter ${esc2.length === 2 ? "" : "disabled"}>🔬 Misturar (Enter)</button>
        <button class="btn" id="voltar" data-acao="voltar">🔙 Voltar (0)</button>
      </div>`;
    return;
  }

  // estoque
  const s = L.selecionado;
  $("principal").innerHTML = cab + `
    <p class="nota">Estoque sorteado só para ${esc(j.nome)}.${L.esgotadas ? " Você já fez as suas compras desta visita." : ""}</p>
    ${avisoHtml()}
    <div class="grade">${L.estoque.map(it => `
      <button class="opcao ${s && s.indice === it.indice ? "selecionada" : ""}" data-acao="item" data-dados="${dados({ indice: it.indice })}"
              data-atalho ${it.disponivel ? "" : "disabled"}>
        <div class="topo-opcao">${tecla(it.disponivel)}<span class="icone">${it.emoji}</span>
          <span class="preco">${it.disponivel ? `💰 ${it.preco}` : "Vendido"}</span></div>
        <span class="nome-item ${it.disponivel ? "" : "vendido"}">${esc(it.nome)}</span>
        <span class="tipo" style="--tcor:${it.cor}">${esc(it.tipo)} · ${it.fixa ? "sempre à venda" : esc(it.fase)}</span>
        <ul class="efeitos">${it.efeitos.map(l => `<li>${l}</li>`).join("")}</ul>
      </button>`).join("")}</div>
    ${s ? `<div class="detalhe">
      <h3>${s.emoji} ${esc(s.nome)} <span class="tipo">${esc(s.tipo)} · ${esc(s.fase)}</span></h3>
      <p class="descricao">${esc(s.descricao)}</p>
      <ul class="efeitos">${s.efeitos.map(l => `<li>✨ ${l}</li>`).join("")}</ul>
      ${s.detalhes.map(l => `<p>${l}</p>`).join("")}
      <p>💰 Preço: <b class="${s.pode_pagar ? "pode" : "nao-pode"}">${s.preco} moedas</b> (você tem ${j.ouro})</p>
      <div class="botoes">
        <button class="btn forte" id="comprar" data-acao="comprar" data-enter ${s.bloqueio ? "disabled" : ""}>✅ Comprar (Enter)</button>
        <button class="btn" id="voltar" data-acao="voltar">🔙 Voltar (0)</button>
        ${s.bloqueio ? `<span class="motivo">${esc(s.bloqueio)}</span>` : ""}
      </div></div>` : ""}
    <div class="botoes">
      ${L.extras.map(x => `<button class="btn" data-acao="${x.id}" data-atalho ${x.bloqueio ? `disabled title="${esc(x.bloqueio)}"` : ""}>
        ${tecla(!x.bloqueio)}${esc(x.nome)}${x.bloqueio ? ` (${esc(x.bloqueio)})` : ""}</button>`).join("")}
      <button class="btn ${L.esgotadas ? "forte" : "saida"}" data-acao="sair_loja" data-atalho ${L.esgotadas && !s ? "data-enter" : ""}>
        ${tecla()}🚪 Sair do Comerciante ${L.proximo ? `(próximo: ${esc(L.proximo)})` : "(último a comprar)"}</button>
    </div>`;
}

/* =====================================================================
   TELA 4 — FIM DE JOGO
   ===================================================================== */
function desenharFim() {
  const lista = E.classificacao, venc = lista[0];
  desenharTopo("🏆 Fim de jogo",
    `${E.rodada} rodadas · vencedor: <b>${esc(venc.nome)}</b> (${venc.emoji} ${esc(venc.personagem)})`, "", cartoesDaPartida());
  const medalhas = ["🥇", "🥈", "🥉"];
  $("principal").innerHTML = `
    <div class="cab"><h2>📜 Resultado final</h2></div>
    <div class="ranking">${lista.map((o, i) => `
      <div class="linha-rank ${i === 0 ? "primeiro" : ""}" style="--cor:${o.cor}">
        <span class="pos">${medalhas[i] || `${i + 1}º`}</span>
        <span class="emo">${o.emoji}</span>
        <div><span class="nome-item">${esc(o.nome)}</span> · ${esc(o.personagem)}<small>${o.equipamentos}</small></div>
        <span class="sit">${o.vencedor ? `🏆 Vencedor<br>💖 ${o.vida}/${o.max}` : `💀 Eliminado na rodada ${o.rodada_morte ?? "?"}`}<br>💰 ${o.ouro}</span>
      </div>`).join("")}</div>
    <div class="botoes"><button class="btn forte grande" data-acao="novo_jogo" data-enter>🔁 Jogar de novo (Enter)</button></div>`;
  $("lateral").innerHTML = painelJogador(E.lateral, "🏆 VENCEDOR");
}

/* =====================================================================
   DESENHO GERAL, CLIQUES E TECLADO
   ===================================================================== */
function desenhar() {
  if (!E) return;
  animacao++;
  contadorTecla = 0;
  if (E.tela === "escolha") desenharEscolha();
  else if (E.tela === "turno") desenharTurno();
  else if (E.tela === "loja") desenharLoja();
  else if (E.tela === "fim") desenharFim();
}

const ACOES_LOCAIS = {
  "tela-cheia": () => alternarTelaCheia(),
  marcar: el => { personagemMarcado = el.dataset.p; desenhar(); },
  // ↑ / ↓ na tela de escolha: troca o personagem marcado sem sair do campo do nome
  trocarPersonagem: passo => {
    const nomes = E.personagens.map(p => p.nome);
    const i = nomes.indexOf(personagemMarcado);
    personagemMarcado = nomes[(i + passo + nomes.length) % nomes.length];
    desenhar();
  },
  entrar: async () => {
    const antes = E.jogadores.length;
    await agir("entrar", { nome: nomeDigitado, personagem: personagemMarcado });
    if (E.jogadores.length > antes) { nomeDigitado = ""; personagemMarcado = null; desenhar(); }
  },
};

document.addEventListener("click", ev => {
  const el = ev.target.closest("[data-acao]");
  if (!el || el.disabled) return;
  const acao = el.dataset.acao;
  if (acao.startsWith("local:")) return ACOES_LOCAIS[acao.slice(6)](el);
  agir(acao, el.dataset.dados ? JSON.parse(el.dataset.dados) : {});
});

const visivel = el => el && !el.disabled && el.offsetParent !== null;
function clicar(el, ev) {
  if (!visivel(el)) return;
  if (ev) ev.preventDefault();
  el.click();
}

document.addEventListener("keydown", ev => {
  if (ev.key === "F11") { ev.preventDefault(); alternarTelaCheia(); return; }
  if (ev.key === "Escape" && telaCheia && !NAVEGADOR) { alternarTelaCheia(false); return; }
  const primeiroEnter = () => [...document.querySelectorAll("[data-enter]")].find(visivel);
  if (ev.target.tagName === "INPUT") {
    if ((ev.key === "ArrowUp" || ev.key === "ArrowDown") && E && E.tela === "escolha") {
      ev.preventDefault();
      ACOES_LOCAIS.trocarPersonagem(ev.key === "ArrowDown" ? 1 : -1);
      return;
    }
    if (ev.key === "Enter" && !ev.repeat) clicar(primeiroEnter(), ev);
    return;
  }
  if (ev.repeat) return;
  // botão com foco (navegação pelo Tab): Enter e espaço clicam nele mesmo
  if ((ev.key === "Enter" || ev.key === " ") && ev.target.tagName === "BUTTON") return;
  if (ev.key === "Enter") { clicar(primeiroEnter(), ev); return; }
  if (ev.key === "0") { clicar($("voltar"), ev); return; }
  if (/^[1-9]$/.test(ev.key)) {
    const exato = document.querySelector(`[data-tecla="${ev.key}"]`);
    if (exato) return clicar(exato, ev);
    clicar([...document.querySelectorAll("#principal [data-atalho]")][+ev.key - 1], ev);
  }
});

if (NAVEGADOR || (window.pywebview && window.pywebview.api && window.pywebview.api.estado)) iniciar();
else window.addEventListener("pywebviewready", iniciar);
