CREATE TABLE IF NOT EXISTS questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asked_by TEXT NOT NULL,
  subject TEXT,
  body TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_answers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID REFERENCES questions(id),
  confidence_score FLOAT,
  answer_body TEXT,
  classification TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);