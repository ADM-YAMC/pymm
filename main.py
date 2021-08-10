import pymssql
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    try:
        lista = []
        query = "Select Nombre from [dbo].[Prueba]"
        conn = pymssql.connect('proyecto-final.database.windows.net', 'ADM-YAMC', 'Ya95509550', 'DBAPI')
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        contenido = cursor.fetchall()
        for row in contenido:
            return row
        conn.close()
    except:
        return "Ocurio un error... "