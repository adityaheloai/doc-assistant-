const amqp = require('amqplib');
require('dotenv').config({ 
  path: require('path').join(__dirname, '../../.env') 
});

const QUEUE_NAME = 'doc_question_processing';

const RABBITMQ_URL = `amqp://${process.env.RABBITMQ_USER || 'docuser'}:${process.env.RABBITMQ_PASSWORD || 'docpassword123'}@${process.env.RABBITMQ_HOST || 'localhost'}:${process.env.RABBITMQ_PORT || 5672}`;

async function publishQuestion(questionId, askedBy) {
  let connection = null;
  try {
    connection = await amqp.connect(RABBITMQ_URL);
    const channel = await connection.createChannel();

    // Queue declare — durable
    await channel.assertQueue(QUEUE_NAME, { durable: true });

    const payload = JSON.stringify({
      questionId: questionId,
      askedBy: askedBy
    });

    channel.sendToQueue(
      QUEUE_NAME,
      Buffer.from(payload),
      { persistent: true }
    );

    console.log(`[QUEUE] Published questionId: ${questionId}`);

    await channel.close();
    await connection.close();

    return true;
  } catch (err) {
    console.error(`[QUEUE] Publish failed: ${err.message}`);
    if (connection) await connection.close().catch(() => {});
    throw err;
  }
}

async function healthCheck() {
  let connection = null;
  try {
    connection = await amqp.connect(RABBITMQ_URL);
    await connection.close();
    return true;
  } catch (err) {
    return false;
  }
}

module.exports = { publishQuestion, healthCheck };