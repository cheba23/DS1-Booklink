from flask import Flask, render_template, request, redirect # Corrigido: 'flask' em minúsculo e adicionado 'redirect'

# instancia do servidor do flask
app = Flask(__name__)

# lista global para armazenar os dicionarios dos cadastro
lista_de_livros = []

# rota 1: pagina inicial (home) calcular metricas, aplicar buscar
# disparada quando o usuario digita o endereço principal
@app.route('/')
def home():
    # 1 capturar termo digitado no campo busca GET
    busca = request.args.get("busca", "").strip().lower()

    # 2 filtra a lista se houver busca digitada
    if busca:
        # Corrigido: item["nome"] em vez de item("nome")
        registro_filtrados = [item for item in lista_de_livros if busca in item["livro"].lower()]
    else:
        registro_filtrados = lista_de_livros

    # 3 calculo de metrica / indicadores (cards home) - AGORA DENTRO DA FUNÇÃO
    total_livro = len(lista_de_livros)
    total_faturamento = sum(item["valor"] for item in lista_de_livros)
    total_disponiveis = sum(1 for item in lista_de_livros if item["status"] == "Disponivel")
    total_esgotados = sum(1 for item in lista_de_livros if item["status"] == "Esgotado")

    # 4 enviar os indicadores para a pagina index.html - AGORA DENTRO DA FUNÇÃO
    return render_template(
        "index.html",
        cadastro=registro_filtrados,
        total=total_livro,
        faturamento=total_faturamento,
        disponiveis=total_disponiveis,
        esgotados = total_esgotados,
        busca=busca
    )

# rota 2: exibição da tela de cadastro metodo (GET)
@app.route('/cadastro')
def pagina_cadastro():
    return render_template("cadastro.html")

# rota 3: processamento dos dados metodo (POST)
@app.route('/salvar', methods=["POST"])
def salvar_cadastro():
    livro_digitado = request.form.get("campo_livro", "").strip()
    genero_digitada = request.form.get("campo_genero", "").strip()
    valor_str = request.form.get("campo_valor", "0").strip()

    try:
        valor = float(valor_str)
        if valor <= 0:
            raise ValueError()
    except ValueError:
        return "<h3>Erro 400: O valor deve ser um valor maior que zero!</h3><br><a href='/cadastro'>voltar ao formulario</a>", 400
    
    # validação 2: verificar se os campos obrigatorios vieram vazios
    # Corrigido: usando as variáveis corretas livro_digitado e genero_digitada
    
    if not livro_digitado or not genero_digitada:
        return "<h3>Erro 400: Preencha todos os campos obrigatorios do formulario</h3><br><a href='/cadastro'>voltar ao formulario</a>", 400
    
    # Criação da estrutura de dados
    novo_registro = {
        "livro": livro_digitado,
        "genero": genero_digitada,
        "valor": valor,
        "status": "Esgotado" # status sempre inicia como pendente
    }

    lista_de_livros.append(novo_registro)

    # Redirecionar para o Home (padrao post-redirect-get)
    return redirect("/")

# Rota 4 Alterar o status
@app.route("/mudar-status/<int:indice>")
def mudar_status(indice):
    if 0 <= indice < len(lista_de_livros):
        # Corrigido: 'status' digitado certo e usando '=' para atribuir valor em vez de '=='
        if lista_de_livros[indice]["status"] == "Esgotado":
            lista_de_livros[indice]["status"] = "Disponivel"
        else:
            lista_de_livros[indice]["status"] = "Esgotado"

    return redirect("/")

# Rota 5: Excluir registro
@app.route("/excluir/<int:indice>")
def excluir_cadastro(indice):
    if 0 <= indice < len(lista_de_livros):
        lista_de_livros.pop(indice)
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)