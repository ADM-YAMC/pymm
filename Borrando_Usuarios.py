from pydantic import BaseModel

class Borrar_Usuarios(BaseModel):
    IdAdmin:str
    IdUsuario:str