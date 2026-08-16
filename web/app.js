const state = { currentView: 'dashboard', chatBusy: false };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const iso = (date) => date.toISOString().slice(0, 10);
const today = () => iso(new Date());
const shiftDay = (date, amount) => { const d = new Date(`${date}T12:00:00`); d.setDate(d.getDate() + amount); return iso(d); };
const esc = (value = '') => String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const num = (value, digits = 0) => value == null ? '—' : Number(value).toFixed(digits).replace('.', ',');

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  if (!response.ok) {
    let message = `Fehler ${response.status}`;
    try { const body = await response.json(); message = body.detail || message; } catch (_) {}
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

function toast(message) {
  const el = $('#toast'); el.textContent = message; el.classList.add('show');
  clearTimeout(toast.timer); toast.timer = setTimeout(() => el.classList.remove('show'), 2800);
}

function setView(name) {
  state.currentView = name;
  $$('.nav-item').forEach(button => button.classList.toggle('active', button.dataset.view === name));
  $$('.view').forEach(view => view.classList.toggle('active', view.id === `view-${name}`));
  const loaders = { dashboard: loadDashboard, goals: loadGoals, calendar: loadCalendar, workouts: loadWorkouts, settings: loadSettings };
  loaders[name]?.();
}

async function checkHealth() {
  try {
    await api('/health');
    $('#connection-label').textContent = 'Coach online';
    document.body.classList.add('online');
  } catch (_) {
    $('#connection-label').textContent = 'Coach offline';
  }
}

function recent(metrics, key) {
  for (let i = metrics.length - 1; i >= 0; i--) if (metrics[i][key] != null) return metrics[i][key];
  return null;
}

async function loadDashboard() {
  try {
    const end = today(), start = shiftDay(end, -29);
    const [metrics, weather] = await Promise.all([
      api(`/metrics?start=${start}&end=${end}`),
      api('/weather').catch(() => null),
    ]);
    renderWeather(weather);
    const empty = metrics.length === 0;
    $('#dashboard-empty').classList.toggle('hidden', !empty);
    $('#dashboard-data').classList.toggle('hidden', empty);
    if (empty) return;
    const fields = { hrv: ['metric-hrv', 0], rhr: ['metric-rhr', 0], training_readiness: ['metric-readiness', 0], body_battery: ['metric-battery', 0], ctl: ['metric-ctl', 1], atl: ['metric-atl', 1], tsb: ['metric-tsb', 1], vo2max: ['metric-vo2', 1] };
    Object.entries(fields).forEach(([key, [id, digits]]) => $(`#${id}`).textContent = num(recent(metrics, key), digits));
    const readiness = recent(metrics, 'training_readiness');
    $('#readiness-core').textContent = readiness == null ? '—' : readiness;
    $('#system-status').textContent = readiness == null ? '// BEREIT FÜR CHECK-IN' : readiness >= 66 ? '// ALLE SYSTEME BEREIT' : readiness >= 33 ? '// SYSTEME NOMINAL' : '// ENERGIE NIEDRIG — RECOVERY EMPFOHLEN';
    renderChart(metrics);
  } catch (error) { toast(error.message); }
}

function renderWeather(weather) {
  const card = $('#weather-card');
  if (!weather?.current) { card.innerHTML = '<span class="weather-icon">◌</span><div><small>WETTER</small><strong>Nicht verfügbar</strong></div>'; return; }
  const w = weather.current;
  card.innerHTML = `<span class="weather-icon">${w.code === 0 ? '☀' : '◌'}</span><div><small>WETTER // LIVE</small><strong>${esc(w.description)} · ${num(w.temp_c, 1)} °C · Wind ${num(w.wind_kmh)} km/h</strong></div>`;
}

function renderChart(metrics) {
  const svg = $('#pmc-chart');
  const series = ['ctl', 'atl', 'tsb'];
  const values = metrics.flatMap(m => series.map(k => m[k])).filter(v => v != null).map(Number);
  if (!values.length) { svg.innerHTML = '<text x="400" y="110" text-anchor="middle" fill="#839ba5" font-size="12">Noch keine Belastungsdaten</text>'; return; }
  const min = Math.min(...values, 0), max = Math.max(...values, 1), range = max - min || 1;
  const x = i => 28 + i * (744 / Math.max(1, metrics.length - 1));
  const y = v => 195 - ((Number(v) - min) / range) * 160;
  const path = key => metrics.map((m, i) => m[key] == null ? null : `${x(i).toFixed(1)},${y(m[key]).toFixed(1)}`).filter(Boolean).map((point, i) => `${i ? 'L' : 'M'}${point}`).join(' ');
  const grids = [35, 75, 115, 155, 195].map(v => `<line class="chart-grid" x1="28" y1="${v}" x2="772" y2="${v}"/>`).join('');
  svg.innerHTML = `${grids}<path class="chart-line" d="${path('ctl')}" stroke="#e1b55d"/><path class="chart-line" d="${path('atl')}" stroke="#ff3b3f"/><path class="chart-line" d="${path('tsb')}" stroke="#5bc7ff"/>`;
}

const sportMeta = {
  swim: ['Schwimmen', '≈'], bike: ['Rad', '◫'], cycling: ['Radfahren', '◫'], run: ['Laufen', '⌁'], strength: ['Kraft', '◆'], brick: ['Koppel', '↻'], triathlon: ['Triathlon', '△'], hiking: ['Wandern', '⌃'], yoga: ['Mobility', '○'], rest: ['Ruhe', '—'], other: ['Sonstiges', '◇']
};

async function loadGoals() {
  const list = $('#goals-list');
  try {
    const goals = await api('/goals?status=all');
    if (!goals.length) { list.innerHTML = '<div class="panel empty-state"><div class="reactor reactor-small"><i></i></div><h2>Keine Missionen</h2><p>Lege dein erstes sportliches Ziel an.</p></div>'; return; }
    list.innerHTML = goals.map(g => `<article class="panel list-card"><div class="list-icon">${sportMeta[g.sport]?.[1] || '◇'}</div><div><h2>${esc(g.title)}</h2><div class="badges"><span class="badge">${esc(sportMeta[g.sport]?.[0] || g.sport)}</span><span class="badge gold">${g.priority === 1 ? 'PRIMÄR' : g.priority === 3 ? 'HINTERGRUND' : 'SEKUNDÄR'}</span>${g.event_date ? `<span class="badge gold">${esc(g.event_date)}</span>` : ''}${g.status !== 'active' ? `<span class="badge">${esc(g.status).toUpperCase()}</span>` : ''}</div>${g.description ? `<p>${esc(g.description)}</p>` : ''}</div><div class="inline-actions">${g.status === 'active' ? `<button class="ghost-button" data-goal-achieve="${g.id}">✓</button>` : ''}<button class="danger-button" data-goal-delete="${g.id}" aria-label="Ziel löschen">×</button></div></article>`).join('');
  } catch (error) { list.innerHTML = `<p class="microcopy">${esc(error.message)}</p>`; }
}

async function loadCalendar() {
  const grid = $('#calendar-grid');
  try {
    const start = today(), end = shiftDay(start, 6);
    const [plan, activities] = await Promise.all([api(`/plan?start=${start}&end=${end}`), api(`/activities?start=${start}&end=${end}`)]);
    const days = ['SO', 'MO', 'DI', 'MI', 'DO', 'FR', 'SA'];
    grid.innerHTML = Array.from({length: 7}, (_, i) => {
      const date = shiftDay(start, i), d = new Date(`${date}T12:00:00`);
      const planned = plan.filter(w => w.date === date), done = activities.filter(a => a.date === date);
      const entries = [
        ...planned.map(w => `<div class="session"><strong>${esc(w.title || sportMeta[w.sport]?.[0] || w.sport)}</strong><span>${w.duration_min ? `${w.duration_min} min · ` : ''}${esc(w.target_zone || 'Plan')}</span></div>`),
        ...done.map(a => `<div class="session activity"><strong>${esc(a.title || sportMeta[a.sport]?.[0] || a.sport)}</strong><span>✓ ${a.duration_min ? `${num(a.duration_min)} min` : 'absolviert'}</span></div>`)
      ].join('');
      return `<article class="panel day-card ${date === today() ? 'today' : ''}"><div class="day-head"><strong>${days[d.getDay()]}</strong><span>${date.slice(8,10)}.${date.slice(5,7)}.</span></div>${entries || '<div class="day-empty">FREIES FENSTER</div>'}</article>`;
    }).join('');
  } catch (error) { grid.innerHTML = `<p class="microcopy">${esc(error.message)}</p>`; }
}

async function loadWorkouts() {
  const list = $('#workouts-list');
  try {
    const start = today(), end = shiftDay(start, 90), workouts = await api(`/plan?start=${start}&end=${end}`);
    if (!workouts.length) { list.innerHTML = '<div class="panel empty-state"><h2>Keine Einheiten geplant</h2><p>Lege selbst ein Workout an oder bitte den Coach um einen Wochenplan.</p></div>'; return; }
    list.innerHTML = workouts.map(w => `<article class="panel list-card"><div class="list-icon">${sportMeta[w.sport]?.[1] || '◇'}</div><div><h2>${esc(w.title || sportMeta[w.sport]?.[0] || w.sport)}</h2><div class="badges"><span class="badge gold">${esc(w.date)}</span><span class="badge">${esc(w.target_zone || 'OHNE ZONE')}</span>${w.duration_min ? `<span class="badge">${w.duration_min} MIN</span>` : ''}</div>${w.content ? `<p>${esc(w.content)}</p>` : ''}</div><button class="danger-button" data-workout-delete="${w.id}" aria-label="Workout löschen">×</button></article>`).join('');
  } catch (error) { list.innerHTML = `<p class="microcopy">${esc(error.message)}</p>`; }
}

async function loadSettings() {
  try {
    const [status, info] = await Promise.all([api('/settings/status'), api('/app-info')]);
    $('#garmin-status').textContent = status.garmin_configured ? 'VERBUNDEN' : 'NICHT VERBUNDEN';
    $('#garmin-status').className = status.garmin_configured ? 'green' : 'red';
    $('#garmin-settings [name=email]').value = status.garmin_email || '';
    $('#calendar-settings [name=source]').value = status.calendar_source || 'auto';
    $('#calendar-status').textContent = status.calendar_configured ? 'KONFIGURIERT' : 'OPTIONAL';
    $('#research-status').textContent = info.research_ready ? `${info.research_files} DATEIEN BEREIT` : 'FEHLT';
    $('#research-status').className = info.research_ready ? 'green' : 'red';
    $('#app-info').innerHTML = `<dt>App-Version</dt><dd>${esc(info.version)}</dd><dt>System</dt><dd>${esc(info.platform)}</dd><dt>Lokaler Datenspeicher</dt><dd>${esc(info.database)}</dd><dt>Recherche-Dateien</dt><dd>${info.research_files}</dd>`;
  } catch (error) { toast(error.message); }
}

async function loadChat() {
  try {
    const history = await api('/chat/history?limit=50');
    if (!history.length) return;
    const box = $('#chat-messages'); box.innerHTML = history.map(m => `<div class="message ${m.role === 'user' ? 'user' : 'assistant'}">${esc(m.content)}</div>`).join(''); box.scrollTop = box.scrollHeight;
  } catch (_) {}
}

async function sendChat(message) {
  if (!message || state.chatBusy) return;
  state.chatBusy = true; $('#chat-status').textContent = 'ANTWORTET…';
  const box = $('#chat-messages'); $('.chat-standby', box)?.remove();
  const user = document.createElement('div'); user.className = 'message user'; user.textContent = message; box.append(user);
  const assistant = document.createElement('div'); assistant.className = 'message assistant'; assistant.textContent = '…'; box.append(assistant); box.scrollTop = box.scrollHeight;
  try {
    const response = await fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message}) });
    if (!response.ok) throw new Error('Coach ist nicht erreichbar.');
    const reader = response.body.getReader(), decoder = new TextDecoder(); let buffer = '', result = '';
    while (true) {
      const {value, done} = await reader.read(); if (done) break;
      buffer += decoder.decode(value, {stream: true});
      const events = buffer.split('\n\n'); buffer = events.pop() || '';
      for (const event of events) for (const line of event.split('\n')) if (line.startsWith('data:')) {
        const payload = JSON.parse(line.slice(5).trim());
        if (payload.delta) { result += payload.delta; assistant.textContent = result; box.scrollTop = box.scrollHeight; }
      }
    }
  } catch (error) { assistant.textContent = `[${error.message}]`; }
  finally { state.chatBusy = false; $('#chat-status').textContent = 'ONLINE'; }
}

function formObject(form) {
  return Object.fromEntries([...new FormData(form)].map(([key, value]) => [key, value === '' ? null : value]));
}

function bindEvents() {
  $('#main-nav').addEventListener('click', e => { const button = e.target.closest('[data-view]'); if (button) setView(button.dataset.view); });
  $$('[data-toggle]').forEach(button => button.addEventListener('click', () => $(`#${button.dataset.toggle}`).classList.toggle('hidden')));
  $$('input[type=range]').forEach(input => input.addEventListener('input', () => $(`output[data-for="${input.name}"]`).textContent = input.value));
  $('#workout-form [name=date]').value = today();

  $('#goal-form').addEventListener('submit', async e => {
    e.preventDefault(); const body = formObject(e.currentTarget); body.priority = Number(body.priority);
    try { await api('/goals', {method:'POST', body:JSON.stringify(body)}); e.currentTarget.reset(); e.currentTarget.classList.add('hidden'); toast('Ziel gespeichert.'); loadGoals(); } catch (error) { toast(error.message); }
  });
  $('#workout-form').addEventListener('submit', async e => {
    e.preventDefault(); const body = formObject(e.currentTarget); if (body.duration_min) body.duration_min = Number(body.duration_min);
    try { await api('/workouts', {method:'POST', body:JSON.stringify(body)}); e.currentTarget.reset(); $('#workout-form [name=date]').value = today(); e.currentTarget.classList.add('hidden'); toast('Workout gespeichert.'); loadWorkouts(); } catch (error) { toast(error.message); }
  });
  document.addEventListener('click', async e => {
    const achieve = e.target.closest('[data-goal-achieve]'), goalDelete = e.target.closest('[data-goal-delete]'), workoutDelete = e.target.closest('[data-workout-delete]');
    try {
      if (achieve) { await api(`/goals/${achieve.dataset.goalAchieve}`, {method:'PATCH', body:JSON.stringify({status:'achieved'})}); loadGoals(); }
      if (goalDelete && confirm('Dieses Ziel wirklich löschen?')) { await api(`/goals/${goalDelete.dataset.goalDelete}`, {method:'DELETE'}); loadGoals(); }
      if (workoutDelete && confirm('Dieses Workout wirklich löschen?')) { await api(`/workouts/${workoutDelete.dataset.workoutDelete}`, {method:'DELETE'}); loadWorkouts(); }
    } catch (error) { toast(error.message); }
  });
  $('#checkin-form').addEventListener('submit', async e => {
    e.preventDefault(); const body = formObject(e.currentTarget); ['soreness','pain_level','motivation','mental_energy','available_time','life_stress'].forEach(k => body[k] = body[k] == null ? null : Number(body[k]));
    try { await api('/checkin', {method:'POST', body:JSON.stringify(body)}); $('#checkin-message').textContent = 'Gespeichert ✓ – der Coach kann es jetzt lesen.'; } catch (error) { $('#checkin-message').textContent = error.message; }
  });
  $('#garmin-settings').addEventListener('submit', async e => {
    e.preventDefault(); const body = formObject(e.currentTarget);
    try { await api('/settings/garmin', {method:'POST', body:JSON.stringify(body)}); e.currentTarget.password.value = ''; $('#garmin-message').textContent = 'Sicher gespeichert ✓'; loadSettings(); } catch (error) { $('#garmin-message').textContent = error.message; }
  });
  $('#calendar-settings').addEventListener('submit', async e => {
    e.preventDefault(); const body = formObject(e.currentTarget);
    try { await api('/settings/calendar', {method:'POST', body:JSON.stringify(body)}); e.currentTarget.ics_url.value = ''; $('#calendar-message').textContent = 'Kalender gespeichert ✓'; loadSettings(); } catch (error) { $('#calendar-message').textContent = error.message; }
  });
  $('#sync-button').addEventListener('click', async e => {
    e.currentTarget.disabled = true; $('#sync-message').textContent = 'Synchronisierung läuft…';
    try { const result = await api('/sync/garmin?days=7', {method:'POST'}); $('#sync-message').textContent = `Sync OK · ${result.activities ?? 0} Aktivitäten`; toast('Garmin-Sync abgeschlossen.'); loadDashboard(); }
    catch (error) { $('#sync-message').textContent = error.message; }
    finally { e.currentTarget.disabled = false; }
  });
  $('#chat-form').addEventListener('submit', e => { e.preventDefault(); const input = $('#chat-input'), message = input.value.trim(); input.value = ''; sendChat(message); });
  $('#chat-input').addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); $('#chat-form').requestSubmit(); } });
  $('#chat-toggle').addEventListener('click', () => { $('.chat-panel').classList.add('closed'); $('#chat-open').classList.add('visible'); });
  $('#chat-open').addEventListener('click', () => { $('.chat-panel').classList.remove('closed'); $('#chat-open').classList.remove('visible'); });
}

document.addEventListener('DOMContentLoaded', () => {
  bindEvents();
  if (window.matchMedia('(max-width: 900px)').matches) {
    $('.chat-panel').classList.add('closed');
    $('#chat-open').classList.add('visible');
  }
  checkHealth(); loadDashboard(); loadChat();
});
