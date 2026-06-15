import os
import sqlite3


def criar_banco_dados():
    
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    dir_banco = os.path.join(dir_atual, '..', 'banco.db')
    # Conecta ou cria a db 
    conexao = sqlite3.connect(dir_banco)
    cursor = conexao.cursor()

    # Ativa as chaves estrangeiras
    cursor.execute("PRAGMA foreign_keys = ON;")
    # Cria as tabelas usando o script SQL definido em queries.py
    cursor.executescript(criar_db)

    # Confirma e encerra a conexão
    conexao.commit()
    conexao.close()


criar_db = """
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------
-- Table `tbl_cliente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `tbl_cliente` (
  -- No SQLite, 'INTEGER PRIMARY KEY AUTOINCREMENT'
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `cpf` VARCHAR(11) NOT NULL UNIQUE -- CPF único para cada cliente; garante integridade.
);

-- -----------------------------------------------------
-- Table `tbl_conta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `tbl_conta` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `numero` INTEGER NOT NULL UNIQUE,                                                     -- numero de conta obrigatório e exclusivo.
  `tipo_conta` VARCHAR(8) NOT NULL CHECK(`tipo_conta` IN ('CORRENTE', 'POUPANCA')),     -- Checar se o tipo de conta é válido; nao aceita outros valores.
  `saldo` DECIMAL(10,2) NOT NULL DEFAULT 0.00,                                          -- não nulo, iniciando sempre com R$0.00 caso nao tenha deposito inicial.
  `limite` DECIMAL(10,2) NULL,
  `fk_tbl_cliente_id` INTEGER NOT NULL,
  
  CONSTRAINT `fk_tbl_cliente_id`
    FOREIGN KEY (`fk_tbl_cliente_id`)
    REFERENCES `tbl_cliente` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- -----------------------------------------------------
-- Table `tbl_transacoes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `tbl_transacoes` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `data_hora` DATETIME NOT NULL,
  `tipo` VARCHAR(10) NOT NULL CHECK(`tipo` IN ('DEPOSITO', 'SAQUE')),                     -- checar se o tipo de transação é válido; nao aceita outros valores.
  `valor` DECIMAL(10,2) NOT NULL,                                                         -- valor da transação não pode ser nulo; garante que cada transação tenha um valor associado.
  `fk_tbl_conta_id` INTEGER NOT NULL,
  
  CONSTRAINT `fk_tbl_conta_id`
    FOREIGN KEY (`fk_tbl_conta_id`)
    REFERENCES `tbl_conta` (`id`)
    ON DELETE RESTRICT                                                                     -- bloqueia a exclusão da conta se houver histórico.
    ON UPDATE CASCADE
);

"""

if __name__ == "__main__":
    criar_banco_dados()
    print("Banco de dados criado com sucesso!")