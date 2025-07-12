#Calendario/model/model.py

from typing import Optional
import reflex as rx
from datetime import datetime

#Modelos de objetos que se crearán en la app a partir de los registros en base de datos

class User(rx.Base):
    #Modelo para el usuario
    id: int
    username: str
    pasw: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    created_at: Optional[datetime] = None


class Calendar(rx.Base):
    #Modelo para el calendario
    id: int
    name: str
    owner_id: int
    shared_with: Optional[list[int]] = []
    created_at: datetime
    start_date : datetime
    end_date : datetime


class Meal(rx.Base):
    #Modelo para las comidas
    id: int
    name: str 
    description: str = None


class Day(rx.Base):
    #Modelo para cada dia en el calendario
    id: int
    calendar_id: int
    date: datetime
    meal: str = None
    dinner: str = None
    comments: bool = False


class Comment(rx.Base):
    #Modelo para los comentarios
    id: int
    day_id: int  
    content: str 
    owner_id: int 
    created_at: datetime
    user: User