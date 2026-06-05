import os
import json
import time
import logging
import pika
from dotenv import load_dotenv

from db import get_question, save_answer
from search import search_documents
from llm import generate_answer

load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(__file__), '..', '..', '.env'
))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'docuser')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'docpassword123')

QUEUE_NAME = 'doc_question_processing'


def get_rabbitmq_connection():

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(parameters)


def process_message(ch, method, properties, body):

    try:
        payload = json.loads(body)
        question_id = payload.get('questionId')
        asked_by = payload.get('askedBy')

        logger.info("=" * 55)
        logger.info("[WORKER] Message received")
        logger.info(f"[WORKER] questionId : {question_id}")
        logger.info(f"[WORKER] askedBy    : {asked_by}")

        logger.info("[STEP 1] Fetching question from PostgreSQL...")
        question = get_question(question_id)

        if not question:
            logger.error(
                f"[STEP 1] Question not found: {question_id}"
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        question_body = question['body']
        logger.info(f"[STEP 1] Question: {question_body[:80]}...")

        logger.info("[STEP 2] Searching Qdrant...")
        contexts = search_documents(question_body, top_k=3)
       
        logger.info("[STEP 3] Generating answer...")
        answer_body, confidence_score, classification = generate_answer(
            question_body,
            contexts
        )

        logger.info("[STEP 4] Saving answer to PostgreSQL...")
        save_answer(
            question_id=question_id,
            answer_body=answer_body,
            confidence_score=confidence_score,
            classification=classification
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

        logger.info("[DONE] Processing complete")
        logger.info(f"[DONE] classification : {classification}")
        logger.info(f"[DONE] confidence     : {confidence_score}")
        logger.info("=" * 55)

    except Exception as e:
        logger.error(f"[WORKER] Error: {e}")
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
        )


def start_worker():
    
    logger.info("=" * 55)
    logger.info("[WORKER] doc-ai-engine starting...")
    logger.info(f"[WORKER] RabbitMQ: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    logger.info(f"[WORKER] Queue   : {QUEUE_NAME}")
    logger.info("=" * 55)

    retries = 0
    max_retries = 10

    while retries < max_retries:
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()

            channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True
            )

            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=process_message
            )

            logger.info("[WORKER] Ready — waiting for messages...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            retries += 1
            logger.warning(
                f"[WORKER] RabbitMQ not ready — "
                f"retry {retries}/{max_retries} in 5s"
            )
            time.sleep(5)

        except KeyboardInterrupt:
            logger.info("[WORKER] Stopped by user")
            break

        except Exception as e:
            logger.error(f"[WORKER] Unexpected error: {e}")
            retries += 1
            time.sleep(5)

    logger.error("[WORKER] Max retries reached — exiting")


if __name__ == '__main__':
    start_worker()