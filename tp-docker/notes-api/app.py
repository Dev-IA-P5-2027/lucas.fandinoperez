# app.py 

from fastapi import FastAPI, HTTPException 

from pydantic import BaseModel 

from typing import Optional 

import sqlite3, os 

 

app = FastAPI(title="API Notes", version="1.0") 

DB_PATH = "/data/notes.db" 

 

# Pydantic : FastAPI utilise ces classes pour valider automatiquement 

# les données reçues dans les requêtes POST/PUT 

class NoteCreate(BaseModel):

    titre: str

    contenu: Optional[str] = ""



class NoteUpdate(BaseModel):

    titre: Optional[str] = None

    contenu: Optional[str] = None

 

def get_db(): 

    os.makedirs("/data", exist_ok=True) 

    conn = sqlite3.connect(DB_PATH) 

    conn.row_factory = sqlite3.Row 

    return conn 

 

def init_db(): 

    conn = get_db() 

    conn.execute(""" 

        CREATE TABLE IF NOT EXISTS notes ( 

            id      INTEGER PRIMARY KEY AUTOINCREMENT, 

            titre   TEXT NOT NULL, 

            contenu TEXT, 

            date    TEXT DEFAULT CURRENT_TIMESTAMP 

        )""") 

    conn.commit() 

    conn.close() 

 

# Démarrage : créer la table si elle n'existe pas encore 

@app.on_event("startup") 

def startup(): 

    init_db() 

 

@app.get("/notes") 

def get_notes(): 

    conn = get_db() 

    rows = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall() 

    conn.close() 

    return [dict(r) for r in rows] 

 

@app.post("/notes", status_code=201) 

def create_note(note: NoteCreate): 

    # FastAPI valide automatiquement que 'titre' est présent et non vide 

    # grâce à la classe NoteCreate ci-dessus 

    conn = get_db() 

    conn.execute("INSERT INTO notes (titre, contenu) VALUES (?, ?)", 

                 (note.titre, note.contenu)) 

    conn.commit() 

    conn.close() 

    return {"message": "Note créée"} 

 

@app.put("/notes/{note_id}")

def update_note(note_id: int, note: NoteUpdate):

    updates = note.dict(exclude_unset=True)

    if not updates:

        raise HTTPException(status_code=400, detail="Aucun champ à modifier")

    conn = get_db()

    existing = conn.execute("SELECT id FROM notes WHERE id = ?", (note_id,)).fetchone()

    if existing is None:

        conn.close()

        raise HTTPException(status_code=404, detail=f"Note {note_id} introuvable")

    champs = ", ".join(f"{k} = ?" for k in updates)

    valeurs = list(updates.values()) + [note_id]

    conn.execute(f"UPDATE notes SET {champs} WHERE id = ?", valeurs)

    conn.commit()

    conn.close()

    return {"message": f"Note {note_id} modifiée"}



@app.delete("/notes/{note_id}")

def delete_note(note_id: int): 

    conn = get_db() 

    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,)) 

    conn.commit() 

    conn.close() 

    return {"message": f"Note {note_id} supprimée"} 