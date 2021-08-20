from pydantic import BaseModel

class logout(BaseModel):
    Correo:str
    Contraseña:str

