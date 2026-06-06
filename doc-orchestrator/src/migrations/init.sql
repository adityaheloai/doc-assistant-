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


CREATE INDEX IF NOT EXISTS idx_questions_processed_at 
ON questions(processed_at);

CREATE INDEX IF NOT EXISTS idx_questions_asked_by 
ON questions(asked_by);

CREATE INDEX IF NOT EXISTS idx_ai_answers_question_id 
ON ai_answers(question_id);

CREATE INDEX IF NOT EXISTS idx_ai_answers_classification 
ON ai_answers(classification);