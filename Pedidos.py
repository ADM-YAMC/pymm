from pydantic import BaseModel

class Registro_Pedidos(BaseModel):
    IdUsuario:int
    Telefono:str
    Total:str
    Direccion:str
    Latitud:str
    Longitud:str