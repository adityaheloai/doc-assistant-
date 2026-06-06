import os
import glob
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(__file__), '..', '.env'
))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
COLLECTION_NAME = os.getenv('QDRANT_COLLECTION', 'doc_knowledge')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5')
KB_DIR = os.path.join(os.path.dirname(__file__), 'kb')

# KB badhane pe sirf ye values change karo
CHUNK_SIZE = 500     # words per chunk
CHUNK_OVERLAP = 50   # overlap between chunks
BATCH_SIZE = 100     # vectors per upload batch


def load_documents():
    documents = []
    files = glob.glob(os.path.join(KB_DIR, '**', '*.md'), recursive=True)

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        channel = filepath.replace(KB_DIR, '').split(os.sep)[1]
        filename = os.path.basename(filepath)
        documents.append({
            'content': content,
            'channel': channel,
            'filename': filename
        })
        logger.info(f"[LOAD] {channel}/{filename} — {len(content)} chars")

    return documents


def chunk_document(doc):
    words = doc['content'].split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_text = ' '.join(words[start:end])
        chunks.append({
            'text': chunk_text,
            'channel': doc['channel'],
            'filename': doc['filename'],
            'chunk_index': len(chunks)
        })
        start = end - CHUNK_OVERLAP

    return chunks


def setup_collection(client, vector_size):
    names = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        logger.info(f"[QDRANT] Collection created: {COLLECTION_NAME}")
    else:
        logger.info(f"[QDRANT] Collection exists: {COLLECTION_NAME}")


def ingest():
    logger.info("=" * 50)
    logger.info("[START] Doc Ingest Pipeline")
    logger.info("=" * 50)

    # Step 1: Load
    documents = load_documents()
    logger.info(f"[STEP 1] Loaded {len(documents)} documents")

    # Step 2: Chunk
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        logger.info(f"[STEP 2] {doc['filename']} → {len(chunks)} chunks")
    logger.info(f"[STEP 2] Total chunks: {len(all_chunks)}")

    # Step 3: Load model
    logger.info(f"[STEP 3] Loading model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Step 4: Embed in batches
    logger.info("[STEP 4] Generating embeddings...")
    texts = [c['text'] for c in all_chunks]
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True
    )
    logger.info(f"[STEP 4] Done — {len(embeddings)} embeddings")

    # Step 5: Connect Qdrant
    logger.info(f"[STEP 5] Connecting Qdrant: {QDRANT_HOST}:{QDRANT_PORT}")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    setup_collection(client, vector_size=len(embeddings[0]))

    # Step 6: Upload in batches
    logger.info(f"[STEP 6] Uploading in batches of {BATCH_SIZE}...")
    points = []
    for idx, (chunk, emb) in enumerate(zip(all_chunks, embeddings)):
        points.append(PointStruct(
            id=idx,
            vector=emb.tolist(),
            payload={
                'text': chunk['text'],
                'channel': chunk['channel'],
                'filename': chunk['filename'],
                'chunk_index': chunk['chunk_index']
            }
        ))

    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i:i + BATCH_SIZE]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        logger.info(
            f"[STEP 6] Batch {i // BATCH_SIZE + 1}"
            f"/{(len(points) + BATCH_SIZE - 1) // BATCH_SIZE} uploaded"
        )

    count = client.count(collection_name=COLLECTION_NAME)
    logger.info(f"[VERIFY] Total vectors: {count.count}")
    logger.info("[DONE] Ingestion complete!")


if __name__ == '__main__':
    ingest()