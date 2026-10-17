import bcrypt
import jwt
import os
import conexao_banco
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import PyJWTError


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TEMPO_EXPIRA_TOKEN = 12


def gerarHashSenha(senha: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode(), salt).decode()


def verificarSenha(senha_pura: str, hash_senha: str) -> bool:
    return bcrypt.checkpw(senha_pura.encode(), hash_senha.encode())


def criarTokenAcesso(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=TEMPO_EXPIRA_TOKEN)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def logar(login: str, senha: str):
    request = f"SELECT senha, tipo_usuario, id_usuario FROM usuarios WHERE codigo_unico = '{login}'"
    usuario = conexao_banco.executar_funcao_sql(request)

    if not usuario:
        return {"sucesso": False, "error": "login"}

    if not verificarSenha(senha, usuario[0]["senha"]):
        return {"sucesso": False, "error": "senha"}

    token = criarTokenAcesso({"sub": str(usuario[0]["id_usuario"]), "type": "acess"})

    return {
        "sucesso": True,
        "gerente": usuario[0]["tipo_usuario"] == 1,
        "codUsuario": usuario[0]["id_usuario"],
        "token": token,
    }


security = HTTPBearer()


def checar_autorizacao_usuario(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: str = payload.get("sub")

        if id_usuario is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: identificador ausente no payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "id": id_usuario,
        }

    except PyJWTError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
