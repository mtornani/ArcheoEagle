"""
Project save/load with SQLite — lightweight persistence for Archaeo-Sentinel MVP.
"""
import sqlite3
import json
import datetime
import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

router = APIRouter()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "archaeo_sentinel.db")


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            aoi_geojson TEXT,
            candidates TEXT,
            stats TEXT,
            layers_config TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


class ProjectSaveRequest(BaseModel):
    name: str
    description: str = ""
    aoi_geojson: Optional[Dict[str, Any]] = None
    candidates: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = None
    layers_config: Optional[Dict[str, Any]] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    aoi_geojson: Optional[Dict[str, Any]] = None
    candidates: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = None
    layers_config: Optional[Dict[str, Any]] = None


@router.post("/save")
def save_project(req: ProjectSaveRequest):
    """Save a new project snapshot."""
    now = datetime.datetime.now().isoformat()
    conn = _get_db()
    cursor = conn.execute(
        """INSERT INTO projects (name, description, aoi_geojson, candidates, stats, layers_config, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            req.name,
            req.description,
            json.dumps(req.aoi_geojson) if req.aoi_geojson else None,
            json.dumps(req.candidates) if req.candidates else None,
            json.dumps(req.stats) if req.stats else None,
            json.dumps(req.layers_config) if req.layers_config else None,
            now, now,
        ),
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return {"message": "Progetto salvato", "id": project_id, "created_at": now}


@router.get("/list")
def list_projects():
    """List all saved projects (metadata only)."""
    conn = _get_db()
    rows = conn.execute(
        "SELECT id, name, description, created_at, updated_at FROM projects ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    return {
        "projects": [
            {"id": r["id"], "name": r["name"], "description": r["description"],
             "created_at": r["created_at"], "updated_at": r["updated_at"]}
            for r in rows
        ]
    }


@router.get("/load/{project_id}")
def load_project(project_id: int):
    """Load a complete project by ID."""
    conn = _get_db()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    if not row:
        return {"error": "Progetto non trovato", "id": project_id}

    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "aoi_geojson": json.loads(row["aoi_geojson"]) if row["aoi_geojson"] else None,
        "candidates": json.loads(row["candidates"]) if row["candidates"] else None,
        "stats": json.loads(row["stats"]) if row["stats"] else None,
        "layers_config": json.loads(row["layers_config"]) if row["layers_config"] else None,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.put("/update/{project_id}")
def update_project(project_id: int, req: ProjectUpdateRequest):
    """Update an existing project."""
    conn = _get_db()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not row:
        conn.close()
        return {"error": "Progetto non trovato"}

    now = datetime.datetime.now().isoformat()
    updates = {"updated_at": now}
    if req.name is not None:
        updates["name"] = req.name
    if req.description is not None:
        updates["description"] = req.description
    if req.aoi_geojson is not None:
        updates["aoi_geojson"] = json.dumps(req.aoi_geojson)
    if req.candidates is not None:
        updates["candidates"] = json.dumps(req.candidates)
    if req.stats is not None:
        updates["stats"] = json.dumps(req.stats)
    if req.layers_config is not None:
        updates["layers_config"] = json.dumps(req.layers_config)

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [project_id]
    conn.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return {"message": "Progetto aggiornato", "id": project_id, "updated_at": now}


@router.delete("/delete/{project_id}")
def delete_project(project_id: int):
    """Delete a project."""
    conn = _get_db()
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return {"message": "Progetto eliminato", "id": project_id}
