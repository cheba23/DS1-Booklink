from flask import Flask, render_template, request

# Intancia do servidor do Flask
app = Flask(__name__)

lista_de_cadastro = []

# Rota 1: Pagina inicial
@app.route('/')
def home():
    return render_template("index.html")

# Rota 2: Exibição da tela de cadastro metodo (GET)
@app.route('/cadastro')
def pagina_cadastro():
    return render_template("cadastro.html")

# Rota 3: Status da aplicação
@app.route('/salvar', methods= ["POST"])
def salvar_cadastro():
    livro_digitado = request.form.get("campo_livro")
    tipoLivro_digitada = request.form.get("campo_tipoLivro")
    return render_template("resultado.html", livro=livro_digitado, tipo=tipoLivro_digitada)

if __name__=='__main__':
    app.run(debug=True)