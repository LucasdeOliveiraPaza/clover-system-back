import conexao_banco

# Códigos da coluna entregas.status. Valores provisórios: confirmar com o Lucas.
STATUS_ENTREGA = {1: "Pendente", 2: "Em rota", 3: "Entregue"}


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