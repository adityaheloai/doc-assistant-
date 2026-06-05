import os
import logging
import psycopg
import psycopg.rows
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(__file__), '..', '..', '.env'
))

logger = logging.getLogger(__name__)


def get_dsn():
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    dbname = os.getenv('POSTGRES_DB', 'docassistant')
    user = os.getenv('POSTGRES_USER', 'docuser')
    password = os.getenv('POSTGRES_PASSWORD', 'docpassword123')
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"


def get_question(question_id):
    try:
        with psycopg.connect(
            get_dsn(),
            row_factory=psycopg.rows.dict_row
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM questions WHERE id::text = %s",
                    [str(question_id)]
                )
                question = cur.fetchone()
                if question:
                    logger.info(f"[DB] Question fetched: {question_id}")
                else:
                    logger.warning(f"[DB] Not found: {question_id}")
                return question
    except Exception as e:
        logger.error(f"[DB] Error fetching: {e}")
        raise


def save_answer(question_id, answer_body, confidence_score, classification):
    try:
        qid = str(question_id)
        ans = str(answer_body)
        score = float(confidence_score)
        cls = str(classification)

        with psycopg.connect(get_dsn()) as conn:
            with conn.cursor() as cur:

                cur.execute(
                    "INSERT INTO ai_answers "
                    "(question_id, answer_body, confidence_score, classification) "
                    "VALUES (%s::uuid, %s, %s, %s)",
                    [qid, ans, score, cls]
                )

                cur.execute(
                    "UPDATE questions "
                    "SET processed_at = CURRENT_TIMESTAMP "
                    "WHERE id::text = %s",
                    [qid]
                )

                conn.commit()
                logger.info(f"[DB] Answer saved: {question_id}")

    except Exception as e:
        logger.error(f"[DB] Error saving: {e}")
        raise