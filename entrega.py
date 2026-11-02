from fastapi import HTTPException
import conexao_banco

# Códigos da coluna entregas.status. Valores provisórios: confirmar com o Lucas.
STATUS_ENTREGA = {1: "Pendente", 2: "Em rota", 3: "Entregue"}
STATUS_PENDENTE = 1


def listarEntregas():
    request = """
        SELECT e.id_entrega, e.id_venda, e.id_entregador,
            u.nome AS nome_entregador,
            e.cep, e.rua, e.bairro, e.numero, e.complemento,
            e.status, e.descricao,
            e.nome_destinatario, e.contato_destinatario
        FROM entregas e
        LEFT JOIN usuarios u ON u.id_usuario = e.id_entregador
        ORDER BY e.id_entrega DESC
    """
    busca = conexao_banco.executar_funcao_sql(request) or []
    ret = []

    for b in busca:
        ret.append(
            {
                "id_entrega": b["id_entrega"],
                "id_venda": b["id_venda"],
                "status": STATUS_ENTREGA.get(b["status"], str(b["status"])),
                "status_codigo": b["status"],
                "entregador": {
                    "label": b["nome_entregador"] or "",
                    "value": b["id_entregador"],
                },
                "destinatario": b["nome_destinatario"],
                "contato": b["contato_destinatario"],
                "cep": b["cep"],
                "rua": b["rua"],
                "bairro": b["bairro"],
                "numero": b["numero"],
                "complemento": b["complemento"],
                "descricao": b["descricao"],
            }
        )
    return ret

def buscarDestinoEntrega(idEntrega: int):
    request = f"""
        SELECT CONCAT(e.rua, ', ', e.numero, ', ', e.cep, ', ', e.bairro, ', ', 'Caçador - SC') endereco FROM entregas e
        WHERE e.id_entrega = {idEntrega}
    """

    busca = conexao_banco.executar_funcao_sql(request)

    return busca[0]["endereco"];

def finalizarEntrega(idEntrega: int, assinatura: str, foto: str):
    request = f"""
        UPDATE entregas SET
            status = 3,
            assinatura_eletronica = '{assinatura}',
            imagem_comprovante = '{foto}'
        WHERE
            id_entrega = {idEntrega}
    """

    conexao_banco.executar_funcao_sql(request)

def usuarioEhGerente(id_usuario: int) -> bool:
    busca = conexao_banco.executar_comando(
        "SELECT tipo_usuario FROM usuarios WHERE id_usuario = %s",
        (id_usuario,),
        retornar=True,
    )
    return bool(busca) and busca[0]["tipo_usuario"] == 1

def exigirGerente(usu: dict):
    if not usuarioEhGerente(int(usu["id"])):
        raise HTTPException(
            status_code=403, detail="Apenas gerentes podem executar esta ação"
        )


def listarEntregadores():
    busca = conexao_banco.executar_comando(
        "SELECT id_usuario, nome FROM usuarios WHERE tipo_usuario = 2 ORDER BY nome",
        retornar=True,
    )
    return [{"label": b["nome"], "codigo": b["id_usuario"]} for b in busca]


def inserirEntrega(dados, id_usuario: int):
    request = """
        INSERT INTO entregas (
            id_venda, id_entregador, cep, rua, bairro, numero, complemento,
            status, descricao, nome_destinatario, contato_destinatario, criado_por
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_entrega
    """
    params = (
        dados.idVenda,
        dados.entregador,
        dados.cep,
        dados.rua,
        dados.bairro,
        dados.numero,
        dados.complemento,
        STATUS_PENDENTE,
        dados.descricao,
        dados.nomeComprador,
        dados.contato,
        id_usuario,
    )
    busca = conexao_banco.executar_comando(request, params, retornar=True)
    return {"id_entrega": busca[0]["id_entrega"]}


def atualizarEntrega(id_entrega: int, dados, id_usuario: int):
    request = """
        UPDATE entregas SET
            id_venda = %s, id_entregador = %s, cep = %s, rua = %s, bairro = %s,
            numero = %s, complemento = %s, descricao = %s,
            nome_destinatario = %s, contato_destinatario = %s,
            atualizado_por = %s, data_atualizacao = CURRENT_TIMESTAMP
        WHERE id_entrega = %s
        RETURNING id_entrega
    """
    params = (
        dados.idVenda,
        dados.entregador,
        dados.cep,
        dados.rua,
        dados.bairro,
        dados.numero,
        dados.complemento,
        dados.descricao,
        dados.nomeComprador,
        dados.contato,
        id_usuario,
        id_entrega,
    )
    busca = conexao_banco.executar_comando(request, params, retornar=True)

    if not busca:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")

    return {"id_entrega": id_entrega}
