from datetime import datetime

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Usuario, Livro, Comprador, Venda, ItemVenda
from db import db


homeadm_bp = Blueprint('homeAdm', __name__)


@homeadm_bp.route('/homeAdm')
@login_required
def homeAdm():

    empresa_id = current_user.empresa_id

    # =========================
    # LIVROS
    # =========================

    total_livros = Livro.query.filter_by(
        empresa_id=empresa_id
    ).count()

    total_estoque = db.session.query(
        db.func.sum(Livro.estoque)
    ).filter_by(
        empresa_id=empresa_id
    ).scalar() or 0

    livros_estoque_baixo = Livro.query.filter(
        Livro.empresa_id == empresa_id,
        Livro.estoque <= 5
    ).count()

    # =========================
    # USUÁRIOS
    # =========================

    total_usuarios = Usuario.query.filter_by(
        empresa_id=empresa_id
    ).count()

    # =========================
    # CLIENTES
    # =========================

    total_clientes = Comprador.query.filter_by(
        empresa_id=empresa_id
    ).count()

    # =========================
    # VENDAS
    # =========================

    total_vendas = Venda.query.filter_by(
        empresa_id=empresa_id
    ).count()

    # =========================
    # DATA DE HOJE
    # =========================

    inicio_do_dia = datetime.now().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    # =========================
    # VENDAS DE HOJE
    # =========================

    vendas_hoje = Venda.query.filter(
        Venda.empresa_id == empresa_id,
        Venda.data_venda >= inicio_do_dia
    ).count()

    # =========================
    # FATURAMENTO
    # SOMENTE PARA O DONO
    # =========================

    faturamento = 0
    faturamento_hoje = 0

    if current_user.tipo == 'dono':

        faturamento = db.session.query(
            db.func.sum(Venda.total)
        ).filter(
            Venda.empresa_id == empresa_id
        ).scalar() or 0

        faturamento_hoje = db.session.query(
            db.func.sum(Venda.total)
        ).filter(
            Venda.empresa_id == empresa_id,
            Venda.data_venda >= inicio_do_dia
        ).scalar() or 0

    # =========================
    # LIVRO MAIS VENDIDO
    # =========================

    livro_mais_vendido = db.session.query(
        Livro.titulo,
        db.func.sum(ItemVenda.quantidade).label('quantidade_vendida')
    ).join(
        ItemVenda,
        ItemVenda.livro_id == Livro.id
    ).join(
        Venda,
        Venda.id == ItemVenda.venda_id
    ).filter(
        Livro.empresa_id == empresa_id,
        Venda.empresa_id == empresa_id
    ).group_by(
        Livro.id,
        Livro.titulo
    ).order_by(
        db.func.sum(ItemVenda.quantidade).desc()
    ).first()

    # =========================
    # ÚLTIMAS 5 VENDAS
    # =========================

    ultimas_vendas = Venda.query.filter_by(
        empresa_id=empresa_id
    ).order_by(
        Venda.data_venda.desc()
    ).limit(5).all()

    # =========================
    # DASHBOARD
    # =========================

    return render_template(
        'homeAdm.html',

        total_livros=total_livros,
        total_estoque=total_estoque,
        livros_estoque_baixo=livros_estoque_baixo,

        total_usuarios=total_usuarios,
        total_clientes=total_clientes,

        total_vendas=total_vendas,
        vendas_hoje=vendas_hoje,

        faturamento=faturamento,
        faturamento_hoje=faturamento_hoje,

        livro_mais_vendido=livro_mais_vendido,
        ultimas_vendas=ultimas_vendas
    )
