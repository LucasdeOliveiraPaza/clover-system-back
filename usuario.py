import conexao_banco


def listarUsuarios():
    request = f"SELECT id_usuario, nome, email, tipo_usuario FROM usuarios"
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
                "email": b["email"],
                "tipo": tipo,
            }
        )
    return ret
