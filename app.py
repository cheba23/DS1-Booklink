from flask import Flask, render_template, redirect, url_for
from db import db
from models import Usuario

from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    current_user
)

from routes.livros import livros_bp
from routes.generos import generos_bp
from routes.empresa import empresa_bp
from routes.login import login_bp
from routes.funcionarios import funcionarios_bp
from routes.homeadm import homeadm_bp
from routes.compradores import compradores_bp
from routes.vendas import vendas_bp

app = Flask(__name__)


# =========================
# CONFIGURAÇÕES
# =========================

app.secret_key = 'BookLink123'

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dados.db"


# =========================
# BANCO DE DADOS
# =========================

db.init_app(app)


# =========================
# BLUEPRINTS
# =========================

app.register_blueprint(livros_bp)
app.register_blueprint(generos_bp)
app.register_blueprint(empresa_bp)
app.register_blueprint(login_bp)
app.register_blueprint(funcionarios_bp)
app.register_blueprint(homeadm_bp)
app.register_blueprint(compradores_bp)
app.register_blueprint(vendas_bp)

# =========================
# LOGIN
# =========================

lm = LoginManager(app)

lm.login_view = 'auth.login'


@lm.user_loader
def user_loader(id):

    usuario = Usuario.query.filter_by(
        id=id
    ).first()

    return usuario


# =========================
# PÁGINA INICIAL
# =========================

@app.route('/')
def home():

    if current_user.is_authenticated:
        return redirect(url_for('homeAdm.homeAdm'))

    return render_template('home.html')


# =========================
# LOGOUT
# =========================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(
        url_for('auth.login')
    )


# =========================
# INICIAR SISTEMA
# =========================

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)