from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user
from werkzeug.security import check_password_hash

from models import Usuario


login_bp = Blueprint('auth', __name__)


# ==========================================
# LOGIN
# ==========================================

@login_bp.route('/login', methods=['GET', 'POST'])
def login():

    # Se abriu a página de login
    if request.method == 'GET':
        return render_template('login.html')

    # ==========================================
    # PEGAR DADOS DO FORMULÁRIO
    # ==========================================

    email = request.form['emailForm'].strip()
    senha = request.form['senhaForm'].strip()


    # ==========================================
    # VALIDAÇÕES
    # ==========================================

    if not email:
        return render_template(
            'login.html',
            erro='O e-mail é obrigatório'
        )

    if not senha:
        return render_template(
            'login.html',
            erro='A senha é obrigatória'
        )


    # ==========================================
    # PROCURAR USUÁRIO
    # ==========================================

    usuario = Usuario.query.filter_by(
        email=email
    ).first()


    # ==========================================
    # VERIFICAR USUÁRIO E SENHA
    # ==========================================

    if not usuario or not check_password_hash(usuario.senha, senha):
        return render_template(
            'login.html',
            erro='E-mail ou senha incorretos'
        )


    # ==========================================
    # FAZER LOGIN
    # ==========================================

    login_user(usuario, remember=True)


    # ==========================================
    # IR PARA O SISTEMA
    # ==========================================

    return redirect(url_for('homeAdm.homeAdm'))
