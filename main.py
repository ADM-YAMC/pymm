from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends, Query
from conexion import conn
from pydantic import BaseModel
import Variables
import secrets
from Usuarios import Usuarios

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Logaut(BaseModel):
    Correo:str
    Contraseña:str

@app.get("/")
def read_root():
    try:
        cursor = conn.cursor()
        cursor.execute("update  [dbo].[Prueba] set Nombre = 'Vicente' where Nombre = 'Yunior'")
        lista = []
        query = "Select Nombre from [dbo].[Prueba]"
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        contenido = cursor.fetchall()
        for row in contenido:
            lista.append(row)
        conn.close()
        return lista
    except TypeError:
        return "Ocurrio un error... "

@app.post("/api/login/")
def Login(a:Logaut):
    contentt = {}
    token = secrets.token_hex(80)
    query = "select * from Cliente_Usuario where Correo = '"+a.Correo+"' and Contraseña = '"+a.Contraseña+"'"
    cursor = conn.cursor()
    cursor.execute(query)
    contenido = cursor.fetchall()
    for i in contenido:
        Variables.h = i
        Variables.IdUser = i[0]
        Variables.user = i[4]
        Variables.passw = i[5]
    if Variables.user == a.Correo and Variables.passw == a.Contraseña:
        update = "UPDATE [dbo].[Cliente_Usuario] SET Token = '"+token+"' WHERE IdUsuarios = '"+str(Variables.IdUser)+"'"
        cursor.execute(update)
        conn.commit()
        cursor.execute("select COUNT(IdCarrito) as cantidad from Carrito where IdUsuarios = '"+str(Variables.IdUser)+"' GROUP BY IdUsuarios")
        content = cursor.fetchall()
        for i in content:
                contentt = {"ok":True,"Cantidad":i[0], "Datos_Usuarios": {"IdUsuario": Variables.h[0], "Nombre":Variables.h[1], "Apellido": Variables.h[2], "Fecha_Nacimiento":Variables.h[3], "Rol":Variables.h[6], "Token":token}}
        if contentt == {}:
            #conn.close()
            return {"ok":True, "Datos_Usuarios": {"IdUsuario": Variables.h[0], "Nombre":Variables.h[1], "Apellido": Variables.h[2], "Fecha_Nacimiento":Variables.h[3], "Rol":Variables.h[6], "Token":token}}
        else:
            #conn.close()
            return contentt
    else:
        return {"ok":False}


@app.get("/api/Relogin/{Token}")
def ReLogin(Token:str):
    contentt = {}
    query = "select * from Cliente_Usuario where Token = '"+str(Token)+"'"
    cursor = conn.cursor()
    cursor.execute(query)
    contenido = cursor.fetchall()
    for i in contenido:
        Variables.h = i
        Variables.IdUser = i[0]
        Variables.token = i[7] 
    if Variables.token == Token:
        cursor.execute("select COUNT(IdCarrito) as cantidad from Carrito where IdUsuarios = '"+str(Variables.IdUser)+"' GROUP BY IdUsuarios")
        content = cursor.fetchall()
        for i in content:
                contentt = {"ok":True,"Cantidad":i[0], "Datos_Usuarios": {"IdUsuario": Variables.h[0], "Nombre":Variables.h[1], "Apellido": Variables.h[2], "Fecha_Nacimiento":Variables.h[3], "Rol":Variables.h[6]}}
        if contentt == {}:
            #conn.close()
            return {"ok":True, "Datos_Usuarios": {"IdUsuario": Variables.h[0], "Nombre":Variables.h[1], "Apellido": Variables.h[2], "Fecha_Nacimiento":Variables.h[3], "Rol":Variables.h[6]}}
        else:
            #conn.close()
            return contentt
    else:
        return {"ok":False}


@app.post("/api/Registro_Usuarios")
def Registro_Usuarios(u:Usuarios):
    try:
        query= "Select Correo from Cliente_Usuario where Correo = '"+u.Correo+"'"
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido:
            Variables.Correo = i[0]
        if Variables.Correo == u.Correo:
            return {"ok": False}
        else:
            Datos = (u.Nombre,u.Apellido,u.Fecha_Nacimiento,u.Correo,u.Contraseña, u.Rol)
            consulta = '''INSERT INTO [dbo].[Cliente_Usuario]
                ([Nombre]
                ,[Apellido]
                ,[Fecha_Nacimiento]
                ,[Correo]
                ,[Contraseña]
                ,[Rol])
                VALUES
                (%s,%s,%s,%s,%s,%s)'''
            cursor.execute(consulta,Datos)
            conn.commit()
            return {"ok":True}
    except:
        return "Error"


@app.put("/app/CerrarSesion/{idUser}")
def CerrarSesion(idUser:str):
    try:
        cursor = conn.cursor()
        update = "UPDATE [dbo].[Cliente_Usuario] SET Token = 'NULL' WHERE IdUsuarios = '"+str(idUser)+"'"
        cursor.execute(update)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}


