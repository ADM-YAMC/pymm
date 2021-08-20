from Registrando_Carrito import Registro_Carrito
from Borrando_Usuarios import Borrar_Usuarios
from Registrando_Admins import Registro_Admins
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends, Query
from pydantic.types import condecimal, conset
from conexion import conn
from pydantic import BaseModel
import Variables
import secrets
from Usuarios import Usuarios
from Logout import logout
from Registrando_Categorias import Registro_Categorias
from Registrando_Productos import Registro_Productos
from Registrando_Slides import Registro_Slides
from Pedidos import Registro_Pedidos
import pymssql

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#region COSAS DE ADMINS
@app.get("/")
def read_root():
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
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

@app.get("/api/Mostrar_Usuarios")
def Mostrar_Usuarios():
    query = "select * from  Cliente_Usuario"
    conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
    cursor = conn.cursor()
    cursor.execute(query)
    contenido = cursor.fetchall()
    Variables.cantidad.clear()
    for i in contenido:
        Variables.cantidad.append({"IdUsuario": i[0],
                                    "Nombre_Usuario": i[1],
                                    "Apellido_Usuario": i[2],
                                    "Fecha_Nacimiento": i[3],
                                    "Correo": i[4],
                                    "Contraseña": i[5],
                                    "Rol": i[6],
                                    "Token": i[7]})
    return Variables.cantidad

@app.get("/api/Mostrar_Conectados")
def Mostrar_Conectados():
    try:
        query = "select COUNT(IdUsuarios) as Conectados from Cliente_Usuario where Token <> 'NULL'"
        query2 = "select COUNT(IdUsuarios) as Conectados from Cliente_Usuario where Token = 'NULL'"
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido:
            aux1 = i
            cursor.execute(query2)
            contenido2 = cursor.fetchall()
            for x in contenido2:
                aux2 = x
        return {"Conectados":aux1,"Desconectados":aux2}
    except:
        return "Error" 
#endregion

#region LOGINS
@app.post("/api/login")
def Login(a:logout):
    try:
        contentt = {}
        token = secrets.token_hex(80)
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
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
            cursor = conn.cursor()
            cursor.execute(update)
            conn.commit()
            cursor.execute("select COUNT(IdCarrito) as cantidad from Carrito where IdUsuarios = '"+str(Variables.IdUser)+"' GROUP BY IdUsuarios")
            content = cursor.fetchall()
            conn.commit()
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
    except:
        conn.ping(reconnect=True)
    

@app.get("/api/Relogin/{Token}")
def ReLogin(Token:str):
    contentt = {}
    conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
    query = "select * from Cliente_Usuario where Token = '"+str(Token)+"'"
    cursor = conn.cursor()
    cursor.execute(query)
    contenido = cursor.fetchall()
    for i in contenido:
        Variables.h = i
        Variables.IdUser = i[0]
        Variables.token = i[7] 
    if Variables.token == Token:
        cursor = conn.cursor()
        cursor.execute("select COUNT(IdCarrito) as cantidad from Carrito where IdUsuarios = '"+str(Variables.IdUser)+"' GROUP BY IdUsuarios")
        content = cursor.fetchall()
        for i in content:
                contentt = {"ok":True,"Cantidad":i[0], "Datos_Usuarios": {"IdUsuario": Variables.h[0], "Nombre":Variables.h[1], "Apellido": Variables.h[2], "Fecha_Nacimiento":Variables.h[3], "Rol":Variables.h[6]}}
        if contentt == {}:
            conn.close()
            return {"ok":True, "Datos_Usuarios": {"IdUsuario": Variables.h[0], "Nombre":Variables.h[1], "Apellido": Variables.h[2], "Fecha_Nacimiento":Variables.h[3], "Rol":Variables.h[6]}}
        else:
            conn.close()
            return contentt
    else:
        return {"ok":False}

@app.post("/api/CerrarSesion/{idUser}")
def CerrarSesion(idUser:str):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor()
        update = "UPDATE [dbo].[Cliente_Usuario] SET Token = 'NULL' WHERE IdUsuarios = '"+str(idUser)+"'"
        cursor.execute(update)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}

#endregion

#region CRUD DE ADMINS
@app.post("/api/Registro_Admins/{IdAdmin}")
def Registro_Administradores(IdAdmin:str, u:Registro_Admins):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query= "Select Rol from Cliente_Usuario where IdUsuarios = '"+str(IdAdmin)+"'"
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido:
            Variables.aux3 = i[0]
        if Variables.aux3 != "SuperAdmin":
            return {"ok": False}
        else:
            Datos = (u.Nombre,u.Apellido,u.Fecha_Nacimiento,u.Correo,u.Contraseña, "Administrador")
            consulta = '''INSERT INTO [dbo].[Cliente_Usuario]
                ([Nombre]
                ,[Apellido]
                ,[Fecha_Nacimiento]
                ,[Correo]
                ,[Contraseña]
                ,[Rol])
                VALUES
                (%s,%s,%s,%s,%s,%s)'''
            cursor = conn.cursor()
            cursor.execute(consulta,Datos)
            conn.commit()
            return {"ok":True}
    except:
        return "Error"

@app.post("/api/Borrar_Usuarios")
def Borrado_Usuarios(x:Borrar_Usuarios):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query= "Select Rol from Cliente_Usuario where IdUsuarios = '"+x.IdAdmin+"'"
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido:
            Variables.aux3 = i[0]
        if Variables.aux3 == "SuperAdmin":
            borrado = "delete from Cliente_Usuario where IdUsuarios = '"+x.IdUsuario+"'"
            cursor.execute(borrado)
            conn.commit()
            return {"ok":True}
        elif Variables.aux3 == "Administrador" and x.IdUsuario == "Cliente":
            borrado = "delete from Cliente_Usuario where IdUsuarios = '"+x.IdUsuario+"'"
            cursor.execute(borrado)
            conn.commit()
            return {"ok":True}
        else:
            return {"ok":False}
    except:
        return "Error"
        
@app.post("/api/Modificar_Usuarios/{Rol}")
def Modificar_Usuarios(Rol:str, x:Borrar_Usuarios):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query= "Select Rol from Cliente_Usuario where IdUsuarios = '"+x.IdAdmin+"'"
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido:
            Variables.aux3 = i[0]
        if Variables.aux3 == "SuperAdmin":
            cambio = "UPDATE [dbo].[Cliente_Usuario] SET Rol = '"+str(Rol)+"' WHERE IdUsuarios = '"+(x.IdUsuario)+"'"
            cursor.execute(cambio)
            conn.commit()
            return {"ok":True}
        else:
            return {"ok":False}
    except:
        return "Error"
#endregion

#region VAINAS DE USUARIOS
@app.post("/api/Registro_Usuarios")
def Registro_Usuarios(u:Usuarios):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
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
            cursor = conn.cursor()
            cursor.execute(consulta,Datos)
            conn.commit()
            return {"ok":True}
    except:
        return "Error"

@app.post("/api/Actualizar_Clave_Usuario/{ClaveNueva}")
def Actualizar_Clave_Usuario(a:logout, ClaveNueva:str):
    conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
    query = "select * from Cliente_Usuario where Correo = '"+a.Correo+"' and Contraseña = '"+a.Contraseña+"'"
    cursor = conn.cursor()
    cursor.execute(query)
    contenido = cursor.fetchall()
    for i in contenido:
        Variables.IdUser = i[0]
        Variables.user = i[4]
        Variables.passw = i[5]
    if Variables.user == a.Correo and Variables.passw == a.Contraseña:
        update = "UPDATE [dbo].[Cliente_Usuario] SET Contraseña = '"+str(ClaveNueva)+"' WHERE IdUsuarios = '"+str(Variables.IdUser)+"'"
        cursor.execute(update)
        conn.commit()
        return {"ok":True}
    else:
        return {"ok":False}
#endregion

#region CRUD DE PRODUCTO
@app.post("/api/Registro_Productos")
def Registros_Productos(x:Registro_Productos):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query = "select Nombre_producto from Producto where Nombre_Producto = '"+str(x.Nombre_producto)+"'"
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido:
            Variables.nombreproducto = i[0]
        if Variables.nombreproducto == x.Nombre_producto:
            return {"ok":False}
        else:
            datos = (x.Nombre_producto, x.Categoria_producto,x.Foto_producto, x.Descripcion_producto, x.Stock, x.Precio)
            consulta = '''INSERT INTO [dbo].[Producto]
                       ([Nombre_producto]
                       ,[Categoria_producto]
                       ,[Foto_producto]
                       ,[Descripcion_producto]
                       ,[Stock]
                       ,[Precio]
                       ,[EstadoCarrito])
                        VALUES(%s,%s,%s,%s,%s,%s,'0')
                       '''
            cursor = conn.cursor()
            cursor.execute(consulta,datos)
            conn.commit()
            return {"ok":True}
    except:
        return "Error"

@app.get("/api/Seleccionar_Todo")
def Seleccionar_Todo():
    Lista = []
    query = "select * from Producto"
    conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
    cursor = conn.cursor()
    cursor.execute(query)
    contenido = cursor.fetchall()
    #Variables.cantidad.clear()
    for i in contenido:
        Lista.append({"IdProducto": i[0],
                                    "Nombre_producto": i[1],
                                    "Categoria_producto": i[2],
                                    "Foto_producto": i[3],
                                    "Descripcion_producto": i[4],
                                    "Stock": i[5],
                                    "Precio": i[6],
                                    "Estado": i[7]})

    return {"ok":True, "data":Lista}


@app.get("/api/Seleccionar_Uno/{IdProducto}")
def Seleccionar_Uno(IdProducto:str):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query = "select * from Producto where IdProducto = '"+str(IdProducto)+"'"
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido:
            Variables.aux = i
        
        if Variables.aux == {}:
            return {"ok":False}
        else:
            return Variables.aux
    except:
        return "Error"

@app.get("/api/Seleccion_Producto_Categoria/{Categoria_Producto}")
def Producto_Categoria(Categoria_Producto:str):
    try:
        Lista = []
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query="select * from Producto where Categoria_producto = '"+str(Categoria_Producto)+"'"
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        contenido = cursor.fetchall()
        #Variables.cantidad.clear()
        for i in contenido:
            Lista.append(i)
        if Lista == []:
            return {"ok":False}
        else:
            return {"ok":True, "data":Lista}
    except:
        "Error"

@app.get("/api/Borrar_Producto/{IdProducto}")
def Borrar_Producto(IdProducto:str):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query = "delete from Producto where IdProducto = '"+str(IdProducto)+"'"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}

@app.post("/api/Actualizar_Producto/{IdProducto}")
def Actualizar_Producto(IdProducto:str, z:Registro_Productos):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        datos = (z.Nombre_producto, z.Categoria_producto, z.Foto_producto, z.Descripcion_producto, z.Stock, z.Precio, IdProducto)
        consulta = '''UPDATE [dbo].[Producto] SET Nombre_producto = %s, Categoria_producto = %s, Foto_producto = %s, Descripcion_producto = %s, Stock = %s, Precio = %s WHERE IdProducto = %s'''
        cursor = conn.cursor()
        cursor.execute(consulta, datos)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}


#endregion

#region CRUD DE CATEGORIAS
@app.post("/api/Registro_Categorias")
def Registro_Categoria(x:Registro_Categorias):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query = "select Nombre_Categoria from Categoria where Nombre_Categoria = '"+str(x.Nombre_categoria)+"'"
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido:
            Variables.nombrecategoria = i[0]
        if Variables.nombrecategoria == x.Nombre_categoria:
            return {"ok":False}
        else:
            datos = (x.Nombre_categoria)
            consulta = '''INSERT INTO [dbo].[Categoria]
                       ([Nombre_categoria])
                        VALUES(%s)
                       '''
            cursor = conn.cursor()
            cursor.execute(consulta,datos)
            conn.commit()
            return {"ok":True}
    except:
        return "Error"

@app.get("/api/Mostrar_Todas_Categoria")
def Seleccionar_Todas_Categorias():
    try:
        Lista = []
        query = "select * from  Categoria"
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        #Variables.cantidad.clear()
        for i in contenido:
            Lista.append({"IdCategoria": i[0],
                                        "Nombre_Categoria": i[1]})

        return Lista
    except:
        return {"ok":False}

@app.get("/api/Mostrar_Una_Categoria/{IdCategoria}")
def Seleccionar_Una_Categoria(IdCategoria:str):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query = "select * from Categoria where IdCategoria = '"+str(IdCategoria)+"'"
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        contenido = cursor.fetchall()
        for i in contenido: 
            Variables.aux = i
        if Variables.aux == {}:
            return {"ok":False}
        else:
            return Variables.aux
    except:
        return "Error"
    

@app.get("/api/Borrar_Categoria/{IdCategoria}")
def Borrar_Categoria(IdCategoria:str):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query = "delete from Categoria where IdCategoria = '"+str(IdCategoria)+"'"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}


@app.post("/api/Actualizar_Categoria/{IdCategoria}")
def Actualizar_Categoria(IdCategoria:str, z:Registro_Categorias):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        datos = (z.Nombre_categoria, IdCategoria)
        consulta = '''UPDATE [dbo].[Categoria] SET Nombre_Categoria = %s WHERE IdCategoria = %s'''
        cursor = conn.cursor()
        cursor.execute(consulta, datos)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}
#endregion

#region CRUD DE SLIDER
@app.post("/api/Registrar_Slides")
def Registrar_Slides(x:Registro_Slides):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        Datos = (x.Titulo, x.Recurso)
        consulta = '''INSERT INTO [dbo].[Slider]
            ([Titulo]
            ,[Recurso])
            VALUES
            (%s,%s)'''
        cursor = conn.cursor()
        cursor.execute(consulta,Datos)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}

@app.get("/api/Mostrar_Un_Slide/{IdSlider}")
def Mostrar_Un_Slide(IdSlider:str):
    query = "select * from Slider where IdSlider = '"+str(IdSlider)+"'"
    conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
    cursor = conn.cursor()
    cursor.execute(query)
    contenido = cursor.fetchall()
    for i in contenido:
        Variables.aux2 = i
    if Variables.aux2 != {}:
        return Variables.aux2
    else:    
        return {"ok":False}

@app.get("/api/Mostrar_Todos_Slides")
def Mostrar_Todos_Slides():
    Lista=[]
    query = "select * from Slider"
    conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
    cursor = conn.cursor()
    cursor.execute(query)
    contenido = cursor.fetchall()
    #Variables.cantidad.clear()
    for i in contenido:
        Lista.append({"IdSlider": i[0],
                                    "Titulo": i[1],
                                    "Recurso": i[2]})
    if Variables.cantidad.count != 0:
        return Lista
    else:
        return {"ok":False}

@app.get("/api/Borrar_Slides/{IdSlider}")
def Borrar_Slides(IdSlider:str):
    try:
        query = "delete from Slider where IdSlider = '"+str(IdSlider)+"'"
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}

@app.post("/api/Actualizar_Slides/{IdSlider}")
def Actualizar_Slides(IdSlider:str, x:Registro_Slides):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        datos = (x.Titulo, x.Recurso, IdSlider)
        consulta = '''UPDATE [dbo].[Slider] SET Titulo = %s, Recurso = %s WHERE IdSlider = %s'''
        cursor = conn.cursor()
        cursor.execute(consulta, datos)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}
#endregion

#region SACAR FECHA
@app.get("/api/Sacar_Cumpleaños/{Mes}")
def Sacar_Cumpleaños(Mes:str):
    try:
        Lista=[]
        query = "select * from  Cliente_Usuario"
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor()
        cursor.execute(query)
        contenido = cursor.fetchall()
        #Variables.cantidad.clear()
        for i in contenido:
            x = i[3]
            aux = x[3] + x[4]
            if aux == Mes:
               Lista.append({"IdUsuario": i[0],
                                    "Nombre_Usuario": i[1],
                                    "Apellido": i[2],
                                    "Fecha_Nacimiento": i[3],
                                    "Correo": i[4],
                                    "Rol": i[6]})
        if Lista != []:
            return Lista
        else:
            return {"ok":False}
    except:
        return "Error"
#endregion

#region CARRITO
@app.post("/api/Registro_Carrito")
def Registrar_Carrito(x:Registro_Carrito):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query = f"exec SP_Carrito {x.IdUsuarios},{x.IdProducto},'{x.Nombre_producto}','{x.Foto}','{x.Descripcion}','{x.Cantidad}','{x.Categoria}','{x.Suma_total}','{x.N_Stock}'"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return {"ok":True}
    except:
        return {"ok":False}



@app.get("/api/Detalles_Carrito/{IdUsuario}")
def Detalle_Carrito(IdUsuario:str):
    try:
        Lista=[]
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query="select * from Detalle where IdUsuarios = '"+str(IdUsuario)+"' and Estado = '0'"
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        contenido = cursor.fetchall()
       # Variables.cantidad.clear()
        for i in contenido:
            Lista.append(i)
        if Lista == []:
            return {"ok":False}
        else:
            return {"ok":True, "data":Lista}
    except:
        return"Error"


@app.get("/api/Detalles_Carrito_Producto_Pagado/{IdUsuario}")
def Detalles_Carrito_Producto_Pagado(IdUsuario:str):
    try:
        Lista=[]
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query="select * from Detalle where IdUsuarios = '"+str(IdUsuario)+"' and Estado = '1'"
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        contenido = cursor.fetchall()
       # Variables.cantidad.clear()
        for i in contenido:
            Lista.append(i)
        if Lista == []:
            return {"ok":False}
        else:
            return {"ok":True, "data":Lista}
    except:
        return"Error"


@app.get("/api/Cantidad_Producto_Carrito/{IdUsuario}")
def Cantidad_Producto_Carrito(IdUsuario):
    try:
        Lista=[]
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor()
        cursor.execute("select COUNT(IdCarrito) as cantidad from Carrito where IdUsuarios = '"+str(IdUsuario)+"' GROUP BY IdUsuarios")
        contenido = cursor.fetchall()
        #Variables.cantidad.clear()
        for i in contenido:
            Lista = i[0]
        if Lista == []:
            return {"ok":False}
        else:
            return {"ok":True,"Cantidad":Lista}
    except:
        "Error"



@app.post("/api/Agregar_Pedidos")
def Agregar_Pedidos(s:Registro_Pedidos):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor()
        Datos = (s.IdUsuario,s.Telefono,s.Total,s.Direccion,s.Latitud,s.Longitud)
        query = '''INSERT INTO [dbo].[Pedidos]
                    ([IdUsuarios]
                    ,[Telefono]
                    ,[Total]
                    ,[Direccion]
                    ,[Latitud]
                    ,[Longitud]
                    ,[Estado])
                VALUES
                    (%s,%s,%s,%s,%s,%s,'En proceso')'''
        cursor.execute(query,Datos)
        conn.commit()
        return {"ok":True}
    except:
         return {"ok":False}


@app.post("/api/Eliminar_producto_carrito/{idProducto}")
def Eliminar_producto_carrito(idProducto:str):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Detalle WHERE idProducto = '"+str(idProducto)+"'")
        conn.commit()
        return {"ok":True}
    except:
         return {"ok":False}



@app.get("/api/Seleccionar_Pedidos")
def Seleccionar_Pedidos():
    try:
        Lista = []
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor(as_dict=True)
        cursor.execute("select p.*, u.Nombre, u.Apellido, u.Correo from Pedidos as p inner join Cliente_Usuario as u on p.IdUsuarios = u.IdUsuarios")
        contenido = cursor.fetchall()
       # Variables.cantidad.clear()
        for i in contenido:
            Lista.append(i)
        if Lista == []:
            return {"ok":False}
        else:
            return {"ok":True, "data":Lista}
    except:
        return {"ok":False}

@app.get("/api/CantidadProductos/{IdUsuario}")
def Cantidad_Productos(IdUsuario:str):
    try:
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        query = "select Cantidad as Cantidad from Detalle where IdUsuarios = '"+str(IdUsuario)+"'"
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        contenido = cursor.fetchall()
        Variables.aux3 = {}
        for i in contenido:
            Variables.aux3 = i
        if Variables.aux3 != {}:
            return Variables.aux3
        else:
           {"ok":False}
    except:
        return "Error"

#endregion







