# Doc Assistant — Commands Reference

## FIRST TIME SETUP (sirf ek baar)

### 1. Infrastructure start
```bash
cd ~/Desktop/doc-assistant
docker-compose up -d
docker exec doc_ollama ollama pull tinyllama
```

### 2. doc-ingest setup + run
```bash
cd ~/Desktop/doc-assistant/doc-ingest
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 ingest.py
```

### 3. doc-ai-engine setup
```bash
cd ~/Desktop/doc-assistant/doc-ai-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. doc-orchestrator setup
```bash
cd ~/Desktop/doc-assistant/doc-orchestrator
npm install
```

### 5. doc-ui setup
```bash
cd ~/Desktop/doc-assistant/doc-ui
npm install
```

---

## DAILY RUN

### Terminal 1 — Infrastructure
```bash
cd ~/Desktop/doc-assistant
docker-compose up -d
```

### Terminal 2 — AI Worker
```bash
cd ~/Desktop/doc-assistant/doc-ai-engine
source venv/bin/activate
cd src
python3 main.py
```

### Terminal 3 — Orchestrator
```bash
cd ~/Desktop/doc-assistant/doc-orchestrator
node src/index.js
```

### Terminal 4 — React UI
```bash
cd ~/Desktop/doc-assistant/doc-ui
npm start
```

---

## BROWSER DASHBOARDS

| Service  | URL                             | Login                             |
|----------|---------------------------------|-----------------------------------|
| React UI | http://localhost:3001           | —                                 |
| RabbitMQ | http://localhost:15672          | docuser / docpassword123          |
| Qdrant   | http://localhost:6333/dashboard | —                                 |
| pgAdmin  | http://localhost:5050           | admin@docassistant.com / admin123 |

---

## KB DATA CHANGE KARNA

```bash
# 1. Qdrant clear
curl -X DELETE http://localhost:6333/collections/doc_knowledge

# 2. doc-ingest/kb/ mein naye .md files daalo

# 3. Re-ingest
cd ~/Desktop/doc-assistant/doc-ingest
source venv/bin/activate
python3 ingest.py
```

---

## VERIFY COMMANDS

```bash
# Containers status
docker-compose ps

# Sab answers dekhne ke liye
docker exec doc_postgres psql -U docuser -d docassistant -c "
SELECT q.body, a.confidence_score, a.classification,
LEFT(a.answer_body, 100) as preview
FROM questions q
JOIN ai_answers a ON a.question_id = q.id
ORDER BY q.created_at DESC LIMIT 10;"

# Indexes verify
docker exec doc_postgres psql -U docuser -d docassistant -c "
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename IN ('questions','ai_answers')
ORDER BY tablename;"

# Queue status
docker exec doc_rabbitmq rabbitmqctl list_queues

# Qdrant vectors
curl http://localhost:6333/collections/doc_knowledge
```

---

## DOCKER COMMANDS

```bash
# Band karo
docker-compose down

# Fresh start — data delete
docker-compose down -v

# Logs
docker-compose logs -f

# Specific service log
docker-compose logs -f ollama
docker-compose logs -f postgres
```