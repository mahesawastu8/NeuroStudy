"""
NeuroStudy Enterprise REST API (FastAPI Backend)
Powers next-gen web, mobile, and institutional hospital LMS integrations.
"""
from fastapi import FastAPI, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Optional, List
import datetime
from core.db import get_connection
from core.rate_limiter import RateLimiter
from core.visual_engine import get_module_visual_atlas

app = FastAPI(
    title="NeuroStudy MedTech AI Core API",
    description="Evidence-based Cognitive Medical Operating System & Curriculum Engine",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "NeuroStudy MedTech AI Engine",
        "version": "2.5.0",
        "standard": "Harrison 21st / Guyton 14th / Robbins 10th / Katzung 13th / Norman & Eva",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "modules": "/api/modules",
            "leaderboard": "/api/leaderboard"
        }
    }

@app.get("/api/health")
def health_check():
    conn = get_connection()
    mod_count = conn.execute("SELECT COUNT(*) as c FROM modules").fetchone()["c"]
    conn.close()
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "database": "SQLite WAL Enterprise Mode",
        "indexed_modules": mod_count,
        "sla": "99.9% uptime"
    }

@app.get("/api/modules")
def list_modules(
    blok: Optional[str] = Query(None, description="Filter by blok, e.g. BMS 1, BMS 2, BDT"),
    search: Optional[str] = Query(None, description="Search keyword in module title"),
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)
):
    # Unwrap Query parameter defaults if called directly in Python
    if hasattr(blok, "default"):
        blok = blok.default
    if hasattr(search, "default"):
        search = search.default
    if hasattr(limit, "default"):
        limit = limit.default
    if hasattr(offset, "default"):
        offset = offset.default
    limit = int(limit) if limit is not None else 50
    offset = int(offset) if offset is not None else 0

    conn = get_connection()
    query = "SELECT id, title, blok, slide_count, text_length, has_visuals FROM modules WHERE 1=1"
    params = []
    if blok and blok != "Semua Blok":
        query += " AND blok = ?"
        params.append(blok)
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
    query += " ORDER BY title ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return {
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "modules": [dict(r) for r in rows]
    }

@app.get("/api/modules/{module_title}/master-note")
def get_master_note(module_title: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM master_notes WHERE module_title = ? OR module_title = ?", (module_title, module_title.replace("_", " ")))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Master Note belum disintesis untuk modul ini.")
    return dict(row)

@app.get("/api/modules/{module_title}/visuals")
def get_visuals(module_title: str):
    visuals = get_module_visual_atlas(module_title)
    return {
        "module": module_title,
        "visual_count": len(visuals),
        "items": visuals
    }

@app.get("/api/leaderboard")
def get_leaderboard():
    conn = get_connection()
    rows = conn.execute("SELECT username, full_name, avatar, streak_days, cards_reviewed, mastery_index, badge_title FROM peer_leaderboard ORDER BY mastery_index DESC").fetchall()
    conn.close()
    return {"leaderboard": [dict(r) for r in rows]}
