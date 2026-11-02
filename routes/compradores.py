from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, func

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

@compradores_bp.route('/compradores/registrar', methods=['GET', 'POST'])
@login_required
def registrar_compradores():
    
    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        return render_template('compradores/registrar_comprador.html')
        
    nome = request.form.get('nomeForm', '').strip()
    email = request.form.get('emailForm', '').strip()
    telefone_raw = request.form.get('telefone', request.form.get('telefoneForm', ''))
    telefone = telefone_raw.strip().replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

    if not nome:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='O nome do comprador é obrigatório'
        )

    if len(nome) > 100:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='O nome deve ter no máximo 100 caracteres'
        )
        
    if not email:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='O email do comprador é obrigatório'
        )

    if '@' not in email or '.' not in email or len(email) > 100:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='Informe um e-mail válido'
        )
            
    if not telefone:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='O telefone do comprador é obrigatório'
        )

    if not telefone.isdigit() or len(telefone) < 10 or len(telefone) > 15:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='Informe um telefone válido com DDD (apenas números)'
        )

    # Verifica duplicidade de comprador por email na empresa
    comprador_email = Comprador.query.filter(
        Comprador.empresa_id == current_user.empresa_id,
        func.lower(Comprador.email) == email.lower()
    ).first()

    if comprador_email:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='Já existe um comprador cadastrado com este e-mail.'
        )

    # Verifica duplicidade de comprador por telefone na empresa
    comprador_tel = Comprador.query.filter(
        Comprador.empresa_id == current_user.empresa_id,
        Comprador.telefone == telefone
    ).first()

    if comprador_tel:
        return render_template(
            'compradores/registrar_comprador.html',
            erro='Já existe um comprador cadastrado com este telefone.'
        )
            
    novo_comprador = Comprador(
        nome=nome,
        email=email,
        telefone=telefone,
        empresa_id=current_user.empresa_id
    )
    
    db.session.add(novo_comprador)
    db.session.commit()
    flash('Comprador cadastrado com sucesso!', 'sucesso')
    
    return redirect(url_for('compradores.listar_compradores'))
            
    
@compradores_bp.route('/compradores/deletar/<int:id>', methods=['GET', 'POST'])
@login_required
def deletar_compradores(id):
    
    if current_user.tipo not in ['admin', 'funcionario']:
        return redirect(url_for('home'))
    
    comprador = Comprador.query.filter_by(
        id=id,
        empresa_id=current_user.empresa_id
    ).first()
    
    if not comprador:
        flash('Comprador não encontrado.', 'erro')
        return redirect(url_for('compradores.listar_compradores'))

    # Verifica se comprador possui vendas antes de excluir
    if comprador.vendas:
        flash('Não é possível excluir um comprador que possui vendas registradas.', 'erro')
        return redirect(url_for('compradores.listar_compradores'))

    db.session.delete(comprador)        
    db.session.commit()
    flash('Comprador excluído definitivamente!', 'sucesso')

    return redirect(url_for('compradores.listar_compradores'))

@compradores_bp.route('/compradores/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_comprador(id):

    if current_user.tipo not in ['admin', 'funcionario']:
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

    nome = request.form.get('nomeForm', '').strip()
    email = request.form.get('emailForm', '').strip()
    telefone_raw = request.form.get('telefoneForm', request.form.get('telefone', ''))
    telefone = telefone_raw.strip().replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

    if not nome:
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador,
            erro='O nome do comprador é obrigatório'
        )

    if len(nome) > 100:
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador,
            erro='O nome deve ter no máximo 100 caracteres'
        )

    if not email:
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador,
            erro='O email do comprador é obrigatório'
        )

    if '@' not in email or '.' not in email or len(email) > 100:
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador,
            erro='Informe um e-mail válido'
        )

    if not telefone:
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador,
            erro='O telefone do comprador é obrigatório'
        )

    if not telefone.isdigit() or len(telefone) < 10 or len(telefone) > 15:
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador,
            erro='Informe um telefone válido com DDD (apenas números)'
        )

    # Verifica duplicidade de email na empresa para outro comprador
    comprador_email = Comprador.query.filter(
        Comprador.empresa_id == current_user.empresa_id,
        func.lower(Comprador.email) == email.lower(),
        Comprador.id != id
    ).first()

    if comprador_email:
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador,
            erro='Já existe outro comprador cadastrado com este e-mail.'
        )

    # Verifica duplicidade de telefone na empresa para outro comprador
    comprador_tel = Comprador.query.filter(
        Comprador.empresa_id == current_user.empresa_id,
        Comprador.telefone == telefone,
        Comprador.id != id
    ).first()

    if comprador_tel:
        return render_template(
            'compradores/editar_comprador.html',
            comprador=comprador,
            erro='Já existe outro comprador cadastrado com este telefone.'
        )

    comprador.nome = nome
    comprador.email = email
    comprador.telefone = telefone

    db.session.commit()
    flash('Comprador atualizado com sucesso!', 'sucesso')

    return redirect(url_for('compradores.listar_compradores'))