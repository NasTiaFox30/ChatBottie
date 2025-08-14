const API_BASE = "http://localhost:8000";

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
