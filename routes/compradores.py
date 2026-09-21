from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_

from models import Comprador
from db import db

compradores_bp = Blueprint('compradores', __name__)

@compradores_bp.route('/compradores')
@login_required
def listar_compradores():

    busca = request.args.get(
        'busca',
        ''
    ).strip()

    query = Comprador.query.filter_by(
        empresa_id=current_user.empresa_id
    )

    if busca:

        query = query.filter(
            or_(
                Comprador.nome.ilike(
                    f'%{busca}%'
                ),

                Comprador.email.ilike(
                    f'%{busca}%'
                ),

                Comprador.telefone.ilike(
                    f'%{busca}%'
                )
            )
        )

    compradores = query.order_by(
        Comprador.nome
    ).all()

    return render_template(
        'compradores/compradores.html',
        compradores=compradores,
        busca=busca
    )

@compradores_bp.route('/compradores/registrar', methods = ['GET', 'POST'])
@login_required
def registrar_compradores():
    
    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
            return render_template('compradores/registrar_comprador.html')
        
    nome = request.form['nomeForm'].strip()
    email = request.form['emailForm'].strip()
    telefone = request.form["telefone"].strip().replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

    if not nome:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='O nome do comprador é obrigatório'
        )
        
    if not email:
            return render_template(
                'compradores/registrar_comprador.html',
                erro='O email do comprador é obrigatório'
            )
            
    if not telefone:
            return render_template(
                'compradores/registrar_comprador.html',
                erro='O telefone do comprador é obrigatório'
            )
            
    novo_comprador = Comprador(
        nome = nome,
        email=email,
        telefone=telefone,
        empresa_id=current_user.empresa_id
    )
    
    db.session.add(novo_comprador)
    db.session.commit()
    
    return redirect(url_for('compradores.listar_compradores'))
            
    
@compradores_bp.route('/compradores/deletar/<int:id>')
@login_required
def deletar_compradores(id):
    
    # TODO: verificar se comprador possui vendas antes de excluir
    
    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
        return redirect(url_for('home'))
    
    comprador = Comprador.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()
    
    if not comprador:
        return redirect(url_for('compradores.listar_compradores'))

    db.session.delete(comprador)        
    db.session.commit()

    return redirect(url_for('compradores.listar_compradores'))

@compradores_bp.route('/compradores/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_comprador(id):

    if current_user.tipo not in ['dono', 'admin_empresa', 'funcionario']:
        return redirect(url_for('home'))

    comprador = Comprador.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()

    if not comprador:
        return redirect(url_for('compradores.listar_compradores'))

    if request.method == 'GET':
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador
        )

    nome = request.form['nomeForm'].strip()
    email = request.form['emailForm'].strip()
    telefone = request.form['telefoneForm'].strip()

    if not nome:
        return render_template(
            'compradores/registrar_comprador.html',
            comprador=comprador,
            erro='O nome do comprador é obrigatório'
        )

    if not email:
        return render_template(
            'compradores/registrar_comprador.html',
            comprador=comprador,
            erro='O email do comprador é obrigatório'
        )

    if not telefone:
        return render_template(
            'compradores/registrar_comprador.html',
            comprador=comprador,
            erro='O telefone do comprador é obrigatório'
        )

    comprador.nome = nome
    comprador.email = email
    comprador.telefone = telefone

    db.session.commit()

    return redirect(url_for('compradores.listar_compradores'))