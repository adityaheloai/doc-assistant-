# Doc Assistant

Open Source Documentation Assistant — RAG-based system that answers
developer questions using vector search and a local LLM.

Inspired by helo.ai production architecture:
- doc-orchestrator → support-automation
- doc-ai-engine    → ai-engine
- doc-ingest       → rag-pipeline

---

## Architecture

```
Developer
    ↓
POST /questions  (Node.js Orchestrator)
    ↓
PostgreSQL  (question store)
    ↓
RabbitMQ  (publish questionId)
    ↓
Python Worker  (consume)
    ↓
Qdrant  (vector search — top 3 docs)
    ↓
Ollama tinyllama  (generate answer)
    ↓
PostgreSQL  (save answer)
    ↓
GET /questions/:id/answer → Developer
```

---

## Services

| Service              | Tech          | Port        |
|----------------------|---------------|-------------|
| doc-orchestrator     | Node.js 18    | 3000        |
| doc-ai-engine        | Python 3.12   | —           |
| doc-ingest           | Python 3.12   | —           |
| doc-ui               | React         | 3001        |
| PostgreSQL           | v15           | 5432        |
| RabbitMQ             | v3            | 5672/15672  |
| Qdrant               | latest        | 6333        |
| Ollama (tinyllama)   | latest        | 11434       |
| pgAdmin              | latest        | 5050        |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/adityaheloai/doc-assistant-.git
cd doc-assistant

# 2. Environment
cp .env.example .env

# 3. Infrastructure
docker-compose up -d
docker exec doc_ollama ollama pull tinyllama

# 4. Ingest KB
cd doc-ingest
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python3 ingest.py

# 5. AI Worker (Terminal 2)
cd ../doc-ai-engine
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd src && python3 main.py

# 6. Orchestrator (Terminal 3)
cd ../../doc-orchestrator
npm install && node src/index.js

# 7. React UI (Terminal 4)
cd ../doc-ui
npm install && npm start
```

---

## API Endpoints

### Submit Question
```
POST http://localhost:3000/questions
Content-Type: application/json

{
  "asked_by": "dev@example.com",
  "subject": "Python",
  "body": "How do I create a virtual environment?"
}
```

### Get Answer
```
GET http://localhost:3000/questions/:id/answer
```

### Health Check
```
GET http://localhost:3000/health
```

---

## Database Schema

```sql
CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asked_by TEXT NOT NULL,
  subject TEXT,
  body TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_at TIMESTAMP
);

CREATE TABLE ai_answers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID REFERENCES questions(id),
  confidence_score FLOAT,
  answer_body TEXT,
  classification TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
CREATE INDEX idx_questions_processed_at ON questions(processed_at);
CREATE INDEX idx_questions_asked_by ON questions(asked_by);
CREATE INDEX idx_ai_answers_question_id ON ai_answers(question_id);
CREATE INDEX idx_ai_answers_classification ON ai_answers(classification);
```

---

## RabbitMQ Message Contract

Queue: `doc_question_processing`

```json
{
  "questionId": "550e8400-e29b-41d4-a716-446655440000",
  "askedBy": "dev@example.com"
}
```

---

## Sample Test Results

| Question                                      | Confidence | Classification |
|-----------------------------------------------|------------|----------------|
| How do I create a virtual environment?        | 0.8095     | auto_answer    |
| What is the purpose of a RabbitMQ queue?      | 0.8428     | auto_answer    |
| How do I connect to PostgreSQL from Node.js?  | 0.8377     | auto_answer    |
| What is FastAPI and when should I use it?     | 0.8317     | auto_answer    |
| How does Qdrant store vectors?                | 0.5319     | needs_review   |

---

## Knowledge Base

6 documents across 4 channels:

| Channel  | Files                          |
|----------|--------------------------------|
| python   | python_faq.md, venv_guide.md   |
| fastapi  | fastapi_intro.md               |
| postgres | postgres_guide.md              |
| rabbitmq | rabbitmq_intro.md, rabbitmq_queues.md |

---

## Changing KB Data (Production Use)

```bash
# 1. Clear existing vectors
curl -X DELETE http://localhost:6333/collections/doc_knowledge

# 2. Add new .md files to doc-ingest/kb/

# 3. Re-ingest
cd doc-ingest
source venv/bin/activate
python3 ingest.py
```

No other code changes needed.

---

## Project Structure

```
doc-assistant/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── COMMANDS.md
├── doc-orchestrator/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── index.js
│       ├── db.js
│       ├── queue.js
│       └── routes/
│           └── questions.js
├── doc-ai-engine/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── db.py
│       ├── search.py
│       └── llm.py
├── doc-ingest/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── ingest.py
│   └── kb/
│       ├── python/
│       ├── fastapi/
│       ├── postgres/
│       └── rabbitmq/
└── doc-ui/
    ├── package.json
    └── src/
        └── App.js
```