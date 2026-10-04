from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import entrega as entrega
import usuario as usuario
import autenticacao as autenticacao

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class credenciais(BaseModel):
    login: str
    senha: str


@app.post("/api/login")
def login(credenciais: credenciais):
    return autenticacao.logar(credenciais.login, credenciais.senha)


@app.get("/api/entregas")
def listarEntregas(usu: dict = Depends(autenticacao.checar_autorizacao_usuario)):
    return entrega.listarEntregas()


@app.get("/api/usuarios")
def listarUsuarios(usu: dict = Depends(autenticacao.checar_autorizacao_usuario)):
    return usuario.listarUsuarios()
