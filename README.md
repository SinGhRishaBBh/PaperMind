
# 🧠 PaperMind  
### Ask Questions From Your PDFs Using AI

PaperMind is a full-stack **PDF Question Answering system** that allows users to upload PDF documents and ask natural language questions. It uses **Retrieval-Augmented Generation (RAG)** to extract relevant content from documents and generate accurate answers using **OpenRouter (DeepSeek model)**.

---

## 🚀 Key Features

- 📄 Upload and process PDF documents  
- 🔍 Context-aware question answering  
- 🤖 AI responses powered by OpenRouter (DeepSeek)  
- 🧠 Prevents hallucinations using document-only context  
- ⚡ Fast and responsive UI  
- 🌐 Full-stack integration (Next.js + FastAPI)  
- 🗂️ MongoDB-based document storage  

---

## 🏗️ Tech Stack

### Frontend
- Next.js (App Router)
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- MongoDB
- OpenRouter API (DeepSeek)
- PyPDF

---

## 📁 Project Structure

```
pdf-question-answering/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   └── styles/
├── python_backend/
│   ├── server.py
│   └── requirements.txt
├── README.md
└── LICENSE
```

---

## ⚙️ Environment Variables

### Backend (`python_backend/.env`)
```
MONGO_URI=your_mongodb_uri
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_SITE_NAME=PaperMind
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
```

---

## ▶️ Run Locally

### Backend
```
cd python_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### Frontend
```
cd frontend
npm install
npm run dev
```

---

## 📜 License
MIT License

---

## ⭐ Author
PaperMind – AI-powered PDF Intelligence
