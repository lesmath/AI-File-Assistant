import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sqlite3
from datetime import datetime

class FileIndexer:
    def __init__(self, watch_dir="."):
        self.watch_dir = watch_dir
        self.conn = sqlite3.connect("file_metadata.db")
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                filetype TEXT,
                size INTEGER,
                last_modified TEXT,
                content TEXT
            )
        """)
        self.conn.commit()

    def index_file(self, path):
        """Extract metadata and store in SQLite."""
        if not os.path.exists(path):
            return

        filetype = os.path.splitext(path)[1].lower()
        size = os.path.getsize(path)
        last_modified = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
        content = self._extract_content(path, filetype)

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO files (path, filetype, size, last_modified, content)
            VALUES (?, ?, ?, ?, ?)
        """, (path, filetype, size, last_modified, content))
        self.conn.commit()

    def _extract_content(self, path, filetype):
        """Extract text from files (PDF, DOCX, TXT, etc.)."""
        if filetype == ".pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            return " ".join([page.extract_text() for page in reader.pages])
        elif filetype == ".txt":
            with open(path, "r") as f:
                return f.read()
        return ""

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, indexer):
        self.indexer = indexer

    def on_modified(self, event):
        if not event.is_directory:
            self.indexer.index_file(event.src_path)

if __name__ == "__main__":
    indexer = FileIndexer(watch_dir="/your/directory")  # Replace with your target directory
    observer = Observer()
    observer.schedule(FileChangeHandler(indexer), path=indexer.watch_dir, recursive=True)
    observer.start()
    print(f"Watching for changes in {indexer.watch_dir}...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
