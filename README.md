# ChatBottie
## RAG(Cohere) z Qdrant + Gemini
(Webowy Chatbot z analizą dokumentów i CMS)

## Liczba godzin
Orientacyjna - 40-80 (14 dni)
Rzeczywista - 

## Rozpoczęty - Zakończony
12.08.2025 - 19.08.25


# Jak działa aplikacja?
- przesyłanie plików (PDF, TXT, DOCX itp.),
- indeksowanie treści w Qdrant,
- zadawanie pytań i otrzymywanie odpowiedzi na podstawie kontekstu dokumentów,
- generowanie bardziej naturalnych odpowiedzi przy pomocy Gemini.

- opcjonalnie: czyszczenie kolekcji w Qdrant


# Raport / Opis:
Aplikacja (Fullstack) stworzona z wykorzystaniam:
Frontend: HTML + CSS3 + JS
Backend: Python (FastAPI - REST API)
(versja Python 3.13.6)

Wektorowa Baza Danych - Qdrant
wymagane: QDRANT_URL, QDRANT_API_KEY

Embeddings (model embeddingów):
Sentence-Transformers (all-MiniLM-L6-v2) – lokalny model embeddingów (old versions 1-2.0.0)
Cohere (embed-multilingual-v3.0) - generowany COHERE_API_KEY na https://dashboard.cohere.com/api-keys (new version 3.0.0)
VECTOR_SIZE="1024"

LLM (model generatywny):
Used Gemini 1.5 Flash - generowany GEMINI_API_KEY na https://aistudio.google.com/apikey

Wszystkie Environment Variables - były umieszczone w .env


### Schemat działania:
Pytanie(quary) → Cohere (embedding) → Qdrant (szukanie kontekstu) → Gemini (generacja odpowiedzi końcowej) 



### Uruchomienie lokalne:
1) użyj:
const API_BASE = "http://localhost:8000";
zaminast -
const API_BASE = "https://chatbottie.onrender.com"

2) Terminal (Bash):
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

Link aplkacji:
Backend
> http://127.0.0.1:8000
Frontend:
index.thml



## Online testowanie:
Deploy Web Aplikacji "ChatBottie" na serwisie  - Render.com
(Zajmuje kilka minut do startu serweru)
https://chatbottie.onrender.com/page/index.html
---------------------------------------------------------------
Creator: Anastasiia Bzova 2025 