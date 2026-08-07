from flask import Flask

# Intancia do servidor do Flask
app = Flask(__name__)

# Rota 1: Pagina inicial
@app.route('/')
def home():
    return "<h1>Servidor Flask rodando!</h1>""<h1>Bem-Vindo ao meu Servidor Flask!</h1>"

# Rota 2: Sobre a aplicação
@app.route('/sobre')
def sobre():
    return "<h1>Sobre a aplicação</h1>""<p>Esta  é uma aplicação Flask.</p>"

# Rota 3: Status da aplicação
@app.route('/status')
def status():
    return "<h1>status da aplicação</h1>""<p>o servidor flask esta rodando corretamente.</p>"

if __name__=='__main__':
    app.run(debug=True)