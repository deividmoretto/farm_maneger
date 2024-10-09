from app import create_app  # Importa a função de criação do app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # Executa o servidor no modo de desenvolvimento