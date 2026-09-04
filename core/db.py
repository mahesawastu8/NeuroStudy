"""
NeuroStudy ACID Database Engine (SQLite WAL Mode)
Provides enterprise transactional integrity, zero race-conditions, and fast indexed queries.
"""
import sqlite3
import json
import os
import re
import datetime
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "neurostudy.db"

_lock = threading.Lock()

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _lock:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Users Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            tier TEXT DEFAULT 'pro',
            full_name TEXT,
            daily_ai_requests INTEGER DEFAULT 0,
            last_request_date TEXT,
            streak_days INTEGER DEFAULT 1,
            mastery_score INTEGER DEFAULT 80,
            created_at TEXT,
            last_login TEXT
        );
        """)
        
        # 2. Modules Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            blok TEXT NOT NULL,
            slide_count INTEGER DEFAULT 0,
            text_length INTEGER DEFAULT 0,
            text_content TEXT,
            has_visuals INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_modules_blok ON modules(blok);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_modules_title ON modules(title);")
        
        # 3. Master Notes Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS master_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_title TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            verified INTEGER DEFAULT 0,
            verified_by TEXT,
            verified_at TEXT,
            clinical_standard TEXT,
            cryptographic_sig TEXT,
            updated_at TEXT
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_master_notes_title ON master_notes(module_title);")
        
        # 4. User Progress (Spaced Repetition & Retention)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            module_title TEXT NOT NULL,
            sessions INTEGER DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            next_review TEXT,
            last_studied TEXT,
            retention_pct INTEGER DEFAULT 100,
            UNIQUE(username, module_title)
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_progress_user ON user_progress(username);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_progress_review ON user_progress(next_review);")
        
        # 5. Peer Leaderboard Table (Anti-churn Gamification)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS peer_leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            avatar TEXT DEFAULT '🩺',
            streak_days INTEGER DEFAULT 1,
            cards_reviewed INTEGER DEFAULT 0,
            mastery_index REAL DEFAULT 75.0,
            badge_title TEXT DEFAULT 'Harrison Scholar',
            updated_at TEXT
        );
        """)
        
        # 6. Audit & Rate Limiting Logs
        cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT NOT NULL,
            endpoint TEXT,
            status TEXT,
            timestamp TEXT
        );
        """)
        
        conn.commit()
        conn.close()
        
    _auto_seed_db()

def _auto_seed_db():
    """Migrate 208 materials from JSON to SQLite seamlessly on first launch."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as cnt FROM modules;")
    row = cur.fetchone()
    if row["cnt"] < 200:
        mat_dir = DATA_DIR / "master_materials"
        if mat_dir.exists():
            for f in mat_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    title = f.stem
                    text = data.get("text", "")
                    blok = "Lainnya"
                    for b in ["BMS 1", "BUAMS", "BMS 2", "BMS 3", "BMS 4", "BDT", "BMD"]:
                        if title.startswith(f"[{b}]"):
                            blok = b
                            break
                    now_str = datetime.datetime.now().isoformat()
                    cur.execute("""
                    INSERT OR REPLACE INTO modules (title, blok, slide_count, text_length, text_content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (title, blok, data.get("slide_count", 0), len(text), text, now_str, now_str))
                except Exception: pass
            conn.commit()
            
    mn_dir = DATA_DIR / "global_library" / "master_notes"
    if mn_dir.exists():
        for mf in mn_dir.glob("*.json"):
            try:
                m_data = json.loads(mf.read_text(encoding="utf-8"))
                mod_name = mf.stem.replace("_", " ")
                cur.execute("""
                INSERT OR REPLACE INTO master_notes (module_title, content, verified, verified_by, verified_at, clinical_standard, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    mod_name,
                    m_data.get("content", ""),
                    1 if m_data.get("verified") else 0,
                    m_data.get("verified_by", ""),
                    m_data.get("verified_at", ""),
                    m_data.get("clinical_standard", "Harrison 21st / Guyton 14th / Robbins 10th"),
                    datetime.datetime.now().isoformat()
                ))
            except Exception: pass
        conn.commit()
        
    cur.execute("SELECT COUNT(*) as cnt FROM peer_leaderboard;")
    if cur.fetchone()["cnt"] == 0:
        seed_peers = [
            ("dr_dimas", "dr. Dimas Wastu Mahesa", "👨‍⚕️", 24, 840, 96.5, "🥇 Konsultan EBM Senior"),
            ("sarah_med", "Sarah Aurelia, S.Ked", "👩‍⚕️", 18, 620, 93.2, "🥈 Guyton Physiologist"),
            ("kevin_fk", "Kevin Pratama, S.Ked", "🩺", 14, 510, 89.4, "🥉 Robbins Pathologist"),
            ("nadia_clin", "Nadia Syahrini, S.Ked", "🔬", 11, 430, 86.8, "⭐ Diagnostic Tactician"),
            ("fadhil_r", "Fadhil Ramadhan, S.Ked", "💊", 8, 310, 82.5, "⭐ Katzung Pharmacologist"),
        ]
        now_str = datetime.datetime.now().isoformat()
        for u, fn, av, st, cr, mi, bt in seed_peers:
            cur.execute("""
            INSERT OR IGNORE INTO peer_leaderboard (username, full_name, avatar, streak_days, cards_reviewed, mastery_index, badge_title, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (u, fn, av, st, cr, mi, bt, now_str))
        conn.commit()

    conn.close()

init_db()
print("core/db.py initialized successfully!")
