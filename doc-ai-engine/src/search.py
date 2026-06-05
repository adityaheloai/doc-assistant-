import os
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(__file__), '..', '..', '.env'
))

logger = logging.getLogger(__name__)

QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
COLLECTION_NAME = os.getenv('QDRANT_COLLECTION', 'doc_knowledge')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5')

logger.info(f"[SEARCH] Loading embedding model: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
logger.info("[SEARCH] Model and Qdrant client ready")


def search_documents(query, top_k=3):

    try:
        logger.info(f"[SEARCH] Query: {query[:60]}...")

        query_vector = model.encode(query).tolist()

        # Qdrant search
        results = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k
        )

        contexts = []
        for hit in results:
            contexts.append({
                'text': hit.payload['text'],
                'channel': hit.payload['channel'],
                'filename': hit.payload['filename'],
                'score': round(hit.score, 4)
            })
            logger.info(
                f"[SEARCH] Hit — file: {hit.payload['filename']} | "
                f"channel: {hit.payload['channel']} | "
                f"score: {hit.score:.4f}"
            )

        logger.info(f"[SEARCH] Total hits: {len(contexts)}")
        return contexts

    except Exception as e:
        logger.error(f"[SEARCH] Search failed: {e}")
        raise