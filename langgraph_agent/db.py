import sqlite3
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional

# Ensure the data directory exists
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "agent_state.db"

def init_db():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            session_start TIMESTAMP NOT NULL,
            session_end TIMESTAMP,
            metadata TEXT
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS user_state (
            username TEXT PRIMARY KEY,
            first_seen TIMESTAMP NOT NULL,
            last_active TIMESTAMP NOT NULL,
            conversation_count INTEGER DEFAULT 0,
            preferences TEXT
        );
    """)

    conn.commit()
    conn.close()

class StateManager:
    def __init__(self):
        """Initialize the state manager and ensure database exists."""
        init_db()
        self.current_session_id = None

    def _get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(DB_PATH)

    def start_session(self, username: str, metadata: Dict = None) -> int:
        """Start a new session for a user."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Update or create user state
            cursor.execute("""
                INSERT INTO user_state (username, first_seen, last_active, conversation_count)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(username) DO UPDATE SET
                    last_active = ?,
                    conversation_count = conversation_count + 1
            """, (username, datetime.now(), datetime.now(), datetime.now()))

            # Create new session
            cursor.execute("""
                INSERT INTO sessions (username, session_start, metadata)
                VALUES (?, ?, ?)
            """, (username, datetime.now(), json.dumps(metadata or {})))

            session_id = cursor.lastrowid
            self.current_session_id = session_id

            conn.commit()
            return session_id

        finally:
            conn.close()

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the current session."""
        if not self.current_session_id:
            raise ValueError("No active session")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO messages (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (self.current_session_id, role, content, datetime.now()))
            conn.commit()
        finally:
            conn.close()

    def get_session_messages(self, session_id: Optional[int] = None) -> List[Dict]:
        """Get all messages for a session."""
        session_id = session_id or self.current_session_id
        if not session_id:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT role, content, timestamp
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))

            return [
                {
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2]
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_user_history(self, username: str) -> Dict:
        """Get user's conversation history and stats."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get user stats
            cursor.execute("""
                SELECT first_seen, last_active, conversation_count
                FROM user_state
                WHERE username = ?
            """, (username,))

            user_row = cursor.fetchone()
            if not user_row:
                return {
                    "user_stats": {
                        "first_seen": datetime.now().isoformat(),
                        "last_active": datetime.now().isoformat(),
                        "conversation_count": 0
                    },
                    "recent_sessions": []
                }

            # Get recent sessions
            cursor.execute("""
                SELECT id, session_start, session_end, metadata
                FROM sessions
                WHERE username = ?
                ORDER BY session_start DESC
                LIMIT 5
            """, (username,))

            sessions = []
            for session_row in cursor.fetchall():
                session_id = session_row[0]
                # Get messages for this session
                cursor.execute("""
                    SELECT role, content, timestamp
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp
                """, (session_id,))

                messages = [
                    {
                        "role": row[0],
                        "content": row[1],
                        "timestamp": row[2]
                    }
                    for row in cursor.fetchall()
                ]

                sessions.append({
                    "session_id": session_id,
                    "start": session_row[1],
                    "end": session_row[2],
                    "metadata": json.loads(session_row[3] or "{}"),
                    "messages": messages
                })

            return {
                "user_stats": {
                    "first_seen": user_row[0],
                    "last_active": user_row[1],
                    "conversation_count": user_row[2]
                },
                "recent_sessions": sessions
            }
        finally:
            conn.close()

    def end_session(self) -> None:
        """End the current session."""
        if not self.current_session_id:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE sessions
                SET session_end = ?
                WHERE id = ?
            """, (datetime.now(), self.current_session_id))
            conn.commit()
        finally:
            conn.close()
            self.current_session_id = None

    def get_session_start(self) -> str:
        """Get the start time of the current session."""
        if not self.current_session_id:
            return datetime.now().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT session_start
                FROM sessions
                WHERE id = ?
            """, (self.current_session_id,))
            row = cursor.fetchone()
            return row[0] if row else datetime.now().isoformat()
        finally:
            conn.close()

    def get_username(self) -> Optional[str]:
        """Get the username for the current session."""
        if not self.current_session_id:
            return None

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT username
                FROM sessions
                WHERE id = ?
            """, (self.current_session_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()
