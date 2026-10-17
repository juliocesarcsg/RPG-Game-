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
  return ordem.map((o, i) => `<span class="item ${o.estado}">${i + 1}º ${esc(o.nome.toUpperCase())}</span>`)
    .join(`<span class="seta">➜</span>`);
}

function desenharTopo(titulo, subtitulo, ordem, jogadores) {
  $("topo").innerHTML = `
    <button class="btn-tela" id="btn-tela" data-acao="local:tela-cheia"></button>
    <h1>${titulo}</h1>
    ${subtitulo ? `<div class="subtitulo">${subtitulo}</div>` : ""}
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
function tecla() {
  contadorTecla++;
  return contadorTecla <= 9 ? `<span class="tecla">${contadorTecla}</span>` : "";
}

function painelJogador(p, tag) {
  return `
    ${tag ? `<div class="vencedor-tag">${tag}</div>` : ""}
    <h2>${esc(p.nome)}</h2>
    <div class="quem">${p.emoji} ${esc(p.personagem)}</div>
    <div class="retrato" title="Retrato do personagem">${p.emoji}</div>
    ${barraVida(p.vida, p.max, true)}
    <div class="atributos">
      <span>💖 ${p.vida}/${p.max}</span><span title="Dano físico">🔪 ${num(p.fis)}</span>
      <span title="Dano mágico">🌠 ${num(p.mag)}</span>
      <span title="Defesa${p.defesa.endsWith("*") ? " (com ácido ou Defesa temporária)" : ""}">🔰 ${num(p.defesa)}</span>
    </div>
    <ul class="lista">
      <li>💰 <b>${p.ouro} moedas</b></li>
      ${p.recurso ? `<li>${p.recurso}</li>` : ""}
      ${p.buffs ? `<li>${p.buffs}</li>` : ""}
      ${p.espacos.map(s => `<li><span class="rotulo">${esc(s.rotulo)} (${s.usados}/${s.limite}):</span> ${s.itens.join(", ") || "—"}</li>`).join("")}
      <li><span class="rotulo">Consumíveis:</span> ${p.consumiveis.join(", ") || "—"}</li>
      ${p.info.map(l => `<li>${l}</li>`).join("")}
    </ul>`;
}

function lateralOrdem() {
  return `<h2>Rodada ${E.rodada}</h2>
    <ul class="lista" style="margin-top:14px">${(E.ordem || []).map((o, i) => {
      const j = E.jogadores.find(x => x.nome === o.nome);
      return `<li><b style="color:${j.cor}">${i + 1}º ${esc(o.nome)}</b> · ${j.emoji} ${esc(j.personagem)}${j.vivo ? "" : " 💀"}</li>`;
    }).join("")}</ul>`;
}

/* ---------- painel: resultado de ação, anúncio de rodada, Comerciante ---------- */
function painelHtml(p) {
  const animado = p.dados.length > 0 || !!p.roleta;
  return `
    <div class="cab"><h2>${p.titulo}</h2></div>
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
    el.innerHTML = `👉 <span style="color:${r.cores[k]}">${esc(r.nomes[k])}</span> 👈`;
    await espera(atraso);
    atraso *= 1.09;
  }
  el.innerHTML = `🏁 <span style="color:${r.cores[r.vencedor]}">${esc(r.nomes[r.vencedor])}</span> começa! 🏁`;
  await espera(500);
}

/* =====================================================================
   TELA 1 — ESCOLHA DOS JOGADORES
   ===================================================================== */
function desenharEscolha() {
  if (!E.quantidade) {
    desenharTopo("⚔️ ARENA DE COMBATE", "RPG PvP em turnos · de 2 a 6 jogadores no mesmo teclado",
      `<span class="item atual">Quantos jogadores?</span>`, "");
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
        <h2>Como jogar</h2>
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
  desenharTopo("⚔️ ARENA DE COMBATE", `RPG PvP em turnos · ${q} jogadores no mesmo teclado`,
    `<span class="item atual">${n < q ? `Jogador ${n + 1} de ${q}: escolha o seu personagem` : "Todos prontos!"}</span>`,
    gradeJogadores(vagas));

  if (n >= q) {
    $("principal").innerHTML = `
      <div class="cab"><h2>Tudo pronto!</h2></div>
      <p>Os ${q} jogadores escolheram. A roleta vai sortear quem começa.</p>
      <div class="botoes">
        <button class="btn forte grande" data-acao="comecar" data-enter>🎲 Começar a partida (Enter)</button>
        <button class="btn" data-acao="refazer">Refazer as escolhas</button>
      </div>`;
    $("lateral").innerHTML = `<h2>Jogadores</h2><ul class="lista" style="margin-top:14px">${
      E.jogadores.map(j => `<li><b style="color:${j.cor}">${esc(j.nome)}</b> · ${j.emoji} ${esc(j.personagem)}</li>`).join("")}</ul>`;
    return;
  }

  if (!E.personagens.some(p => p.nome === personagemMarcado)) personagemMarcado = E.personagens[0].nome;
  $("principal").innerHTML = `
    <div class="cab"><h2 style="color:${E.cores[n]}">Jogador ${n + 1}</h2>
      <div class="botoes">
        ${n > 0 ? `<button class="btn" data-acao="refazer">Refazer</button>` : ""}
        <button class="btn" data-acao="trocar_quantidade">Trocar a quantidade (${q})</button>
      </div></div>
    ${avisoHtml()}
    <label class="campo"><b>📝 Nome:</b>
      <input id="nome" maxlength="20" placeholder="Digite o seu nome" value="${esc(nomeDigitado)}" autocomplete="off"></label>
    <p class="secao">Personagens · clique para ver os detalhes</p>
    <div class="grade">${E.personagens.map(p => `
      <button class="opcao ${personagemMarcado === p.nome ? "selecionada" : ""}" data-acao="local:marcar" data-p="${esc(p.nome)}" data-atalho>
        <div class="topo-opcao">${tecla()}<span class="icone">${p.emoji}</span><b>${esc(p.nome)}</b></div>
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
  $("lateral").innerHTML = `
    <h2>${esc(p.nome)}</h2>
    <div class="retrato">${p.emoji}</div>
    <ul class="lista">
      <li><b>💖 Vida ${p.vida}</b>${barra(p.vida, 150, "var(--vida-alta)")}</li>
      <li><b>🔪 Físico ${num(p.fis)}</b>${barra(p.fis, 10, "#c0392b")}</li>
      <li><b>🌠 Mágico ${num(p.mag)}</b>${barra(p.mag, 10, "#8e44ad")}</li>
      <li>🎯 ${esc(p.estilo)}</li>
    </ul>
    <p class="nota" style="margin-top:6px">Dano já com o item inicial.</p>
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
  desenharTopo(`RODADA ${E.rodada}`, "", linhaOrdem(E.ordem), cartoes);
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
  const cab = `<div class="cab"><h2>Turno de <span style="color:${j.cor}">${esc(j.nome.toUpperCase())}</span></h2>
    <span class="etiqueta">${j.emoji} ${esc(j.personagem)}</span></div>`;

  if (E.modo === "acoes") {
    $("principal").innerHTML = cab + registroHtml() + avisoHtml() + `
      <p class="secao">Escolha sua ação</p>
      <div class="acoes">${E.acoes.map(a => `
        <button class="acao ${a.livre ? "livre" : ""}" data-acao="acao" data-dados="${dados({ id: a.id })}"
                ${a.bloqueio ? "disabled" : "data-atalho"}>
          ${a.bloqueio ? `<span class="tecla" style="opacity:.4">✖</span>` : tecla()}
          <span class="acao-texto"><strong>${esc(a.nome)}${a.livre ? `<span class="pill-livre">ação livre</span>` : ""}</strong>
          <small>${a.bloqueio ? `<span class="motivo">${esc(a.bloqueio)}</span>` : esc(a.desc)}</small></span>
        </button>`).join("")}</div>`;
  } else if (E.modo === "alvo") {
    $("principal").innerHTML = cab + avisoHtml() + `
      <p class="secao">${esc(E.alvos.titulo)}</p>
      <div class="grade">${E.alvos.lista.map(o => `
        <button class="opcao" data-acao="alvo" data-dados="${dados({ indice: o.indice })}" style="border-left:8px solid ${o.cor}"
                ${o.bloqueio ? "disabled" : "data-atalho"}>
          <div class="topo-opcao">${o.bloqueio ? "" : tecla()}<span class="icone">${o.emoji}</span><b>${esc(o.nome)}</b></div>
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
                  ${clicavel ? "data-atalho" : "disabled"}>
          <div class="topo-opcao">${clicavel ? tecla() : ""}<b>${it.nome}</b></div>
          <span class="tipo" style="--tcor:${it.cor}">${esc(it.tipo)}${uso}</span>
          <ul class="efeitos">${it.efeitos.map(l => `<li>${l}</li>`).join("")}</ul>
          <small>${it.bloqueio ? `<span class="motivo">${esc(it.bloqueio)}</span>` : esc(it.estado)}</small>
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
  desenharTopo("🧳 O COMERCIANTE", `Rodada ${L.rodada} · itens <b>${esc(L.fase)}</b>`, linhaOrdem(L.ordem), cartoesDaPartida());
  $("lateral").innerHTML = E.lateral ? painelJogador(E.lateral)
    : `<h2>🧳</h2><p class="nota" style="text-align:center">Todos já passaram pelo Comerciante.</p>`;

  if (E.modo === "painel") {
    $("principal").innerHTML = painelHtml(E.painel);
    $("continuar").focus();
    return;
  }
  const j = E.jogadores[E.atual];
  const cab = `<div class="cab"><h2>Estoque de <span style="color:${j.cor}">${esc(j.nome.toUpperCase())}</span></h2>
    <div class="chips">${L.compras.map(c => `<span class="chip ${c.feitas >= c.limite ? "esgotado" : ""}">${esc(c.rotulo)} ${c.feitas}/${c.limite}</span>`).join("")}</div></div>`;
  const voltar = `<div class="botoes"><button class="btn" id="voltar" data-acao="voltar">🔙 Voltar (0)</button></div>`;

  if (E.modo === "substituir") {
    $("principal").innerHTML = cab + avisoHtml() + `<p class="secao">${esc(L.substituir.titulo)}</p>
      <div class="grade">${L.substituir.lista.map(c => `
        <button class="opcao" data-acao="substituir" data-dados="${dados({ indice: c.indice })}" data-atalho>
          <div class="topo-opcao">${tecla()}<b>${c.nome}</b></div>
          <ul class="efeitos">${c.efeitos.map(l => `<li>${l}</li>`).join("")}</ul>
        </button>`).join("")}</div>` + voltar;
    return;
  }
  if (E.modo === "forja") {
    $("principal").innerHTML = cab + avisoHtml() + `<p class="secao">${esc(L.forja.titulo)}</p>
      <div class="grade">${L.forja.lista.map(c => `
        <button class="opcao" data-acao="forjar" data-dados="${dados({ indice: c.indice })}" data-atalho>
          <div class="topo-opcao">${tecla()}<b>${c.nome}</b><span class="preco">🔨 ${c.nivel}/${c.max}</span></div>
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
          <div class="topo-opcao">${tecla()}<b>${c.nome}</b><span class="preco">${vezes ? `✔ ${vezes > 1 ? "×2" : ""}` : ""}</span></div>
          <small>${c.usos} uso(s)</small>
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
              ${it.disponivel ? "data-atalho" : "disabled"}>
        <div class="topo-opcao">${it.disponivel ? tecla() : ""}<span class="icone">${it.emoji}</span>
          <span class="preco">${it.disponivel ? `💰 ${it.preco}` : "VENDIDO"}</span></div>
        <b class="${it.disponivel ? "" : "vendido"}">${esc(it.nome)}</b>
        <span class="tipo" style="--tcor:${it.cor}">${esc(it.tipo)} · ${it.fixa ? "sempre à venda" : esc(it.fase)}</span>
        <ul class="efeitos">${it.efeitos.map(l => `<li>${l}</li>`).join("")}</ul>
      </button>`).join("")}</div>
    ${s ? `<div class="detalhe">
      <h3>${s.emoji} ${esc(s.nome)} <span class="tipo" style="--tcor:var(--suave)">${esc(s.tipo)} · ${esc(s.fase)}</span></h3>
      <p><i>${esc(s.descricao)}</i></p>
      <ul class="efeitos">${s.efeitos.map(l => `<li>✨ ${l}</li>`).join("")}</ul>
      ${s.detalhes.map(l => `<p>${l}</p>`).join("")}
      <p>💰 Preço: <b style="color:${s.pode_pagar ? "var(--ok)" : "var(--perigo)"}">${s.preco} moedas</b> (você tem ${j.ouro})</p>
      <div class="botoes">
        <button class="btn forte" id="comprar" data-acao="comprar" data-enter ${s.bloqueio ? "disabled" : ""}>✅ Comprar (Enter)</button>
        <button class="btn" id="voltar" data-acao="voltar">🔙 Voltar (0)</button>
        ${s.bloqueio ? `<span class="motivo">${esc(s.bloqueio)}</span>` : ""}
      </div></div>` : ""}
    <div class="botoes">
      ${L.extras.map(x => `<button class="btn" data-acao="${x.id}" ${x.bloqueio ? `disabled title="${esc(x.bloqueio)}"` : ""}>
        ${esc(x.nome)}${x.bloqueio ? ` (${esc(x.bloqueio)})` : ""}</button>`).join("")}
      <button class="btn ${L.esgotadas ? "forte" : ""}" data-acao="sair_loja" ${L.esgotadas && !s ? "data-enter" : ""}>
        🚪 Sair do Comerciante ${L.proximo ? `(próximo: ${esc(L.proximo)})` : "(último a comprar)"}</button>
    </div>`;
}

/* =====================================================================
   TELA 4 — FIM DE JOGO
   ===================================================================== */
function desenharFim() {
  const lista = E.classificacao, venc = lista[0];
  desenharTopo("🏆 FIM DE JOGO",
    `${E.rodada} rodadas · vencedor: <b>${esc(venc.nome)}</b> (${venc.emoji} ${esc(venc.personagem)})`, "", cartoesDaPartida());
  const medalhas = ["🥇", "🥈", "🥉"];
  $("principal").innerHTML = `
    <div class="cab"><h2>📜 Resultado final</h2></div>
    <div class="ranking">${lista.map((o, i) => `
      <div class="linha-rank ${i === 0 ? "primeiro" : ""}" style="--cor:${o.cor}">
        <span class="pos">${medalhas[i] || `${i + 1}º`}</span>
        <span class="emo">${o.emoji}</span>
        <div><b>${esc(o.nome)}</b> · ${esc(o.personagem)}<small>${o.equipamentos}</small></div>
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
  if (ev.repeat) return;
  const primeiroEnter = () => [...document.querySelectorAll("[data-enter]")].find(visivel);
  if (ev.target.tagName === "INPUT") {
    if (ev.key === "Enter") clicar(primeiroEnter(), ev);
    return;
  }
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
