// const API_BASE = "http://localhost:8000";
const API_BASE = "https://chatbottie.onrender.com"

const messagesEl = document.getElementById('messages');
const chatForm   = document.getElementById('chatForm');
const userInput  = document.getElementById('userInput');
const fileInput  = document.getElementById('fileInput');
const importBtn  = document.getElementById('importCmsBtn');
const clearBtn = document.getElementById('clearBtn');

function addMessage(role, text, sources=[]) {
  const wrapper = document.createElement('div');
  wrapper.className = `msg ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  messagesEl.appendChild(wrapper);

  if (sources && sources.length) {
    const pillTpl = document.getElementById('source-pill');
    sources.slice(0,5).forEach(s => {
      const a = pillTpl.content.firstElementChild.cloneNode(true);
      a.textContent = `${s.file_type || s.source || 'źródło'} • ${s.id || ''}`.trim();
      if (s.url) { a.href = s.url; } else { a.href = '#'; a.onclick = e => e.preventDefault(); }
      bubble.appendChild(document.createElement('br'));
      bubble.appendChild(a);
    });
  }

  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// bot typing (thinking)
function addTyping() {
  const el = document.createElement('div');
  el.className = 'msg bot';
  el.dataset.typing = '1';
  el.innerHTML = `<div class="bubble"><span class="typing"><span></span><span></span><span></span></span></div>`;
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return el;
}

function removeTyping(el) { if (el && el.parentNode) el.parentNode.removeChild(el); }

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;
  addMessage('user', text);
  userInput.value = '';

  const typing = addTyping();
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ query: text, top_k: 5 })
    });
    const data = await res.json();
    removeTyping(typing);
    if (!res.ok) {
      addMessage('bot', `❌ Błąd: ${data.detail || res.statusText}`);
    } else {
      addMessage('bot', data.answer, data.sources || []);
    }
  } catch (err) {
    removeTyping(typing);
    addMessage('bot', `Problem z połączeniem - 
      (${err.message}).`);
  }
});

// upload files
fileInput.addEventListener('change', async (e) => {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;

  addMessage('bot', `Przesyłam ${files.length} plik(i)…`);
  const form = new FormData();
  files.forEach(f => form.append('files', f, f.name));

  const typing = addTyping();
  try {
    const res = await fetch(`${API_BASE}/upload`, { method:'POST', body: form });
    const data = await res.json();
    removeTyping(typing);
    if (!res.ok) addMessage('bot', `❌ Upload nieudany: ${data.detail || res.statusText}`);
    else addMessage('bot', `Zindeksowano: ${data.indexed} fragmentów z ${files.length} plików.`);
  } catch (err) {
    removeTyping(typing);
    addMessage('bot', `❌ Upload nieudany: ${err.message}`);
  } finally {
    fileInput.value = '';
  }
});

// clear colecction
clearBtn.addEventListener('click', async () => {
  const ok = confirm('Wyczyścić kolekcję wektorów?');
  if (!ok) return;
  const typing = addTyping();
  try {
    const res = await fetch(`${API_BASE}/reset`, { method:'POST' });
    const data = await res.json();
    removeTyping(typing);
    if (!res.ok) addMessage('bot', `❌ Reset nieudany: ${data.detail || res.statusText}`);
    else addMessage('bot', `Kolekcja wyczyszczona! : ${data.status}`);
  } catch (err) {
    removeTyping(typing);
    addMessage('bot', `❌ Reset nieudany: ${err.message}`);
  }
});


// Testowanie 
importBtn.addEventListener('click', async () => {
  const demo = {
    collection: "docs",
    records: [
      { id: "cms-1", title: "FAQ – Dostawa", body: "Dostawa trwa 2-3 dni robocze. Darmowa od 199 zł.", url: "https://example.com/faq" },
      { id: "cms-2", title: "Kontakt", body: "Kontakt: support@example.com, tel. 123 456 789", url: "https://example.com/contact" },
      { id: "cms-3", title: "Regulamin – zwroty", body: "Zwrot możliwy w 30 dni. Wymagany paragon lub potwierdzenie zakupu.", url: "https://example.com/terms" }
    ]
  };

  const typing = addTyping();
  try {
    const res = await fetch(`${API_BASE}/cms/import`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(demo)
    });
    const data = await res.json();
    removeTyping(typing);
    if (!res.ok) addMessage('bot', `❌ Import CMS nieudany: ${data.detail || res.statusText}`);
    else addMessage('bot', `📦 Zaimportowano CMS: ${data.indexed} fragmentów.`);
  } catch (err) {
    removeTyping(typing);
    addMessage('bot', `❌ Import CMS nieudany: ${err.message}`);
  }
});