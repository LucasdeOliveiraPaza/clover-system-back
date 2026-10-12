import conexao_banco
import autenticacao


def listarUsuarios():
    request = f"SELECT id_usuario, nome, codigo_unico, tipo_usuario FROM usuarios"
    busca = conexao_banco.executar_funcao_sql(request)
    ret = []

    for b in busca:
        tipo = "G"
        if b["tipo_usuario"] == 2:
            tipo = "E"
        ret.append(
            {
                "id_usuario": b["id_usuario"],
                "nome": b["nome"],
                "login": b["codigo_unico"],
                "tipo": tipo,
            }
        )
    return ret


def inserirUsuario(dados: dict):
    hash_senha = autenticacao.gerarHashSenha(dados.senha)
    tipo = 1
    if dados.tipo == "E":
        tipo = 2

    request = f"""
        INSERT INTO usuarios (nome, codigo_unico, tipo_usuario, senha)
        VALUES ('{dados.nome}', '{dados.login}',{tipo}, '{hash_senha}')
    """

    conexao_banco.executar_funcao_sql(request)


def atualizarUsuario(
    id: int, nome: str = "", login: str = "", tipo: str = "", senha: str = ""
):
    update = ""

    if nome != "":
        update += f"nome = '{nome}',"

    if login != "":
        update += f"codigo_unico = '{login}',"

    if tipo != "":
        tp = 1
        if tipo == "E":
            tp = 2

        update += f"tipo_usuario = {tp},"

    if senha != "":
        hash_senha = autenticacao.gerarHashSenha(senha)
        update += f"senha = '{hash_senha}',"

    if update != "":
        update = update[:-1]

        request = f"""
            UPDATE usuarios SET
            {update}
            WHERE id_usuario = {id}
        """

        conexao_banco.executar_funcao_sql(request)
