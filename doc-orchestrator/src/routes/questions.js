const express = require('express');
const router = express.Router();
const db = require('../db');
const queue = require('../queue');

router.post('/', async (req, res) => {
  try {
    const { asked_by, subject, body } = req.body;

    if (!asked_by || !body) {
      return res.status(400).json({
        error: 'asked_by and body are required'
      });
    }

    console.log(`[ROUTE] POST /questions — from: ${asked_by}`);

    const question = await db.saveQuestion(asked_by, subject, body);

    await queue.publishQuestion(question.id, asked_by);

    console.log(`[ROUTE] Question queued: ${question.id}`);

    return res.status(201).json({
      message: 'Question submitted successfully',
      questionId: question.id,
      asked_by: question.asked_by,
      subject: question.subject,
      body: question.body,
      created_at: question.created_at,
      status: 'processing'
    });

  } catch (err) {
    console.error(`[ROUTE] POST /questions error: ${err.message}`);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/:id/answer', async (req, res) => {
  try {
    const { id } = req.params;

    console.log(`[ROUTE] GET /questions/${id}/answer`);

    const result = await db.getAnswer(id);

    if (!result) {
      return res.status(404).json({ error: 'Question not found' });
    }

    if (!result.answer_body) {
      return res.status(202).json({
        message: 'Answer is being processed, please try again shortly',
        questionId: id,
        status: 'processing'
      });
    }

    return res.status(200).json({
      questionId: result.question_id,
      question: result.question,
      asked_by: result.asked_by,
      answer: result.answer_body,
      confidence_score: result.confidence_score,
      classification: result.classification,
      question_created_at: result.question_created_at,
      answered_at: result.answered_at,
      status: 'completed'
    });

  } catch (err) {
    console.error(`[ROUTE] GET answer error: ${err.message}`);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;