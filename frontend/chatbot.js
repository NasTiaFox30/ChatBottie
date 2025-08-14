const API_BASE = "http://localhost:8000";

const messagesEl = document.getElementById('messages');
const chatForm   = document.getElementById('chatForm');
const userInput  = document.getElementById('userInput');
const fileInput  = document.getElementById('fileInput');
const importBtn  = document.getElementById('importCmsBtn');
const clearBtn = document.getElementById('clearBtn');

function addTyping() {
  const el = document.createElement('div');
  el.className = 'msg bot';
  el.dataset.typing = '1';
  el.innerHTML = `<div class="bubble"><span class="typing"><span></span><span></span><span></span></span></div>`;
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return el;
}
