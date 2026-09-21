from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash

from models import Empresa, Usuario
from db import db


empresa_bp = Blueprint('empresa', __name__)


# ==========================================
# CADASTRAR EMPRESA
# ==========================================

@empresa_bp.route('/empresa/registrar', methods=['GET', 'POST'])
def registrar_empresa():

    # Se abriu a página
    if request.method == 'GET':
        return render_template('registrar_empresa.html')

    # ==========================================
    # PEGAR DADOS DO FORMULÁRIO
    # ==========================================

    nome_empresa = request.form['nomeEmpresaForm'].strip()
    cnpj = request.form['cnpjForm'].strip().replace(".", "").replace("/", "").replace("-", "")
    
    nome_dono = request.form['nomeDonoForm'].strip()
    email = request.form['emailForm'].strip()
    senha = request.form['senhaForm'].strip()


    # ==========================================
    # VALIDAÇÕES
    # ==========================================

    if not nome_empresa:
        return render_template(
            'registrar_empresa.html',
            erro='O nome da empresa é obrigatório'
        )

    if not cnpj:
        return render_template(
            'registrar_empresa.html',
            erro='O CNPJ é obrigatório'
        )

    if not nome_dono:
        return render_template(
            'registrar_empresa.html',
            erro='O nome do dono é obrigatório'
        )

    if not email:
        return render_template(
            'registrar_empresa.html',
            erro='O e-mail é obrigatório'
        )

    if not senha:
        return render_template(
            'registrar_empresa.html',
            erro='A senha é obrigatória'
        )


    # ==========================================
    # VERIFICAR SE CNPJ JÁ EXISTE
    # ==========================================

    empresa_existente = Empresa.query.filter_by(
        cnpj=cnpj
    ).first()

    if empresa_existente:
        return render_template(
            'registrar_empresa.html',
            erro='Esse CNPJ já está cadastrado'
        )


    # ==========================================
    # VERIFICAR SE E-MAIL JÁ EXISTE
    # ==========================================

    usuario_existente = Usuario.query.filter_by(
        email=email
    ).first()

    if usuario_existente:
        return render_template(
            'registrar_empresa.html',
            erro='Esse e-mail já está cadastrado'
        )


    # ==========================================
    # CRIAR EMPRESA
    # ==========================================

    nova_empresa = Empresa(
        nome=nome_empresa,
        cnpj=cnpj
    )

    db.session.add(nova_empresa)
    db.session.commit()


    # ==========================================
    # CRIAR DONO DA EMPRESA
    # ==========================================

    nova_senha = generate_password_hash(senha)

    novo_usuario = Usuario(
        nome=nome_dono,
        email=email,
        senha=nova_senha,
        tipo='dono',
        empresa_id=nova_empresa.id
    )

    db.session.add(novo_usuario)
    db.session.commit()


    # ==========================================
    # FINALIZAR CADASTRO
    # ==========================================

    return redirect(url_for('auth.login'))

