# Doc Assistant — Commands Reference

---

## FIRST TIME SETUP (sirf ek baar)

```bash
cd ~/Desktop/doc-assistant

# Step 1: Sab build + start karo
docker-compose up -d --build

# Step 2: tinyllama download karo
docker exec doc_ollama ollama pull tinyllama

# Step 3: KB ingest karo
cd doc-ingest
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 ingest.py
cd ..
```

---

## DAILY RUN (bas ek command)

```bash
cd ~/Desktop/doc-assistant
docker-compose up -d
```

---

## BROWSER DASHBOARDS

| Service  | URL                             | Login                             |
|----------|---------------------------------|-----------------------------------|
| React UI | http://localhost:3000           | —                                 |
| RabbitMQ | http://localhost:15672          | docuser / docpassword123          |
| Qdrant   | http://localhost:6333/dashboard | —                                 |
| pgAdmin  | http://localhost:5050           | admin@docassistant.com / admin123 |

---

## KB DATA BADHANA

```bash
cd ~/Desktop/doc-assistant/doc-ingest
source venv/bin/activate

# Step 1: Naye .md files daalo doc-ingest/kb/ mein

# Step 2: Qdrant clear karo
curl -X DELETE http://localhost:6333/collections/doc_knowledge

# Step 3: Re-ingest karo
python3 ingest.py
```

---

## VERIFY COMMANDS

```bash
# Sab containers status
docker-compose ps

# Sab answers dekhne ke liye
docker exec doc_postgres psql -U docuser -d docassistant -c "
SELECT q.body, a.confidence_score, a.classification,
LEFT(a.answer_body, 100) as preview
FROM questions q
JOIN ai_answers a ON a.question_id = q.id
ORDER BY q.created_at DESC LIMIT 5;"

# Indexes verify
docker exec doc_postgres psql -U docuser -d docassistant -c "
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename IN ('questions','ai_answers')
ORDER BY tablename;"

# Queue status
docker exec doc_rabbitmq rabbitmqctl list_queues
```

---

## DOCKER COMMANDS

```bash
# Sab band karo
docker-compose down

# Fresh start — data delete
docker-compose down -v
docker-compose up -d --build

# Logs dekhne ke liye
docker-compose logs -f

# Specific service log
docker-compose logs -f doc_ai_engine
docker-compose logs -f doc_orchestrator
```