from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import or_

from models import Usuario
from db import db


funcionarios_bp = Blueprint('funcionarios', __name__)

@funcionarios_bp.route('/funcionarios')
@login_required
def listar_funcionarios():

    if current_user.tipo not in ['dono', 'admin_empresa']:
        return redirect(url_for('home'))

    busca = request.args.get('busca', '').strip()

    query = Usuario.query.filter_by(
        empresa_id=current_user.empresa_id
    )

    if busca:
        query = query.filter(
            or_(
                Usuario.nome.ilike(f'%{busca}%'),
                Usuario.email.ilike(f'%{busca}%')
            )
        )

    funcionarios = query.order_by(
        Usuario.nome
    ).all()

    return render_template(
        'funcionarios/funcionarios.html',
        funcionarios=funcionarios,
        busca=busca
    )

@funcionarios_bp.route('/funcionarios/registrar', methods=['GET', 'POST'])
@login_required
def registrar_funcionario():

    # Dono e administrador da empresa podem cadastrar funcionários
    if current_user.tipo not in ['dono', 'admin_empresa']:
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('funcionarios/registrar_funcionarios.html')

    nome = request.form['nomeForm'].strip()
    email = request.form['emailForm'].strip()
    senha = request.form['senhaForm'].strip()

    if not nome:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='O nome é obrigatório'
        )

    if not email:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='O e-mail é obrigatório'
        )

    if not senha:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='A senha é obrigatória'
        )

    if len(senha) < 6:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='A senha deve ter pelo menos 6 caracteres'
        )

    usuario_existente = Usuario.query.filter_by(email=email).first()

    if usuario_existente:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='Esse e-mail já está cadastrado'
        )

    novo_funcionario = Usuario(
        nome=nome,
        email=email,
        senha=generate_password_hash(senha),
        tipo='funcionario',
        empresa_id=current_user.empresa_id
    )

    db.session.add(novo_funcionario)
    db.session.commit()

    return redirect(url_for('funcionarios.listar_funcionarios'))


@funcionarios_bp.route('/funcionarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_funcionarios(id):

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
        return redirect(url_for('home'))

    if current_user.tipo != 'dono' and id != current_user.id:
        return redirect(url_for('funcionarios.listar_funcionarios'))

    funcionario = Usuario.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()

    if not funcionario:
        return redirect(url_for('funcionarios.listar_funcionarios'))

    if request.method == 'GET':
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario
        )

    nome = request.form['nomeForm'].strip()
    email = request.form['emailForm'].strip()
    senha = request.form['senhaForm'].strip()

    if not nome:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='O nome é obrigatório'
        )

    if not email:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='O e-mail é obrigatório'
        )

    if not senha:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='A senha é obrigatória'
        )

    if len(senha) < 6:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='A senha deve ter pelo menos 6 caracteres'
        )

    funcionario.nome = nome
    funcionario.email = email

    funcionario.senha = generate_password_hash(senha)

    db.session.commit()

    return redirect(url_for('funcionarios.listar_funcionarios'))

@funcionarios_bp.route('/funcionarios/tornar-admin/<int:id>')
@login_required
def tornar_admin(id):

    # Somente dono podem promover
    if current_user.tipo != 'admin':
        return redirect(url_for('home'))

    funcionario = Usuario.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id,
        tipo='funcionario'
    ).first()

    if not funcionario:
        return "Funcionário não encontrado", 404

    funcionario.tipo = 'admin'

    db.session.commit()

    return redirect(url_for('funcionarios.listar_funcionarios'))


@funcionarios_bp.route('/funcionarios/deletar/<int:id>')
@login_required
def deletar_funcionario(id):

    # Somente dono podem excluir
    if current_user.tipo != 'admin':
        return redirect(url_for('home'))

    usuario = Usuario.query.filter(
        Usuario.id == id,
        Usuario.empresa_id == current_user.empresa_id,
        Usuario.tipo.in_(['funcionario', 'admin'])
    ).first()

    if not usuario:
        return "Funcionário não encontrado", 404

    db.session.delete(usuario)
    db.session.commit()

    return redirect(url_for('funcionarios.listar_funcionarios'))

@funcionarios_bp.route('/funcionarios/tornar-funcionario/<int:id>')
@login_required
def tornar_funcionario(id):

    # Somente o dono pode remover o cargo de administrador
    if current_user.tipo != 'admin':
        return redirect(url_for('home'))

    usuario = Usuario.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id,
        tipo='admin'
    ).first()

    if not usuario:
        return "Administrador não encontrado", 404

    usuario.tipo = 'funcionario'

    db.session.commit()

    return redirect(url_for('funcionarios.listar_funcionarios'))