import os
import glob
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

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

def load_documents():
    """KB folder se saare .md files load karo"""
    documents = []
    files = glob.glob(os.path.join(KB_DIR, '**', '*.md'), recursive=True)
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Channel = folder name (python, fastapi, postgres, rabbitmq)
        channel = filepath.replace(KB_DIR, '').split(os.sep)[1]
        filename = os.path.basename(filepath)
        
        documents.append({
            'content': content,
            'channel': channel,
            'filename': filename,
            'filepath': filepath
        })
        logger.info(f"[LOAD] {channel}/{filename} — {len(content)} chars")
    
    return documents

def chunk_document(doc, chunk_size=500, overlap=50):
    """Document ko chunks mein toddo"""
    content = doc['content']
    words = content.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        
        chunks.append({
            'text': chunk_text,
            'channel': doc['channel'],
            'filename': doc['filename'],
            'chunk_index': len(chunks)
        })
        
        start = end - overlap
    
    return chunks

def setup_collection(client, vector_size):
    """Qdrant collection setup karo"""
    collections = client.get_collections().collections
    names = [c.name for c in collections]
    
    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        logger.info(f"[QDRANT] Collection '{COLLECTION_NAME}' created")
    else:
        logger.info(f"[QDRANT] Collection '{COLLECTION_NAME}' already exists")

def ingest():
    logger.info("=" * 50)
    logger.info("[START] Doc Ingest Pipeline")
    logger.info("=" * 50)
    
    logger.info("[STEP 1] Loading documents from KB...")
    documents = load_documents()
    logger.info(f"[STEP 1] Loaded {len(documents)} documents")
    
    logger.info("[STEP 2] Chunking documents...")
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        logger.info(f"[STEP 2] {doc['filename']} → {len(chunks)} chunks")
    logger.info(f"[STEP 2] Total chunks: {len(all_chunks)}")
    
    logger.info(f"[STEP 3] Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    logger.info("[STEP 3] Model loaded successfully")
    
    logger.info("[STEP 4] Generating embeddings...")
    texts = [chunk['text'] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    logger.info(f"[STEP 4] Generated {len(embeddings)} embeddings — size: {len(embeddings[0])}")
    
    logger.info(f"[STEP 5] Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    setup_collection(client, vector_size=len(embeddings[0]))
    
    logger.info("[STEP 6] Uploading vectors to Qdrant...")
    points = []
    for idx, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
        points.append(PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                'text': chunk['text'],
                'channel': chunk['channel'],
                'filename': chunk['filename'],
                'chunk_index': chunk['chunk_index']
            }
        ))
    
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    logger.info(f"[STEP 6] Uploaded {len(points)} vectors to Qdrant")
    
    count = client.count(collection_name=COLLECTION_NAME)
    logger.info(f"[VERIFY] Qdrant collection '{COLLECTION_NAME}' has {count.count} points")
    logger.info("[DONE] Ingestion complete!")

if __name__ == '__main__':
    ingest()