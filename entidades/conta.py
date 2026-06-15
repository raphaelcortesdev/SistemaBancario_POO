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

        # Flag para indicar se o histórico já foi carregado do banco de dados, evitando múltiplos carregamentos desnecessários
        self._historico_carregado = False

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
             self._saldo += valor #incrementa o saldo com o valor depositado
            #adiciona a operação no histórico como uma tupla, com data e descrição
             self._historico.append((datetime.now(), f'Depósito de R$ {valor:.2f}'))
             self.atualizar_saldo_db()                     # Sincroniza o saldo atual
             self._salvar_transacao_db('DEPOSITO', valor)  # Grava o histórico financeiro
         
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

    # se o histórico ainda nao foi carregado (self._historico_carregado == False), ele puxa o passado do banco de dados e junta com o presente da RAM, para exibir o extrato completo. Se já tiver sido carregado, ele exibe direto da RAM, sem puxar do banco novamente.
        if not self._historico_carregado:
            dir_atual = os.path.dirname(os.path.abspath(__file__))
            dir_banco = os.path.join(dir_atual, '..', 'banco.db')

            conexao = sqlite3.connect(dir_banco)
            cursor = conexao.cursor()

            cursor.execute("SELECT id FROM tbl_conta WHERE numero = ?", (self._numero,))
            linha_conta = cursor.fetchone()

            if linha_conta:
                id_interno_conta = linha_conta[0]

                # Puxa o historico do banco de dados, ordena por data e hora, e prepara uma lista de tuplas (data_objeto, descricao) para juntar com o histórico presente da RAM
                cursor.execute("""
                    SELECT data_hora, tipo, valor 
                    FROM tbl_transacoes 
                    WHERE fk_tbl_conta_id = ?
                    ORDER BY data_hora ASC
                """, (id_interno_conta,))
                
                linhas_banco = cursor.fetchall()

                self._historico = []
                
                for data_texto, tipo, valor in linhas_banco:
                    data_objeto = datetime.strptime(data_texto, '%Y-%m-%d %H:%M:%S')
                    if tipo == 'DEPOSITO':
                        descricao = f'Depósito de R$ {valor:.2f}'
                    else:
                        descricao = f'Saque de R$ {valor:.2f}'
                    
                    self._historico.append((data_objeto, descricao))

            conexao.close()
            
            # Marca como carregado para que nas próximas vezes ele use apenas a memória RAM direta
            self._historico_carregado = True

        # --- EXIBIÇÃO DA INFORMAÇÃO ---
        if not self._historico:
            print("Nenhuma transação registrada para esta conta.")
            return

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
            WHERE numero = ?
        """, (self._saldo, self._numero))
        
        conexao.commit()
        conexao.close()
    
    def _salvar_transacao_db(self, tipo: str, valor: float):
        '''Registra fisicamente a transação na tabela tbl_transacoes'''
        
        # localiza o banco.db subindo um nível
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()

        # captura o momento exato do sistema no formato YYYY-MM-DD HH:MM:SS
        data_hora_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # descobre o id da conta atraves do número da conta, para usar como chave estrangeira na tabela de transações
        cursor.execute("SELECT id FROM tbl_conta WHERE numero = ?", (self._numero,))
        linha = cursor.fetchone()
        
        if linha:
            id_interno_conta = linha[0]

            # executa o insert em tbl_transacoes
            cursor.execute("""
                INSERT INTO tbl_transacoes (data_hora, tipo, valor, fk_tbl_conta_id)
                VALUES (?, ?, ?, ?)
            """, (data_hora_atual, tipo, valor, id_interno_conta))
            
            # Confirma o registro
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

        self.atualizar_saldo_db() # Sincroniza o saldo atual
        self._salvar_transacao_db('SAQUE', valor)  # Grava o histórico financeiro

    # Salva a conta corrente em banco.db
    def salvar_db(self):
        # Localiza o banco.db
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()

        # Aplica o INSERT INTO e salva a conta corrente na db; associa a conta ao cliente atraves de self._cliente.id
        cursor.execute("""
            INSERT INTO tbl_conta (numero, tipo_conta, saldo, limite, fk_tbl_cliente_id)
            VALUES (?, ?, ?, ?, ?)
        """, (self._numero, 'CORRENTE', self._saldo, self.limite, self._cliente.id))

        conexao.commit()
        conexao.close()
    
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
            return

        #verifica se há saldo suficiente
        if valor > self._saldo:
            raise SaldoInsuficienteError(self._saldo, valor)

        #deduz o valor sacado do saldo
        self._saldo -= valor

        #Registra a transação no histórico
        self._historico.append((datetime.now(), f'Saque de R${valor:.2f}'))
        print(f'Saque de {valor:.2f} realizado com sucesso.')

        self.atualizar_saldo_db()                  # Sincroniza o saldo atual no banco
        self._salvar_transacao_db('SAQUE', valor)  # Grava a transação física no banco

    # Salva a conta poupança em banco.db
    def salvar_db(self):
        # Localiza o banco.db na raiz
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_banco = os.path.join(dir_atual, '..', 'banco.db')

        conexao = sqlite3.connect(dir_banco)
        cursor = conexao.cursor()

        # Aplica INSERT INTO para salvar a conta poupança na db; associa a conta ao cliente atraves de self._cliente.id. O tipo_conta é 'POUPANCA' para poupança, e o limite é None.
        cursor.execute("""
            INSERT INTO tbl_conta (numero, tipo_conta, saldo, limite, fk_tbl_cliente_id)
            VALUES (?, ?, ?, ?, ?)
        """, (self._numero, 'POUPANCA', self._saldo, None, self._cliente.id))

        conexao.commit()
        conexao.close()       