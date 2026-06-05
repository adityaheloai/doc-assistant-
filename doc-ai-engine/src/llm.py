import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(__file__), '..', '..', '.env'
))

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'tinyllama')
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"


def build_prompt(question, contexts):

    context_text = "\n\n".join([
        f"Source: {c['filename']}\n{c['text']}"
        for c in contexts
    ])

    return f"""You are a helpful documentation assistant.
Answer the question using ONLY the context provided below.
If the answer is not found in the context, say exactly:
"I could not find this in the documentation."
Keep your answer clear and concise.

CONTEXT:
{context_text}

QUESTION:
{question}

ANSWER:"""


def call_ollama(prompt):

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        answer = result.get('response', '').strip()

        if answer:
            logger.info("[LLM] Ollama response received")
            return answer
        return None

    except Exception as e:
        logger.warning(f"[LLM] Ollama unavailable: {e}")
        return None


def template_fallback(question, contexts):

    if not contexts:
        return "I could not find relevant information in the documentation."

    parts = []
    for ctx in contexts[:2]:
        parts.append(
            f"From {ctx['filename']}:\n{ctx['text'][:400]}"
        )

    answer = (
        "Based on the documentation:\n\n" +
        "\n\n".join(parts)
    )
    return answer


def calculate_confidence(contexts):
    
    if not contexts:
        return 0.0
    return round(float(contexts[0]['score']), 4)


def classify_answer(confidence_score):

    if confidence_score >= 0.75:
        return 'auto_answer'
    return 'needs_review'


def generate_answer(question, contexts):

    logger.info(f"[LLM] Generating answer...")

    confidence_score = calculate_confidence(contexts)
    classification = classify_answer(confidence_score)

    # Ollama try karo pehle
    prompt = build_prompt(question, contexts)
    answer = call_ollama(prompt)

    if answer:
        logger.info("[LLM] Using Ollama answer")
    else:
        logger.warning("[LLM] Ollama failed — using template fallback")
        answer = template_fallback(question, contexts)

    logger.info(
        f"[LLM] confidence_score: {confidence_score} | "
        f"classification: {classification}"
    )

    return answer, confidence_score, classification