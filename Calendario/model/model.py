from typing import Optional
import reflex as rx
from datetime import datetime

class User(rx.Base):
    """
    Modelo para usuarios.
    """
    id: int
    username: str
    pasw: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    created_at: Optional[datetime] = None


class Calendar(rx.Base):
    """
    Modelo para calendarios.
    """
    id: int
    name: str
    owner_id: int  # Relación con el usuario propietario
    shared_with: Optional[list[int]] = []  # Permite None pero inicializa como lista vacía
    created_at: datetime
    start_date : datetime
    end_date : datetime


class Meal(rx.Base):
    """
    Modelo para opciones de comidas y cenas.
    """
    id: int
    name: str  # Nombre de la comida o cena (ejemplo: "Pizza", "Ensalada")
    description: str = None  # Descripción opcional (ejemplo: ingredientes)


class Day(rx.Base):
    id: int
    calendar_id: int
    date: datetime
    meal: str = None
    dinner: str = None
    comments: bool = False


class Comment(rx.Base):
    """
    Modelo para comentarios asociados a un día.
    """
    id: int
    day_id: int  # Relación con el día
    content: str  # Contenido del comentario
    owner_id: int  # Usuario que hizo el comentario
    created_at: datetime
    user: User