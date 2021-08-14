from pydantic import BaseModel
class Usuarios(BaseModel):
    Nombre:str
    Apellido:str
    Fecha_Nacimiento:str
    Correo:str
    Contraseña:str
    Rol:str