# Sistema de Análise de Solo

Este é um sistema web desenvolvido com Flask para gerenciamento de análises de solo.

## Requisitos

- Python 3.8 ou superior
- PostgreSQL
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd <diretorio-do-projeto>
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o banco de dados PostgreSQL:
- Crie um banco de dados chamado `farmdb`
- Ajuste as configurações de conexão no arquivo `.env`

5. Inicialize o banco de dados:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Executando o projeto

1. Ative o ambiente virtual (se ainda não estiver ativo)
2. Execute o servidor Flask:
```bash
python main.py
```

3. Acesse o sistema em `http://localhost:5000`

## Funcionalidades

- Cadastro e login de usuários
- Gerenciamento de áreas de análise
- Registro de análises de solo
- Calculadora de nutrientes
- Visualização de preços
- Sistema responsivo e amigável

## Estrutura do Projeto

```
projeto/
├── app/
│   ├── models/
│   │   ├── user.py
│   │   ├── area.py
│   │   └── analysis.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── areas.py
│   │   └── analises.py
│   ├── static/
│   │   ├── css/
│   │   └── images/
│   ├── templates/
│   │   ├── areas/
│   │   ├── errors/
│   │   └── *.html
│   └── __init__.py
├── main.py
├── requirements.txt
├── README.md
└── .env 