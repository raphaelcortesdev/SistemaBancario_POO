
![Python](https://img.shields.io/badge/Python-3.12+-blue) ![Status](https://img.shields.io/badge/status-em%20desenvolvimento-green) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/raphael-cortes-b0b544305/) [![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=flat&logo=instagram&logoColor=white)](https://www.instagram.com/raphaelcorte_s/) [![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=flat&logo=whatsapp&logoColor=white)](https://wa.me/5561998294492)
# Sistema Bancário em Python

Sistema bancário digital, com as funcionalidades de adicionar cliente, criar uma conta, vincular conta ao cliente, depositar, sacar e ver extrato da conta

## 📌 Sobre o Projeto
Este projeto foi desenvolvido para aplicar e compreender na prática os conceitos de **Programação Orientada a Objetos (POO)**, utilizando as melhores práticas do paradigma. O sistema bancário cadastra clientes, cria novas contas e vincula contas a clientes. Uma vez que uma conta é vinculada a um cliente, é possível realizar depósitos, saques e conferir o extrato bancário.

  

## 🗂️ Estrutura do Projeto

  

```bash

.
│   banco.db
│   main.py
│   readme.md
│
├───database
│       criar_db.py
│       queries.py
│       __init__.py
│
├───entidades
│       cliente.py
│       conta.py
│       __init__.py
│
├───modelagem_db
│       modelo_logico_sistemabancario.mwb
│       modelo_logico_sistemabancario.mwb.bak
│
├───operacoes
│      banco.py
│      __init__.py
│   
│
└───utilitarios
        exceptions.py
        __init__.py
    


```

  

## 🧱 Organização Modular

  

O projeto foi estruturado de forma modular, separando responsabilidades em diferentes pacotes:

  

### 📦 entidades

Responsável pela definição das entidades principais do sistema:

-  `Cliente`: Classe que cria o objeto `cliente`.

-  `Conta`: Contém a Classe abstrata `Conta`, que serve de molde para as classes `ContaCorrente` e `ContaPoupanca`.

  

### 📦 operacoes

Contém a classe `Banco`, responsável por:

- Gerenciar clientes e contas

- Vincular contas a clientes

- Controlar regras de negócio

  

### 📦 utilitarios

Contém utilitários auxiliares:

- Tratamento de exceções personalizadas
  

>A modularização garante maior organização, legibilidade e escalabilidade do sistema, indo de acordo com as melhores práticas de programação.

  

## 🧱 Funcionamento Interno

  

O sistema segue os princípios da Programação Orientada a Objetos (POO).

  

O fluxo principal funciona da seguinte maneira:

  

1. Um objeto `Cliente` é criado e armazenado pelo sistema.

2. Um objeto `ContaCorrente` ou `ContaPoupanca` é criado e armazenado pelo sistema.

3. A classe `Banco` é responsável por gerenciar os objetos criados.

4. O Banco vincula a conta ao cliente.

5. Após o vínculo, operações como depósito, saque e consulta de extrato podem ser realizadas.

  

A classe `Banco` atua como camada central de controle, garantindo que as regras de negócio sejam respeitadas.

  

### 🔎 Conceitos Aplicados

  

#### Encapsulamento

- controlar o acesso a atributos do objeto que não devem ser acessados diretamente, bem como agrupar tipos de dados e comportamentos na mesma classe.

  

#### Abstração

- Foco nas características relevantes para o contexto do projeto, abstraindo toda a complexidade que uma agência bancária tem na realidade.

  

#### Herança

- As classes `ContaCorrente` e `ContaPoupanca` são classes "filhas", que herdam metodos e atributos da classe abstrata "pai" `Conta`.

  

#### Polimorfismo

- No submodulo `conta.py`, o polimorfismo se faz presente no metodo sacar, herdado de `Conta` e sobrescrito por `ContaCorrente` e `ContaPoupanca`. Ambas apresentam comportamento diferente para o mesmo método, dada as características de cada conta.

  

## 🛠️ Tecnologias utilizadas.
-  **Python 3.12+** - Linguagem principal

## ▶️ Como Executar

Clone o repositório:

```bash
git clone https://github.com/raphaelcortesdev/SistemaBancario_POO.git
```
No terminal, navegue até o repositório clonado e execute o sistema:

```bash
python main.py
```
## 📚 Aprendizados

Durante o desenvolvimento deste projeto, foram consolidados os seguintes conceitos:

- Estruturação de projetos Python em módulos
- Aplicação prática de POO
- Herança e polimorfismo
- Tratamento de exceções personalizadas

## 📝 TODO List

- [x] Persistência de dados em banco de dados: cadastro de clientes, criação de conta e vinculação de conta ao cliente
- [ ] Persistência de dados em banco de dados: extrato
- [ ] API REST
- [ ] Sistema de autenticação
- [ ] Implementação de testes automatizados