const { Pool } = require('pg');
require('dotenv').config({ 
  path: require('path').join(__dirname, '../../.env') 
});

const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT) || 5432,
  database: process.env.POSTGRES_DB || 'docassistant',
  user: process.env.POSTGRES_USER || 'docuser',
  password: process.env.POSTGRES_PASSWORD || 'docpassword123',
});

pool.on('connect', () => {
  console.log('[DB] PostgreSQL connected');
});

pool.on('error', (err) => {
  console.error('[DB] PostgreSQL error:', err.message);
});

module.exports = {

  async saveQuestion(asked_by, subject, body) {
    const result = await pool.query(
      `INSERT INTO questions (asked_by, subject, body)
       VALUES ($1, $2, $3)
       RETURNING id, asked_by, subject, body, created_at`,
      [asked_by, subject || null, body]
    );
    console.log(`[DB] Question saved: ${result.rows[0].id}`);
    return result.rows[0];
  },

  async getAnswer(question_id) {
    const result = await pool.query(
      `SELECT 
         q.id as question_id,
         q.body as question,
         q.asked_by,
         q.created_at as question_created_at,
         q.processed_at,
         a.answer_body,
         a.confidence_score,
         a.classification,
         a.created_at as answered_at
       FROM questions q
       LEFT JOIN ai_answers a ON a.question_id = q.id
       WHERE q.id = $1`,
      [question_id]
    );
    return result.rows[0] || null;
  },

  async healthCheck() {
    const result = await pool.query('SELECT NOW() as time');
    return result.rows[0].time;
  }
};