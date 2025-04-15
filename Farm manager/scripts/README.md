# Scripts Utilitários para Gerenciamento de Usuários

Esta pasta contém scripts utilitários para gerenciar os usuários e o banco de dados da aplicação.

## Scripts Disponíveis

### 1. `update_database.py`

Script para atualizar a estrutura do banco de dados, especificamente para aumentar o tamanho do campo `password_hash` para 255 caracteres.

**Uso:**
```bash
python scripts/update_database.py
```

### 2. `create_admin.py`

Script para criar ou atualizar um usuário administrador.

**Uso básico (cria usuário 'admin' com senha 'admin'):**
```bash
python scripts/create_admin.py
```

**Uso personalizado:**
```bash
python scripts/create_admin.py --username seu_admin --email admin@exemplo.com --password sua_senha
```

### 3. `create_user.py`

Script para criar um usuário normal (sem privilégios de administrador).

**Uso:**
```bash
python scripts/create_user.py --username novo_usuario --email usuario@exemplo.com --password senha123
```

### 4. `soil_calculator.py`

Script para análise de solo e geração de recomendações de correção/adubação com base nos resultados laboratoriais.

**Uso básico:**
```bash
python scripts/soil_calculator.py --ph 5.2 --p 8.5 --k 0.10 --ca 1.8 --mg 0.6
```

**Opções:**
- `--ph`: Valor do pH do solo (obrigatório)
- `--p` ou `--phosphorus`: Teor de fósforo em mg/dm³ (obrigatório)
- `--k` ou `--potassium`: Teor de potássio em cmolc/dm³ (obrigatório)
- `--ca` ou `--calcium`: Teor de cálcio em cmolc/dm³ (obrigatório)
- `--mg` ou `--magnesium`: Teor de magnésio em cmolc/dm³ (obrigatório)
- `--save`: Salvar a análise no banco de dados (opcional)
- `--area-id`: ID da área, se aplicável (opcional)
- `--user-id`: ID do usuário, se aplicável (opcional)
- `--output`: Formato de saída, 'text' (padrão) ou 'json' (opcional)

**Exemplo com salvamento no banco de dados:**
```bash
python scripts/soil_calculator.py --ph 5.2 --p 8.5 --k 0.10 --ca 1.8 --mg 0.6 --save --user-id 1
```

**Exemplo com saída em JSON:**
```bash
python scripts/soil_calculator.py --ph 5.2 --p 8.5 --k 0.10 --ca 1.8 --mg 0.6 --output json
```

### 5. `soil_calculator_flask.py`

Versão web da calculadora de solo com interface gráfica que utiliza o template HTML existente.

**Uso:**
```bash
python scripts/soil_calculator_flask.py
```

Depois de executar o comando, acesse a calculadora no navegador:
```
http://127.0.0.1:5002/calculadora
```

**Recursos:**
- Interface gráfica completa com formulário para entrada de dados
- Cálculos automáticos de CTC, saturação por bases e outros parâmetros
- Interpretação dos resultados com valores de referência
- Recomendação de calagem com base nos níveis desejados
- Suporte para diferentes tipos de solo e culturas

## Observações

- Todos os scripts utilizam as mesmas configurações de banco de dados definidas no arquivo `.env` na raiz do projeto.
- Os scripts criam as tabelas necessárias se elas não existirem.
- É recomendável executar estes scripts em ambiente de desenvolvimento ou manutenção, nunca em produção sem testes prévios. 