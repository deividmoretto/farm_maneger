FROM python:3.9-slim

WORKDIR /app

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta que o Flask usará
EXPOSE 5000

# Define as variáveis de ambiente
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Executa as migrações e inicia o servidor
CMD flask db upgrade && gunicorn --bind 0.0.0.0:5000 main:app 