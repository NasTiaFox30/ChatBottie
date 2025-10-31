# ChatBottie
RAG(Cohere) z Qdrant + Gemini
(Webowy Chatbot z analizą dokumentów i CMS)

## Liczba godzin
Orientacyjna - 40-80 (14 dni)
Rzeczywista -  20 god.

## Rozpoczęty - Zakończony
12.08.2025 - 20.08.25

# Technologie:
- Backend: FastAPI (Python)
- Wektorowa Baza Danych: Qdrant
- Embedings: Cohere
- Generacja: Google Gemini
- Frontend: Static HTML/CSS/JS


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
Used Gemini 2.0 Flash - generowany GEMINI_API_KEY na https://aistudio.google.com/apikey

Parser konwertuje, czyści i rozdziela na osobne części (chunks) - zdania, akapity 

Wszystkie Environment Variables - były umieszczone w .env


### Schemat działania:
Pytanie(quary) → Cohere (embedding) → Qdrant (szukanie kontekstu) → Gemini (generacja odpowiedzi końcowej) 



### Uruchomienie lokalne:
1) użyj w pliku frontend/chatbot.js:
```
const API_BASE = "http://localhost:8000";
```
zaminast -
```
const API_BASE = "https://chatbottie.onrender.com"
```

2) Terminal (Bash):
```
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

Link aplkacji:
_Backend_: http://127.0.0.1:8000; 
_Frontend_: index.html

### Online testowanie:

Deploy Web Aplikacji "ChatBottie" na serwisie  - Render.com
(Zajmuje kilka minut do startu serweru)
https://chatbottie.onrender.com/page/index.html


## Endpoints:
#### `GET /health`
Sprawdzenie stanu aplikacji
#### `POST /chat`
Komunikacja z botem
```
{
  "query": "Twoje pytanie ,
  "top_k": 5
}
```
#### `POST /upload`
Upload pliku dla indeksacji danych
korzystanie z curl:
```
curl -X POST http://127.0.0.1:8000/upload \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx"
```
#### `POST /cms/import`
Importowanie danych z CMS (Content Management System)
```
{
  "collection": "docs",
  "records": [
    {
      "id": "унікальний_id",
      "title": "Заголовок статті",
      "body": "Текст статті...",
      "url": "https://example.com/article",
      "file_type": "cms"
    }
  ]
}
```
#### `POST /reset`
Czyszenie wektorowej bazy danych (kolekcji w Qdrant)
#### `POST /reset_all`
Całe czyszenie wektorowej bazy danych + uploaded pliki

## dodatkowe instrukcje:
 *Korzytanie z metody post /reset_all*:
czyszczenie wszystkich plików (uploaded)

lokal server:
```
 curl -X POST https://chatbottie.onrender.com/reset_all
```
online server:
```
 curl -X POST http://127.0.0.1:8000/reset_all
```

## Environments variables (.ENV):
GEMINI_URL
GEMINI_API_KEY
COHERE_API_KEY
QDRANT_API_KEY
QDRANT_URL
VECTOR_SIZE


---------------------------------------------------------------
_**Creator: Anastasiia Bzova 2025**_
