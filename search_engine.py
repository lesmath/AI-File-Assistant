import chromadb
from sentence_transformers import SentenceTransformer
import sqlite3

class SearchEngine:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.collection = self.client.get_or_create_collection(name="files")
        self._sync_db()

    def _sync_db(self):
        """Sync SQLite metadata with ChromaDB."""
        conn = sqlite3.connect("file_metadata.db")
        cursor = conn.cursor()
        cursor.execute("SELECT path, content FROM files WHERE content != ''")
        records = cursor.fetchall()

        self.collection.add(
            documents=[record[1] for record in records],
            metadatas=[{"path": record[0]} for record in records],
            ids=[str(i) for i in range(len(records))]
        )

    def search(self, query, n_results=5):
        """Semantic search over file contents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results["metadatas"][0]  # Returns file paths + snippets

# Example usage:
# engine = SearchEngine()
# print(engine.search("React component"))
