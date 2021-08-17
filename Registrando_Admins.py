from pydantic import BaseModel

class Registro_Admins(BaseModel):
    Nombre:str
    Apellido:str
    Fecha_Nacimiento:str
    Correo:str
    Contraseña:str
    Rol:str