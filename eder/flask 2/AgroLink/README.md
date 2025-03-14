# AgroLink - Sistema de Gerenciamento Agrícola

AgroLink é uma aplicação web desenvolvida com Flask para auxiliar produtores rurais no gerenciamento de informações sobre solo, safras e usuários.

## Funcionalidades

- **Gerenciamento de Usuários**: Cadastro, edição e exclusão de usuários
- **Análise de Solo**: Registro e análise de informações sobre o solo
- **Gerenciamento de Safras**: Planejamento e acompanhamento de safras
- **API RESTful**: Acesso programático aos dados via API
- **Autenticação Segura**: Sistema de login com JWT e proteção contra ataques
- **Dashboard**: Visualização de dados em gráficos e tabelas

## Requisitos

- Python 3.8+
- PostgreSQL
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/AgroLink.git
   cd AgroLink
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   
   # No Windows
   venv\Scripts\activate
   
   # No Linux/Mac
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` na raiz do projeto com base no exemplo fornecido
   - Ajuste as configurações de banco de dados e chaves de segurança

5. Inicialize o banco de dados:
   ```
   flask db init
   flask db migrate -m "Migração inicial"
   flask db upgrade
   ```

6. Execute a aplicação:
   ```
   python main.py
   ```

## Estrutura do Projeto

- `app/`: Diretório principal da aplicação
  - `__init__.py`: Configuração e inicialização da aplicação
  - `models.py`: Modelos de dados (SQLAlchemy)
  - `routes.py`: Rotas da aplicação web
  - `recursos.py`: Recursos da API RESTful
  - `forms.py`: Formulários da aplicação
  - `conta_solo.py`: Funções para cálculos de análise de solo
  - `views/`: Templates HTML
- `public/`: Arquivos estáticos (CSS, JS, imagens)
- `migrations/`: Migrações do banco de dados
- `main.py`: Ponto de entrada da aplicação
- `blacklist.py`: Gerenciamento de tokens JWT revogados

## API RESTful

A aplicação fornece uma API RESTful para acesso programático aos dados:

- `GET /api/usuarios`: Lista todos os usuários
- `POST /api/usuarios`: Cria um novo usuário
- `GET /api/usuarios/<id>`: Obtém detalhes de um usuário específico
- `PUT /api/usuarios/<id>`: Atualiza um usuário existente
- `DELETE /api/usuarios/<id>`: Remove um usuário
- `POST /api/login`: Autentica um usuário e retorna um token JWT
- `POST /api/logout`: Revoga o token JWT atual

## Análise de Solo

O sistema permite o registro e análise de informações sobre o solo, incluindo:

- Área
- Tipo de solo
- pH do solo
- Matéria orgânica
- Capacidade de Troca Catiônica (CTC)
- Níveis de nitrogênio, fósforo e potássio
- Recomendações de aplicação

## Gerenciamento de Safras

O sistema permite o planejamento e acompanhamento de safras, incluindo:

- Nome da safra
- Cultura
- Área
- Previsão de plantio e colheita
- Produtividade estimada
- Visualização de dados em gráficos

## Segurança

- Senhas armazenadas com hash seguro
- Autenticação via JWT para a API
- Proteção contra SQL Injection via SQLAlchemy
- Variáveis de ambiente para informações sensíveis

## Desenvolvimento

Para contribuir com o desenvolvimento do projeto:

1. Instale as dependências de desenvolvimento:
   ```
   pip install -r requirements-dev.txt
   ```

2. Execute os testes:
   ```
   pytest
   ```

3. Verifique a cobertura de testes:
   ```
   pytest --cov=app
   ```

4. Formate o código:
   ```
   black .
   ```

## Contribuição

Contribuições são bem-vindas! Por favor, siga estas etapas:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
