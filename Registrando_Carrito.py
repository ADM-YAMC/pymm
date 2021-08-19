from pydantic import BaseModel

class Registro_Carrito(BaseModel):
    IdUsuarios:int
    IdProducto:int
    Nombre_producto:str
    Cantidad:str
    Suma_total:str
    Categoria:str
    Descripcion:str
    Foto:str
    N_Stock:str