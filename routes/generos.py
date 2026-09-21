from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from models import Genero, Livro
from db import db


generos_bp = Blueprint('generos', __name__)


# ==========================================
# LISTAR GÊNEROS
# ==========================================

@generos_bp.route('/generos')
@login_required
def listar_generos():

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
        return redirect(url_for('home'))

    generos = Genero.query.filter_by(
        empresa_id=current_user.empresa_id
    ).all()

    return render_template(
        'generos/generos.html',
        generos=generos
    )


# ==========================================
# EDITAR GÊNERO
# ==========================================

@generos_bp.route('/editar-genero/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_genero(id):

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
        return redirect(url_for('home'))

    # Procura o gênero somente dentro da empresa atual
    genero = Genero.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()

    if not genero:
        return "Gênero não encontrado", 404

    if request.method == 'GET':
        return render_template(
            'generos/editar_genero.html',
            genero=genero
        )

    nome = request.form['nomeForm'].strip()

    if not nome:
        return render_template(
            'generos/editar_genero.html',
            genero=genero,
            erro='O nome do gênero é obrigatório'
        )

    genero.nome = nome

    db.session.commit()

    return redirect(url_for('generos.listar_generos'))


# ==========================================
# DELETAR GÊNERO
# ==========================================

@generos_bp.route('/deletar-genero/<int:id>')
@login_required
def deletar_genero(id):

    if current_user.tipo not in ['dono', 'funcionario']:
        return redirect(url_for('home'))

    # Busca somente um gênero da própria empresa
    genero = Genero.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()

    if not genero:
        return "Gênero não encontrado", 404

    # Verifica se algum livro usa esse gênero
    livros = Livro.query.filter_by(
        genero_id=genero.id,
        empresa_id=current_user.empresa_id
    ).first()

    if livros:
        generos = Genero.query.filter_by(
            empresa_id=current_user.empresa_id
        ).all()

        return render_template(
            'generos/generos.html',
            generos=generos,
            erro='Não é possível excluir um gênero que possui livros cadastrados.'
        )

    # Exclui o gênero
    db.session.delete(genero)
    db.session.commit()

    return redirect(url_for('generos.listar_generos'))


# ==========================================
# CADASTRAR GÊNERO
# ==========================================

@generos_bp.route('/registrar_genero', methods=['GET', 'POST'])
@login_required
def registrar_genero():

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('generos/registrar_genero.html')

    nome = request.form['nomeForm'].strip()

    if not nome:
        return render_template(
            'generos/registrar_genero.html',
            erro='O nome do gênero é obrigatório'
        )

    novo_genero = Genero(
        nome=nome,
        empresa_id=current_user.empresa_id
    )

    db.session.add(novo_genero)
    db.session.commit()

    return redirect(url_for('generos.listar_generos'))