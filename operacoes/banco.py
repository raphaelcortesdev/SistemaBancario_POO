'''
Submodulo que implementa a classe Banco, que gerencia Cliente, Conta, ContaCorrente e ContaPoupanca

'''
import os
import sqlite3
from entidades.cliente import Cliente
from entidades.conta import Conta, ContaCorrente, ContaPoupanca
from utilitarios.exceptions import ContaInexistenteError
from database.criar_db import criar_banco_dados


class Banco:

    '''
    Classe que gerencia Cliente, Conta, ContaCorrente e ContaPoupanca
    composição -> "tem" clientes e contas
    '''

    #Construtorda classe banco
    def __init__(self, nome: str):
        
        #Nome do Banco
        self.nome = nome

        #Dict clientes (key: CPF, value: objeto Cliente)
        self._clientes = {}

        #Dict contas (key: número da conta, value: objeto Conta)
        self._contas = {}

        # Cria o banco de dados e as tabelas, caso ainda não existam, ao iniciar o sistema
        criar_banco_dados()

    #Metodo para adicionar um novo cliente ao banco
    def adicionar_cliente(self, nome: str, cpf: str) -> Cliente:

        '''Cria e adiciona um novo cliente ao banco'''

        #Verifica se já existe um cliente com o mesmo CPF
        cliente_existente = self.buscar_cliente(cpf)
        
        if cliente_existente:
            print('Erro: Cliente com este CPF já cadastrado.')
            return cliente_existente

        # Se não há cliente com o cpf, cria e salva
        novo_cliente = Cliente(nome, cpf)
        # Salva em memoria
        self._clientes[cpf] = novo_cliente
        # Salva em banco.db
        novo_cliente.salvar_db()

        print(f"Cliente {nome} adicionado com sucesso!")
        
        return novo_cliente
    
    # Busca um CLiente pelo CPF.
    def buscar_cliente(self, cpf: str) -> Cliente:
        
        # Verifica se o Cliente já está na memória
        if cpf in self._clientes:
            return self._clientes[cpf]

        # Se não, busca no arquivo banco.db
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()
        
        # Faz a busca do cliente pelo CPF, utilizando o SELECT. A tupla resultante é salva na variável linha.
        cursor.execute("SELECT id_cliente, nome_cliente, cpf_cliente FROM tbl_cliente WHERE cpf_cliente = ?", (cpf,))
        linha = cursor.fetchone()
        conexao.close()

        # Se encontrou o cliente, reconstrói o objeto Cliente e o retorna. Se não, retorna None.
        if linha:
            id_cli, nome_cli, cpf_cli = linha
            # Reconstrói o objeto Cliente (Reidratação)
            cliente = Cliente(nome_cli, cpf_cli)
            cliente.id = id_cli
            
            # Alimenta o dicionário interno para guardar em memória
            self._clientes[cpf] = cliente
            return cliente
            
        return None
    
    
    # Metodo para criar uma conta para um cliente
    def criar_conta(self, cliente: Cliente, tipo: str) -> Conta:

        '''Cria uma nova conta para um cliente existente'''



        # Identifica o caminho para banco.db
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        # Realiza a conexão
        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()

        # Padroniza a entrada do tipo de conta e verifica se é valida
        tipo_conta = tipo.upper()
        if tipo_conta not in ['C', 'P']:
            print('Tipo de conta inválido. Digite C para Conta Corrente ou P para Conta Poupança: ')
            return None

        # Verifica se o Cliente ja possui uma conta do mesmo tipo associada a ele em banco.db
        tipo_db = tipo_conta
        cursor.execute("""
            SELECT COUNT(*) 
            FROM tbl_conta 
            WHERE tbl_cliente_id_cliente = ? AND tipo_conta = ?
        """, (cliente.id, tipo_db))
        
        if cursor.fetchone()[0] > 0:
            conexao.close()  # Fecha a conexão antes de sair
            tipo_texto = "Corrente" if tipo_db == 'C' else "Poupança"
            print(f"Erro: O cliente {cliente.nome} já possui uma Conta {tipo_texto} cadastrada.")
            return None

        
        # SELECT MAX() retorna o maior número de conta já existente no banco, para garantir que o próximo número seja único e sequencial. 
        # O resultado é salvo na variável maior_numero.
        cursor.execute("SELECT MAX(numero_conta) FROM tbl_conta")
        maior_numero = cursor.fetchone()[0]
        
        # Se for a primeira conta, inicia com 1001
        if maior_numero is None:
            numero_conta = 1001
        # Caso contrário, incrementa o maior número encontrado
        else:
            numero_conta = maior_numero + 1

        # Encerra a conexão
        conexao.close()
        
        #Cria conta corrente se o tipo informado for "corrente"
        if tipo_conta == 'C':
            nova_conta = ContaCorrente(numero_conta, cliente)
        
        #Cria conta poupança se o tipo informado for "poupanca"
        elif tipo_conta == 'P':
            nova_conta = ContaPoupanca(numero_conta, cliente)
        
        
        #Adiciona a conta ao dict _contas (key: nº da conta, value: obj Conta)
        self._contas[numero_conta] = nova_conta

        #associa a conta ao cliente
        cliente.adicionar_conta(nova_conta)
        # Salva a conta no banco.db
        nova_conta.salvar_db()

        print(f'Conta {tipo} nº{numero_conta} criada para o cliente {cliente.nome}')

        return nova_conta
    
    #Metodo para buscar uma conta pelo número
    def buscar_conta(self, numero_conta: int):
        
        # Verifica se a conta já está na memória
        if numero_conta in self._contas:
            return self._contas[numero_conta]

        # Se não estiver, realiza a conexão com a database
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()

        # Fazemos um SELECT buscando o número da conta
        cursor.execute(""" 
            SELECT numero_conta, tipo_conta, saldo, limite, tbl_cliente_id_cliente 
            FROM tbl_conta
            WHERE numero_conta = ?
        """, (numero_conta,))
        
        # Salva a linha encontrada na variavel linha. fetchone() retorna uma tupla com os valores da linha, ou None se não encontrar nada.
        linha = cursor.fetchone() 

        # Se não achou a conta, lança a exceção personalizada.
        if not linha:
            conexao.close()
            raise ContaInexistenteError(numero_conta)

        # Se achou, desempacota os valores da tupla linha em variáveis
        num, tipo, saldo, limite, id_cliente = linha

        # Após encontrar a conta, é preciso achar o cliente dono dessa conta atraves do id desempacotado, 
        # para remontar o objeto cliente e depois a conta com todos os dados e métodos ativos.
        cursor.execute("SELECT nome_cliente, cpf_cliente FROM tbl_cliente WHERE id_cliente = ?", (id_cliente,))
        nome_cli, cpf_cli = cursor.fetchone() # Salva nome e cpf do cliente.

        # Criação do objeto Cliente em memória, utilizando os dados do banco.
        cliente_recuperado = Cliente(nome_cli, cpf_cli)
        # Atribui o id do cliente encontrado no banco ao objeto Cliente sendo criado.
        cliente_recuperado.id = id_cliente

        # Cria a conta em memória novamente, utilizando os dados do banco, a depender do de conta
        if tipo == 'C':
            # Cria o objeto ContaCorrente com os dados do banco
            conta_recuperada = ContaCorrente(numero=num, cliente=cliente_recuperado, limite=limite)
        elif tipo == 'P':
            # Cria o objeto ContaPoupanca com os dados do banco
            conta_recuperada = ContaPoupanca(numero=num, cliente=cliente_recuperado)

        # Restaura o saldo original da conta recuparada em banco.db, respeitando o encapsulamento
        conta_recuperada.restaurar_saldo_banco(saldo)

        conexao.close()

        # Guarda conta_recuperada em dict na memoria para futuras buscas
        self._contas[numero_conta] = conta_recuperada

        return conta_recuperada
