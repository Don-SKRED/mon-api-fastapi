import os
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- CONFIGURATION DB ---
# NE COLLE PAS TON LIEN NEON ICI ! 
# On utilise os.getenv pour que Render le trouve tout seul plus tard.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODÈLE ---
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)

Base.metadata.create_all(bind=engine)

class MessageCreate(BaseModel):
    content: str

# --- APP ---
app = FastAPI()

# Autorise ton futur site Netlify à parler à ce backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/messages")
def get_messages(db: Session = Depends(get_db)):
    return db.query(Message).all()

@app.post("/messages")
def post_message(msg: MessageCreate, db: Session = Depends(get_db)):
    new_msg = Message(content=msg.content)
    db.add(new_msg)
    db.commit()
    return {"status": "success"}