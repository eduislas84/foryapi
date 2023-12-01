import logging
import fastapi
import sqlite3
from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Crea la base de datos
conn = sqlite3.connect("contactos.db")

app = fastapi.FastAPI()

origins = [
    "http://localhost:8080",
    "https://heroku-mysql-frontend-ac0fa64dec05.herokuapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   


class Contacto(BaseModel):
    email : str
    nombre : str
    telefono : str

@app.post("/contactos")
async def crear_contacto(contacto: Contacto):
    try:
        # Verificar si el contacto ya existe
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM contactos WHERE email = ?', (contacto.email,))
        count = c.fetchone()[0]

        if count > 0:
            # El contacto ya existe, devolver un error
            raise HTTPException(status_code=400, detail="El contacto ya existe")

        # Si no hay duplicados, proceder con la inserción
        c.execute('INSERT INTO contactos (email, nombre, telefono) VALUES (?, ?, ?)',
                  (contacto.email, contacto.nombre, contacto.telefono))
        conn.commit()
        
        return contacto
    except Exception as e:
        logging.error(str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/contactos")
async def obtener_contactos():
    """Obtiene todos los contactos."""
    # TODO Consulta todos los contactos de la base de datos y los envia en un JSON
    c = conn.cursor()
    c.execute('SELECT * FROM contactos;')
    response = []
    for row in c:
        contacto = {"email":row[0],"nombre":row[1], "telefono":row[2]}
        response.append(contacto)
    return response


@app.get("/contactos/{email}")
async def obtener_contacto(email: str):
    """Obtiene un contacto por su email."""
    # Consulta el contacto por su email
    c = conn.cursor()
    c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
    contacto = None
    for row in c:
        contacto = {"email":row[0],"nombre":row[1],"telefono":row[2]}
    return contacto


@app.put("/contactos/{email}")
async def actualizar_contacto(email: str, contacto: Contacto):
    """Actualiza un contacto."""
    c = conn.cursor()
    c.execute('UPDATE contactos SET nombre = ?, telefono = ? WHERE email = ?',
              (contacto.nombre, contacto.telefono, email))
    conn.commit()
    return contacto

@app.delete("/contactos/{email}")
async def eliminar_contacto(email: str):
    """Elimina un contacto."""
    # TODO Elimina el contacto de la base de datos
    c = conn.cursor()
    c.execute('DELETE FROM contactos WHERE email = ?', (email,))
    conn.commit()
    return {"mensaje":"Contacto eliminado"}