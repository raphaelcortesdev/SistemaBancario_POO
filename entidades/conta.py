'''
Submodulo que define as entidades de Conta (abstrata, corrente, poupança)
'''
import os
import sqlite3

#Importa a classe base abstrata e o decorador para metodos abstratos
from abc import ABC, abstractmethod

#importa o metodo datetime para auxiliar nos registros de horario das transações bancárias
from datetime import datetime

#Importa a exceção personalizada para saldo insuficiente
from utilitarios.exceptions import SaldoInsuficienteError

#Classe Conta: abstrata, serve de base para os outros tipos de conta (Classe PAI)
class Conta(ABC):
    '''
    classe base abstrata (PAI).
    Herança e encapsulamento
    '''

    #Atributo de classe que calcula quantas contas foram criadas (atributo protegido)
    _total_contas = 0

    #Método construtor da classe
    def __init__(self, numero: int, cliente):
        
        #Número da conta: atributo protegido (underline)
        self._numero = numero

        #Saldo, inicializado em 0.0: atriubuto protegido
        self._saldo = 0.0

        #Referência ao cliente dono da conta: atributo protegido
        self._cliente = cliente

        #Lista para armazenar histórico de transações: atributo protegido
        self._historico = []

        #Incrementa o total de contas criadas
        Conta._total_contas += 1 

    #propriedade para acessar o saldo de forma controlada
    @property
    def saldo(self):

        #Getter para o saldo, permitindo acesso controlado, já que o atributo é protegido
        return self._saldo
    
    #Metodo para acessar o total de contas
    @classmethod
    def get_total_contas(cls):

        #Método de classe para obter o número total de contas criadas
        return cls._total_contas
    
    #Método para realizar depósitos
    def deposito(self, valor: float):
         
         #verifica se o valor é válido (positivo)
         if valor > 0:
             
             #incrementa o saldo com o valor depositado
             self._saldo += valor
            
            #adiciona a operação no histórico como uma tupla, com data e descrição
             self._historico.append((datetime.now(), f'Depósito de R$ {valor:.2f}'))
             
         else:
             print(f'Valor de depósito inválido.')

    #Método abstrato que deve ser implementado pelas subclasses (filhos)
    @abstractmethod
    def sacar(self, valor: float):
    
        pass
    
    #metodo para exibir o extrato da conta
    def extrato(self):

        #Exibe o extrato
        print(f'\n--- Extrato da conta nº {self._numero} ---')
        print(f'Cliente: {self._cliente.nome}')
        print(f'Saldo Atual: {self._saldo:.2f}')
        print('\n\nHISTÓRICO DE TRANSAÇÕES:')

        #Verifica se tem histórico de transações
        if not self._historico:
            print("Nenhuma transação registrada.")

        #percorre a lista de histórico (lista de tuplas), e printa a data e a transação
        for data, transacao in self._historico:
            print(f'- {data.strftime("%d/%m/%Y %H:%M:%S")}: {transacao}')
            print('---------------------------------------\n')

    # Método para restaurar o saldo original ao criar a conta buscada em banco.db
    def restaurar_saldo_banco(self, saldo_original: float):
        self._saldo = saldo_original

    # Atualiza o saldo atual do objeto na tabela tbl_conta, após operações de saque ou depósito
    def atualizar_saldo_db(self):
        
        # Localiza o banco.db
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()
        
        # Executa a atualização do saldo na tabela tbl_conta, usando o número da conta para localizar o registro correto
        cursor.execute("""
            UPDATE tbl_conta 
            SET saldo = ? 
            WHERE numero_conta = ?
        """, (self._saldo, self._numero))
        
        conexao.commit()
        conexao.close()

#Define a subclasse (filha) da Classe Conta: ContaCorrente
class ContaCorrente(Conta):

    '''
    subclasse que representa a conta corrente
    um tipo da classe conta
    sobrescreve o metodo sacar da classe base Conta -> POLIMORFISMO
    '''

    #Metodo construtor da classe, com limite do cheque especial defalt de R$500
    def __init__(self, numero: int, cliente, limite: float = 500.00):
        
        #Chama o construtor da classe base
        super().__init__(numero, cliente)

        #Define o limite do cheque especial
        self.limite = limite

    #Metodo para sacar, com cheque especial
    def sacar(self, valor: float):
        
        '''
        permite sacar utilizando o saldo da conta + o limite do cheque especial
        '''

        #Verifica se o valor é válido
        if valor <= 0:
            print("Valor de saque inválido")
            return
        
        #Calcula o saldo disponivel (saldo + limite)
        saldo_disponivel = self._saldo + self.limite

        #caso o valor do saque ultrapasse o saldo disponivel
        if valor > saldo_disponivel:
            raise SaldoInsuficienteError(saldo_disponivel, valor, "Saldo e limite insuficientes")
        
        #Deduz o valor do saque do saldo disponivel
        self._saldo -= valor

        #Registra a transação no histórico
        self._historico.append((datetime.now(), f'Saque de R${valor:.2f}'))
        print(f'Saque de {valor:.2f} realizado com sucesso.')


    # Salva a conta corrente em banco.db
    def salvar_db(self):
        # Localiza o banco.db
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()

        # Aplica o INSERT INTO e salva a conta corrente na db; associa a conta ao cliente atraves de self._cliente.id
        cursor.execute("""
            INSERT INTO tbl_conta (numero_conta, tipo_conta, saldo, limite, tbl_cliente_id_cliente)
            VALUES (?, ?, ?, ?, ?)
        """, (self._numero, 'C', self._saldo, self.limite, self._cliente.id))

        conexao.commit()
        conexao.close()
        print(f"Conta Corrente nº {self._numero} salva no banco de dados!")
    


#Define a subclasse ContaPoupanca, que herda a classe Conta
class ContaPoupanca(Conta):

    '''
    subclasse que representa conta poupança -> herança
    '''

    #Método construtor da classe, herda da classe Conta:
    def __init__(self, numero: int, cliente):
        super().__init__(numero, cliente)

    #Implementa o metodo sacar
    def sacar(self, valor: float):

        #verifica se o valor é válido
        if valor <= 0:
            print('Valor de saque inválido.')

        #verifica se há saldo suficiente
        if valor > self._saldo:
            raise SaldoInsuficienteError(self._saldo, valor)

        #deduz o valor sacado do saldo
        self._saldo -= valor

        #Registra a transação no histórico
        self._historico.append((datetime.now(), f'Saque de R${valor:.2f}'))
        print(f'Saque de {valor:.2f} realizado com sucesso.')

    # Salva a conta poupança em banco.db
    def salvar_db(self):
        # Localiza o banco.db na raiz
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()

        # Aplica INSERT INTO para salvar a conta poupança na db; associa a conta ao cliente atraves de self._cliente.id. O tipo_conta é 'P' para poupança, e o limite é None.
        cursor.execute("""
            INSERT INTO tbl_conta (numero_conta, tipo_conta, saldo, limite, tbl_cliente_id_cliente)
            VALUES (?, ?, ?, ?, ?)
        """, (self._numero, 'P', self._saldo, None, self._cliente.id))

        conexao.commit()
        conexao.close()
        print(f"Conta Poupança nº {self._numero} salva no banco de dados!")        