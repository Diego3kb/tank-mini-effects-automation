// UI Tank Mini — sem dependências externas.
"use strict";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];

// ----- enums de docs/EFEITOS-FABRICA.md -----
const ENUMS = {
  fx: { 0: "Noise Gate", 1: "Boost", 2: "Compress" },
  mod: { 0: "Chorus", 1: "Phaser", 2: "Tremolo", 3: "Flanger", 4: "Vibrato", 5: "Univibe", 6: "Autofilter" },
  delay: { 0: "Analog", 1: "Duck", 2: "dTape", 3: "Dual", 4: "Lofi" },
  reverb: { 0: "Room", 1: "Hall", 2: "Swell", 3: "Spring", 4: "Shimmer", 5: "Cloud" },
  amp: { 0: "UWE-Twins", 1: "UK-C30Normal", 2: "MarsVM410", 3: "Victor_Mars", 4: "BritPLEX_100", 5: "MarsFD100", 6: "Eagle_SAVAGE", 7: "TH_DiselHgn", 8: "PvEV5150", 9: "FORTIN_CALI", 10: "MessMktCln2", 11: "CA-tweed", 12: "BogSV20", 13: "Juice_JIM", 14: "Sur_SL68", 15: "BasADAtube", 16: "BasAlmbic", 17: "BasG800K_7", 18: "BasTR-Trad", 19: "BasMarkT501" },
  cab: { 1: "EAGLProV30s", 2: "Sperimental", 3: "Juice4x12V30", 4: "Mess Bog", 5: "FdChamp", 6: "FdPrJunir", 7: "Mar960BV30", 8: "DizzlV30", 9: "Elctrovoice", 10: "MessRectV30", 11: "TwinJensenC", 12: "TwedDlx1X12", 13: "FendShowman", 14: "J120Rolnd", 15: "AC30Silvers", 16: "BassAgula25", 17: "BassJensn10", 18: "BassStdio22", 19: "BassAmpg410", 20: "BassEDN300" },
};
const PARAM_COUNTS = { fx: 4, mod: 6, delay: 6, reverb: 6 };

const state = { bundlePath: null, sha: null, slots: {}, original: {}, current: null };

async function api(url, options) {
  const r = await fetch(url, options);
  const body = await r.json().catch(() => ({}));
  if (!r.ok) {
    const msg = body.error || `HTTP ${r.status}`;
    if (msg.includes("hash")) alert(`${msg}\n\nRecarregue o banco (Abrir banco).`);
    throw new Error(msg);
  }
  return body;
}

// ----- abas -----
$$(".tab-btn").forEach((btn) => btn.addEventListener("click", () => {
  $$(".tab-btn, .tab").forEach((el) => el.classList.remove("active"));
  btn.classList.add("active");
  $(`#tab-${btn.dataset.tab}`).classList.add("active");
}));

// ----- banco: abrir e grid -----
$("#btn-open").addEventListener("click", async () => {
  const path = $("#bundle-path").value.trim();
  if (!path) return;
  try {
    const body = await api(`/api/bundle?path=${encodeURIComponent(path)}`);
    state.bundlePath = path;
    state.sha = body.sha256;
    state.slots = body.slots;
    state.original = JSON.parse(JSON.stringify(body.slots));
    $("#bundle-info").textContent = `sha256: ${body.sha256.slice(0, 16)}…`;
    renderGrid();
  } catch (e) { alert(e.message); }
});

function renderGrid() {
  const grid = $("#slot-grid");
  grid.innerHTML = "";
  for (const [slot, d] of Object.entries(state.slots)) {
    const cell = document.createElement("div");
    cell.className = "slot" + (slot === state.current ? " selected" : "");
    const mods = ["fx", "amp", "mod", "delay", "cab", "reverb"]
      .filter((m) => d[`${m}.enabled`])
      .map((m) => m.toUpperCase()).join(" ");
    cell.innerHTML = `<b>${slot}</b><small>${d.amp_nome_tabela_am2_original || ""}<br>${d.cab_nome_de_fabrica || ""}<br>${mods}</small>`;
    cell.addEventListener("click", () => { state.current = slot; renderGrid(); renderEditor(); });
    grid.appendChild(cell);
  }
}

// ----- editor do slot -----
function fillSelect(sel, enumKey, value) {
  sel.innerHTML = "";
  for (const [k, label] of Object.entries(ENUMS[enumKey])) {
    const opt = document.createElement("option");
    opt.value = k; opt.textContent = label;
    sel.appendChild(opt);
  }
  sel.value = String(value);
}

function sliderRow(field, value) {
  const input = $(`[data-f="${field}"]`);
  if (!input) return;
  input.value = value;
  const out = $(`[data-v="${field}"]`);
  if (out) out.textContent = value;
}

function renderEditor() {
  const d = state.slots[state.current];
  if (!d) return;
  $("#ed-slot").textContent = state.current;
  $("#editor").classList.remove("hidden");
  for (const m of ["fx", "amp", "mod", "delay", "cab", "reverb"])
    $(`[data-f="${m}.enabled"]`).checked = !!d[`${m}.enabled`];
  fillSelect($('[data-f="fx.type"]'), "fx", d.fx.type_id);
  fillSelect($('[data-f="mod.type"]'), "mod", d.mod.type_id);
  fillSelect($('[data-f="delay.type"]'), "delay", d.delay.type_id);
  fillSelect($('[data-f="reverb.type"]'), "reverb", d.reverb.type_id);
  fillSelect($('[data-f="amp.model"]'), "amp", d.amp.model_id);
  fillSelect($('[data-f="cab.slot"]'), "cab", d.cab.slot);
  for (const f of ["preset_volume_raw", "amp.gain", "amp.level", "amp.bass", "amp.mid", "amp.treble", "cab.level", "cab.low_cut_raw", "cab.high_cut_raw"])
    sliderRow(f, d[f]);
  renderParams("fx", d.fx.type_id);
  renderParams("mod", d.mod.type_id);
  renderParams("delay", d.delay.type_id);
  renderParams("reverb", d.reverb.type_id);
}

function renderParams(mod, typeId) {
  const holder = $(`#${mod}-params`);
  holder.innerHTML = "";
  for (let n = 1; n <= PARAM_COUNTS[mod]; n++) {
    const field = `${mod}.param${n}`;
    const wrap = document.createElement("label");
    wrap.innerHTML = `p${n} <input type="number" min="0" max="100" data-f="${field}" value="${state.slots[state.current][field] ?? 0}">`;
    holder.appendChild(wrap);
  }
}

// ----- salvar: diff campo a campo -----
$("#btn-save").addEventListener("click", async () => {
  if (!state.current) return;
  const slot = state.current;
  const edits = {};
  const changes = {};
  $$("[data-f]").forEach((input) => {
    const field = input.dataset.f;
    let value;
    if (input.type === "checkbox") value = input.checked ? 1 : 0;
    else value = Number(input.value);
    if (state.original[slot][field] !== value) changes[field] = value;
  });
  if (!Object.keys(changes).length) { alert("Nenhuma alteração."); return; }
  edits[slot] = changes;
  try {
    const body = await api("/api/edit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: state.bundlePath, edits }),
    });
    $("#edit-log").textContent = body.log;
    $("#bundle-path").value = body.output;
    alert(`Banco criado: ${body.output}`);
  } catch (e) { alert(e.message); }
});

// ----- dispositivo -----
function logTo(sel, text) { $(sel).textContent = text; }

async function device(command, extra = {}) {
  try {
    const body = await api("/api/device", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command, ...extra }),
    });
    logTo("#device-log", body.log);
  } catch (e) { logTo("#device-log", `ERRO: ${e.message}`); }
}

$("#dev-backup").addEventListener("click", () => device("backup"));
$("#dev-export-all").addEventListener("click", () => device("export-all"));
$("#dev-export-preset").addEventListener("click", () => device("export-preset", { slot: $("#dev-slot").value }));
$("#dev-import-preset").addEventListener("click", () => device("import-preset", { slot: $("#dev-slot").value, path: $("#dev-import-file").value.trim() }));
$("#dev-import-all").addEventListener("click", () => device("import-all", { path: $("#dev-import-file").value.trim() }));

// ----- biblioteca -----
async function refreshLibrary() {
  try {
    const body = await api("/api/library");
    const fill = (ul, items, kind) => {
      ul.innerHTML = "";
      items.forEach((p, i) => {
        const li = document.createElement("li");
        li.innerHTML = `<span>${p.split("/").pop()}</span> `;
        const open = document.createElement("button");
        open.textContent = "Carregar";
        open.addEventListener("click", async () => {
          try {
            const r = await api("/api/library/open", {
              method: "POST", headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ kind, path: p }),
            });
            logTo("#library-log", r.log);
          } catch (e) { logTo("#library-log", `ERRO: ${e.message}`); }
        });
        const save = document.createElement("button");
        save.textContent = "Salvar no pedal";
        save.addEventListener("click", async () => {
          const item = Number(prompt(`Número do item na lista do M-EFCS (1-based):`, String(i + 1)));
          if (!item) return;
          if (!confirm(`Confirmar envio do item ${item} ao pedal?`)) return;
          const typed = prompt(`Digite ${item} para confirmar:`);
          if (typed !== String(item)) { alert("Confirmação não bate."); return; }
          try {
            const r = await api("/api/library/save", {
              method: "POST", headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ kind, item, confirm: true }),
            });
            logTo("#library-log", r.log);
          } catch (e) { logTo("#library-log", `ERRO: ${e.message}`); }
        });
        li.append(open, save);
        ul.appendChild(li);
      });
    };
    fill($("#lib-cabs"), body.cabs, "cab");
    fill($("#lib-amps"), body.amps, "amp");
  } catch (e) { logTo("#library-log", `ERRO: ${e.message}`); }
}
$("#lib-refresh").addEventListener("click", refreshLibrary);

// ----- init -----
{
  const sel = $("#dev-slot");
  for (let b = 1; b <= 7; b++) for (const l of "ABC") {
    const opt = document.createElement("option");
    opt.textContent = `${b}${l}`;
    sel.appendChild(opt);
  }
  $$("[data-enum]").forEach((s) => fillSelect(s, s.dataset.enum, 0));
}
