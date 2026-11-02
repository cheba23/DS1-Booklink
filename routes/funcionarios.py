from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import or_, func

from models import Usuario
from db import db


funcionarios_bp = Blueprint('funcionarios', __name__)

@funcionarios_bp.route('/funcionarios')
@login_required
def listar_funcionarios():

    if current_user.tipo not in ['admin']:
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
    if current_user.tipo not in ['admin']:
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('funcionarios/registrar_funcionarios.html')

    nome = request.form.get('nomeForm', '').strip()
    email = request.form.get('emailForm', '').strip()
    senha = request.form.get('senhaForm', '').strip()

    if not nome:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='O nome é obrigatório'
        )

    if len(nome) > 100:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='O nome deve ter no máximo 100 caracteres'
        )

    if not email:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='O e-mail é obrigatório'
        )

    if '@' not in email or '.' not in email or len(email) > 100:
        return render_template(
            'funcionarios/registrar_funcionarios.html',
            erro='Informe um e-mail válido'
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

    usuario_existente = Usuario.query.filter(
        func.lower(Usuario.email) == email.lower()
    ).first()

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
    flash('Funcionário cadastrado com sucesso!', 'sucesso')

    return redirect(url_for('funcionarios.listar_funcionarios'))


@funcionarios_bp.route('/funcionarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_funcionarios(id):

    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))

    if current_user.tipo != 'admin' and id != current_user.id:
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

    nome = request.form.get('nomeForm', '').strip()
    email = request.form.get('emailForm', '').strip()
    senha = request.form.get('senhaForm', '').strip()

    if not nome:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='O nome é obrigatório'
        )

    if len(nome) > 100:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='O nome deve ter no máximo 100 caracteres'
        )

    if not email:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='O e-mail é obrigatório'
        )

    if '@' not in email or '.' not in email or len(email) > 100:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='Informe um e-mail válido'
        )

    # Verifica se o email já pertence a outro usuário
    usuario_existente = Usuario.query.filter(
        func.lower(Usuario.email) == email.lower(),
        Usuario.id != id
    ).first()

    if usuario_existente:
        return render_template(
            'funcionarios/editar_funcionarios.html',
            funcionario=funcionario,
            erro='Esse e-mail já está cadastrado para outro usuário'
        )

    # Se informou senha, valida o tamanho
    if senha:
        if len(senha) < 6:
            return render_template(
                'funcionarios/editar_funcionarios.html',
                funcionario=funcionario,
                erro='A senha deve ter pelo menos 6 caracteres'
            )
        funcionario.senha = generate_password_hash(senha)

    funcionario.nome = nome
    funcionario.email = email

    db.session.commit()
    flash('Dados atualizados com sucesso!', 'sucesso')

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
    flash('Funcionário promovido a Administrador!', 'sucesso')

    return redirect(url_for('funcionarios.listar_funcionarios'))


@funcionarios_bp.route('/funcionarios/deletar/<int:id>', methods=['GET', 'POST'])
@login_required
def deletar_funcionario(id):

    # Somente dono pode excluir
    if current_user.tipo != 'admin':
        return redirect(url_for('home'))

    if id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'erro')
        return redirect(url_for('funcionarios.listar_funcionarios'))

    usuario = Usuario.query.filter(
        Usuario.id == id,
        Usuario.empresa_id == current_user.empresa_id,
        Usuario.tipo.in_(['funcionario', 'admin'])
    ).first()

    if not usuario:
        flash('Funcionário não encontrado.', 'erro')
        return redirect(url_for('funcionarios.listar_funcionarios'))

    if usuario.vendas:
        flash('Não é possível excluir um funcionário que possui vendas registradas.', 'erro')
        return redirect(url_for('funcionarios.listar_funcionarios'))

    db.session.delete(usuario)
    db.session.commit()
    flash('Funcionário excluído definitivamente!', 'sucesso')

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
    flash('Cargo alterado para Funcionário!', 'sucesso')

    return redirect(url_for('funcionarios.listar_funcionarios'))