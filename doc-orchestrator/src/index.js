const express = require('express');
const path = require('path');
require('dotenv').config({ 
  path: path.join(__dirname, '../../.env') 
});

const db = require('./db');
const queue = require('./queue');
const questionsRouter = require('./routes/questions');

const app = express();
const PORT = process.env.ORCHESTRATOR_PORT || 3000;

app.use(express.json());

app.use((req, res, next) => {
  console.log(`[HTTP] ${req.method} ${req.path}`);
  next();
});

app.use('/questions', questionsRouter);

app.get('/health', async (req, res) => {
  try {
    const dbTime = await db.healthCheck();
    const mqOk = await queue.healthCheck();

    const status = {
      status: 'ok',
      service: 'doc-orchestrator',
      timestamp: new Date().toISOString(),
      dependencies: {
        postgres: dbTime ? 'healthy' : 'unhealthy',
        rabbitmq: mqOk ? 'healthy' : 'unhealthy'
      }
    };

    console.log('[HEALTH] Check passed');
    return res.status(200).json(status);

  } catch (err) {
    console.error(`[HEALTH] Check failed: ${err.message}`);
    return res.status(503).json({
      status: 'error',
      message: err.message
    });
  }
});

app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log('==');
  console.log('[SERVER] doc-orchestrator starting...');
  console.log(`[SERVER] Port     : ${PORT}`);
  console.log(`[SERVER] DB       : ${process.env.POSTGRES_HOST}:${process.env.POSTGRES_PORT}`);
  console.log(`[SERVER] RabbitMQ : ${process.env.RABBITMQ_HOST}:${process.env.RABBITMQ_PORT}`);
  console.log('==');
  console.log('[SERVER] Ready!');
});

module.exports = app;