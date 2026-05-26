queries_criar_db = """
CREATE TABLE IF NOT EXISTS `tbl_cliente`(
  `id_cliente` INTEGER PRIMARY KEY AUTOINCREMENT,
  `nome_cliente` VARCHAR(100) NOT NULL,
  `cpf_cliente` VARCHAR(45) NOT NULL UNIQUE
  );


CREATE TABLE IF NOT EXISTS `tbl_conta`(
  `id_conta` INTEGER PRIMARY KEY AUTOINCREMENT,
  `numero_conta` INTEGER NOT NULL UNIQUE,
    `tipo_conta` CHAR(1) NOT NULL CHECK(`tipo_conta` IN ('C', 'P')),
  `saldo` DECIMAL(10,2) NULL,
  `limite` DECIMAL(10,2) NULL,
  `tbl_cliente_id_cliente` INTEGER NOT NULL,
  CONSTRAINT `fk_tbl_conta_tbl_cliente`
    FOREIGN KEY (`tbl_cliente_id_cliente`)
    REFERENCES `tbl_cliente` (`id_cliente`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
    );
"""