import os
import sqlite3
from database.queries import queries_criar_db

def criar_banco_dados():
    
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    dir_banco = os.path.join(dir_atual, '..', 'banco.db')
    # Conecta ou cria a db 
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()

    # Ativa as chaves estrangeiras
    cursor.execute("PRAGMA foreign_keys = ON;")
    # Cria as tabelas usando o script SQL definido em queries.py
    cursor.executescript(queries_criar_db)

    # Confirma e encerra a conexão
    conexao.commit()
    conexao.close()

if __name__ == "__main__":
    criar_banco_dados()
    print("Banco de dados criado com sucesso!")