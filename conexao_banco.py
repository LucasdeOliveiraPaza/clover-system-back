import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

global conection
global cursor


def executar_funcao_sql(request: str) -> any:
    cursor = None
    conection = None

    load_dotenv()

    try:
        conection = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

        cursor = conection.cursor(cursor_factory=RealDictCursor)

        cursor.execute(request)

        conection.commit()

        return cursor.fetchall()
    except Exception as Error:
        print(Error)
    finally:
        if cursor is not None:
            cursor.close()
        if conection is not None:
            conection.close()


def executar_comando(request: str, params: tuple | None = None, retornar: bool = False):
    """Versão segura de executar_funcao_sql.

    - Aceita parâmetros (%s), evitando SQL injection.
    - Funciona para INSERT/UPDATE/DELETE (sem retorno).
    - retornar=True devolve as linhas (SELECT ou INSERT ... RETURNING).
    - Em caso de erro, desfaz a operação e propaga a exceção.
    """
    load_dotenv()

    conection = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

    try:
        with conection:
            with conection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(request, params)

                if retornar:
                    return cursor.fetchall()
    finally:
        conection.close()
