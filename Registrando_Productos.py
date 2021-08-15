from pydantic import BaseModel

class Registro_Productos(BaseModel):
    Nombre_producto:str
    Categoria_producto:str
    Foto_producto:str
    Descripcion_producto:str
    Stock:str
    Precio:str