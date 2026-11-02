from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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


class credenciaisModel(BaseModel):
    login: str
    senha: str


class usuarioModel(BaseModel):
    nome: str = ""
    login: str = ""
    tipo: str = ""
    senha: str = ""

class recebimentoModel(BaseModel):
    assinatura: str
    foto: str

class entregaModel(BaseModel):
    idVenda: int
    entregador: int | None = None
    descricao: str = ""
    nomeComprador: str = Field(min_length=1)
    contato: str = Field(min_length=1)
    cep: str = Field(min_length=1)
    bairro: str = Field(min_length=1)
    rua: str = Field(min_length=1)
    numero: str = Field(min_length=1)
    complemento: str = ""


@app.post("/api/login")
def login(credenciais: credenciaisModel):
    return autenticacao.logar(credenciais.login, credenciais.senha)


@app.get("/api/entrega")
def listarEntregas(usu: dict = Depends(autenticacao.checar_autorizacao_usuario)):
    return entrega.listarEntregas()


@app.get("/api/entregador")
def listarEntregadores(usu: dict = Depends(autenticacao.checar_autorizacao_usuario)):
    return entrega.listarEntregadores()


@app.post("/api/entrega")
def inserirEntrega(
    dados: entregaModel, usu: dict = Depends(autenticacao.checar_autorizacao_usuario)
):
    entrega.exigirGerente(usu)
    return entrega.inserirEntrega(dados, int(usu["id"]))


@app.put("/api/entrega/{id_entrega}")
def atualizarEntrega(
    id_entrega: int,
    dados: entregaModel,
    usu: dict = Depends(autenticacao.checar_autorizacao_usuario),
):
    entrega.exigirGerente(usu)
    return entrega.atualizarEntrega(id_entrega, dados, int(usu["id"]))


@app.get("/api/usuario")
def listarUsuarios(usu: dict = Depends(autenticacao.checar_autorizacao_usuario)):
    return usuario.listarUsuarios()


@app.post("/api/usuario")
def inserirUsuario(
    dados: usuarioModel, usu: dict = Depends(autenticacao.checar_autorizacao_usuario)
):
    usuario.inserirUsuario(dados)


@app.put("/api/usuario/{id}")
def atualizarUsuario(
    id,
    dados: usuarioModel,
    usu: dict = Depends(autenticacao.checar_autorizacao_usuario),
):
    usuario.atualizarUsuario(id, nome=dados.nome, login=dados.login, tipo=dados.tipo)


@app.put("/api/senha_usuario/{id}")
def atualizarSenha(
    id,
    dados: usuarioModel,
    usu: dict = Depends(autenticacao.checar_autorizacao_usuario),
):
    usuario.atualizarUsuario(id, senha=dados.senha)

@app.get("/api/destino_entrega/{id}")
def listarEntregas(id, usu: dict = Depends(autenticacao.checar_autorizacao_usuario)):
    return entrega.buscarDestinoEntrega(id)

@app.post("/api/finalizar_entrega/{id}")
def listarEntregas(id, dados: recebimentoModel, usu: dict = Depends(autenticacao.checar_autorizacao_usuario)):
    entrega.finalizarEntrega(id, dados.assinatura, dados.foto)

