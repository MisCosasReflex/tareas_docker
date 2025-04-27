"""
Schemas Pydantic para validación de datos de usuario.
"""
from pydantic import BaseModel, constr, EmailStr

class UsuarioCreate(BaseModel):
    nombre: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6, max_length=128)
    es_admin: bool = False

    class Config:
        orm_mode = True
