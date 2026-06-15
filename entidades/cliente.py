'''
Submodulo da entidade Cliente
'''
import os
import sqlite3

class Cliente:

    #Construtor: inicializa os atributos da classe
    def __init__(self, nome: str, cpf: str):
        
        #Atributo que armazena nome do Cliente
        self.nome = nome

        #Atributo que armazena cpf do Cliente
        self.cpf = cpf

        #Lista vazia que armazena contas associadas ao cliente
        self.contas = []

        # Atributo id para identificar exclusivamente o cliente em banco.db, inicia como None e é autoincrementado ao ser salvo.
        self.id = None

    #Método que adiciona a conta criada à lista de contas do cliente
    def adicionar_conta(self, conta):

        #Adicona o objeto conta na lista de contas
        self.contas.append(conta)

    # Método que salva o cliente em banco.db
    def salvar_db(self):
        
        # Identifica o caminho do banco.db de forma dinâmica, independente do sistema operacional ou estrutura de pastas
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_db = os.path.join(dir_atual, '..', 'banco.db')

        # Abre a conexão com o banco
        conexao = sqlite3.connect(dir_db)
        cursor = conexao.cursor()

        # se o id for None, é um cliente novo e executa o insert
        if self.id is None:
            cursor.execute(
                "INSERT INTO tbl_cliente (nome, cpf) VALUES (?, ?)", 
                (self.nome, self.cpf)
            )
            conexao.commit()
            
            self.id = cursor.lastrowid
            print(f"Sucesso: {self.nome} foi salvo no banco com o ID {self.id}!")
            
        # Se o id já existir, apenas atualiza o registro (UPDATE)
        else:
            cursor.execute(
                "UPDATE tbl_cliente SET nome = ?, cpf = ? WHERE id = ?",
                (self.nome, self.cpf, self.id)
            )
            conexao.commit()
            print(f"Sucesso: Dados do cliente {self.nome} (ID {self.id}) foram atualizados no banco!")

        conexao.close()

    #Método especial que representa o objeto em string
    def __str__(self):
        
        #Retorna uma str format com nome e CPF do Cliente
        return f'Cliente: {self.nome} (CPF: {self.cpf})'