from flask import Blueprint, render_template, redirect, url_for, request, session

from flask_login import login_required, current_user

from sqlalchemy import or_

from models import Livro, Comprador, Genero, Venda, ItemVenda, Usuario

from db import db


vendas_bp = Blueprint('vendas', __name__)


# ============================================================
# VERIFICA SE O USUÁRIO PODE ACESSAR AS VENDAS
# ============================================================

def usuario_pode_vender():

    return current_user.tipo in [
        'dono',
        'admin_empresa',
        'funcionario'
    ]


# ============================================================
# PÁGINA PRINCIPAL DA VENDA
# Mostra a venda que está sendo montada na session.
# Funciona tanto para cliente cadastrado quanto
# para venda sem cadastro.
# ============================================================

@vendas_bp.route('/vendas')
@login_required
def nova_venda():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    venda = session.get('venda')

    comprador = None
    itens = []
    total = 0

    if venda:

        # ====================================================
        # BUSCA O COMPRADOR, CASO EXISTA
        # ====================================================

        comprador_id = venda.get('comprador_id')

        if comprador_id:

            comprador = Comprador.query.filter_by(
                id=comprador_id,
                empresa_id=current_user.empresa_id
            ).first()

        # ====================================================
        # BUSCA OS LIVROS DA VENDA
        # ====================================================

        for item in venda.get('itens', []):

            livro = Livro.query.filter_by(
                id=item['livro_id'],
                empresa_id=current_user.empresa_id
            ).first()

            if not livro:
                continue

            subtotal = livro.preco * item['quantidade']

            itens.append({
                'livro': livro,
                'quantidade': item['quantidade'],
                'subtotal': subtotal
            })

            total += subtotal

    return render_template(
        'vendas/nova_venda.html',
        venda=venda,
        comprador=comprador,
        itens=itens,
        total=total
    )


# ============================================================
# SELECIONAR CLIENTE
# Permite pesquisar e escolher um cliente cadastrado.
# ============================================================

@vendas_bp.route('/vendas/cliente')
@login_required
def selecionar_cliente():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    busca = request.args.get('busca', '').strip()

    compradores = []

    if busca:

        compradores = Comprador.query.filter(
            Comprador.empresa_id == current_user.empresa_id,
            or_(
                Comprador.nome.ilike(f'%{busca}%'),
                Comprador.email.ilike(f'%{busca}%'),
                Comprador.telefone.ilike(f'%{busca}%')
            )
        ).all()

    comprador_id = request.args.get('comprador_id')

    comprador_selecionado = None

    if comprador_id:

        comprador_selecionado = Comprador.query.filter_by(
            id=comprador_id,
            empresa_id=current_user.empresa_id
        ).first()

    return render_template(
        'vendas/cliente.html',
        compradores=compradores,
        comprador_selecionado=comprador_selecionado
    )


# ============================================================
# SELECIONAR LIVROS
# Mostra os livros disponíveis para uma venda
# com cliente cadastrado.
# ============================================================

@vendas_bp.route('/vendas/livros')
@login_required
def selecionar_livros():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    comprador_id = request.args.get('comprador_id')

    comprador = Comprador.query.filter_by(
        id=comprador_id,
        empresa_id=current_user.empresa_id
    ).first()

    if not comprador:
        return redirect(url_for('vendas.nova_venda'))

    busca = request.args.get('busca', '').strip()

    livros = []

    if busca:

        livros = Livro.query.join(Genero).filter(
            Livro.empresa_id == current_user.empresa_id,
            Genero.empresa_id == current_user.empresa_id,
            or_(
                Livro.titulo.ilike(f'%{busca}%'),
                Livro.autor.ilike(f'%{busca}%'),
                Genero.nome.ilike(f'%{busca}%')
            )
        ).all()

    return render_template(
        'vendas/escolher_livros.html',
        comprador=comprador,
        livros=livros
    )


# ============================================================
# SELECIONAR UM LIVRO E INFORMAR QUANTIDADE
# Adiciona um livro à venda de um cliente cadastrado.
# ============================================================

@vendas_bp.route('/vendas/livro', methods=['GET', 'POST'])
@login_required
def selecionar_livro():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    comprador_id = request.args.get('comprador_id')
    livro_id = request.args.get('livro_id')

    comprador = Comprador.query.filter_by(
        id=comprador_id,
        empresa_id=current_user.empresa_id
    ).first()

    livro = Livro.query.filter_by(
        id=livro_id,
        empresa_id=current_user.empresa_id
    ).first()

    if not comprador or not livro:
        return redirect(url_for('vendas.nova_venda'))

    if request.method == 'POST':

        # Tenta transformar a quantidade em número

        try:
            quantidade = int(
                request.form.get('quantidade', 0)
            )

        except (ValueError, TypeError):
            quantidade = 0

        # Verifica se a quantidade é válida

        if quantidade <= 0:

            return redirect(
                url_for(
                    'vendas.selecionar_livro',
                    comprador_id=comprador.id,
                    livro_id=livro.id
                )
            )

        # Verifica se existe estoque suficiente

        if quantidade > livro.estoque:

            return redirect(
                url_for(
                    'vendas.selecionar_livro',
                    comprador_id=comprador.id,
                    livro_id=livro.id
                )
            )

        # Se ainda não existe uma venda na session,
        # cria uma nova.

        if 'venda' not in session:

            session['venda'] = {
                'comprador_id': comprador.id,
                'itens': []
            }

        # Garante que a venda pertence ao cliente escolhido

        session['venda']['comprador_id'] = comprador.id

        # Procura se o livro já foi adicionado

        livro_existente = None

        for item in session['venda']['itens']:

            if item['livro_id'] == livro.id:

                livro_existente = item
                break

        # Se o livro já estiver na venda,
        # soma a nova quantidade.

        if livro_existente:

            nova_quantidade = (
                livro_existente['quantidade'] + quantidade
            )

            # Não deixa passar do estoque

            if nova_quantidade > livro.estoque:

                return redirect(
                    url_for(
                        'vendas.selecionar_livro',
                        comprador_id=comprador.id,
                        livro_id=livro.id
                    )
                )

            livro_existente['quantidade'] = nova_quantidade

        else:

            session['venda']['itens'].append({
                'livro_id': livro.id,
                'quantidade': quantidade
            })

        session.modified = True

        return redirect(
            url_for('vendas.nova_venda')
        )

    return render_template(
        'vendas/quantidade.html',
        comprador=comprador,
        livro=livro
    )


# ============================================================
# REVISAR VENDA
# Mostra todos os livros, quantidades e total antes
# de finalizar a venda.
#
# Funciona com cliente cadastrado ou sem cadastro.
# ============================================================

@vendas_bp.route('/vendas/revisar')
@login_required
def revisar_venda():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    venda = session.get('venda')

    if not venda or not venda.get('itens'):

        return redirect(
            url_for('vendas.nova_venda')
        )

    # ========================================================
    # BUSCA O CLIENTE, SE EXISTIR
    # ========================================================

    comprador = None

    comprador_id = venda.get('comprador_id')

    if comprador_id:

        comprador = Comprador.query.filter_by(
            id=comprador_id,
            empresa_id=current_user.empresa_id
        ).first()

        if not comprador:

            session.pop('venda', None)

            return redirect(
                url_for('vendas.nova_venda')
            )

    # ========================================================
    # BUSCA OS LIVROS
    # ========================================================

    itens = []
    total = 0

    for item in venda['itens']:

        livro = Livro.query.filter_by(
            id=item['livro_id'],
            empresa_id=current_user.empresa_id
        ).first()

        if not livro:
            continue

        quantidade = item['quantidade']

        subtotal = livro.preco * quantidade

        itens.append({
            'livro': livro,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

        total += subtotal

    # Se nenhum livro válido foi encontrado

    if not itens:

        session.pop('venda', None)

        return redirect(
            url_for('vendas.nova_venda')
        )

    return render_template(
        'vendas/revisar.html',
        comprador=comprador,
        itens=itens,
        total=total
    )


# ============================================================
# FINALIZAR VENDA
# Cria a Venda e os ItemVenda no banco de dados,
# diminui o estoque e limpa a session.
#
# Funciona com cliente cadastrado ou sem cadastro.
# ============================================================

@vendas_bp.route('/vendas/finalizar', methods=['POST'])
@login_required
def finalizar_venda():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    venda_session = session.get('venda')

    if not venda_session or not venda_session.get('itens'):

        return redirect(
            url_for('vendas.nova_venda')
        )

    # ========================================================
    # BUSCA O CLIENTE, SE EXISTIR
    # ========================================================

    comprador = None

    comprador_id = venda_session.get('comprador_id')

    if comprador_id:

        comprador = Comprador.query.filter_by(
            id=comprador_id,
            empresa_id=current_user.empresa_id
        ).first()

        if not comprador:

            session.pop('venda', None)

            return redirect(
                url_for('vendas.nova_venda')
            )

    # ========================================================
    # PRIMEIRO: VALIDAR TODOS OS LIVROS
    # ========================================================

    itens_validos = []
    total = 0

    for item in venda_session['itens']:

        livro = Livro.query.filter_by(
            id=item['livro_id'],
            empresa_id=current_user.empresa_id
        ).first()

        # Se algum livro não existir,
        # cancela a finalização.

        if not livro:

            return redirect(
                url_for('vendas.nova_venda')
            )

        quantidade = item['quantidade']

        # Verifica quantidade

        if quantidade <= 0:

            return redirect(
                url_for('vendas.nova_venda')
            )

        # Verifica estoque novamente
        # para evitar vender mais do que existe.

        if quantidade > livro.estoque:

            return redirect(
                url_for('vendas.nova_venda')
            )

        subtotal = livro.preco * quantidade

        itens_validos.append({
            'livro': livro,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

        total += subtotal

    # Se não tiver nenhum item válido

    if not itens_validos:

        return redirect(
            url_for('vendas.nova_venda')
        )

    # ========================================================
    # CRIAR A VENDA
    #
    # Se houver comprador:
    # comprador_id recebe o ID.
    #
    # Se for venda sem cadastro:
    # comprador_id fica como None.
    # ========================================================

    venda = Venda(
        comprador_id=(
            comprador.id
            if comprador
            else None
        ),
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id,
        total=total
    )

    db.session.add(venda)

    # ========================================================
    # CRIAR OS ITENS DA VENDA
    # E DIMINUIR O ESTOQUE
    # ========================================================

    for item in itens_validos:

        livro = item['livro']
        quantidade = item['quantidade']
        subtotal = item['subtotal']

        item_venda = ItemVenda(
            venda=venda,
            livro_id=livro.id,
            quantidade=quantidade,
            preco_unitario=livro.preco,
            subtotal=subtotal
        )

        db.session.add(item_venda)

        # Diminui o estoque

        livro.estoque -= quantidade

    # ========================================================
    # SALVAR NO BANCO
    # ========================================================

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        return redirect(
            url_for('vendas.nova_venda')
        )

    # ========================================================
    # LIMPAR A VENDA DA SESSION
    # ========================================================

    session.pop('venda', None)

    # ========================================================
    # MOSTRAR PÁGINA DE VENDA FINALIZADA
    # ========================================================

    return render_template(
        'vendas/finalizada.html',
        venda=venda
    )


# ============================================================
# LIMPAR VENDA
# Cancela a venda que está sendo montada e remove
# os dados temporários da session.
# ============================================================

@vendas_bp.route('/vendas/limpar')
@login_required
def limpar_venda():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    session.pop('venda', None)

    return redirect(
        url_for('vendas.nova_venda')
    )


# ============================================================
# INICIAR VENDA SEM CADASTRO
# Cria uma nova venda sem cliente cadastrado.
# O comprador_id fica como None.
# ============================================================

@vendas_bp.route('/vendas/sem-cadastro')
@login_required
def venda_sem_cadastro():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    # Cria a venda temporária sem comprador

    session['venda'] = {
        'comprador_id': None,
        'itens': []
    }

    return redirect(
        url_for(
            'vendas.selecionar_livros_sem_cadastro'
        )
    )


# ============================================================
# SELECIONAR LIVROS DA VENDA SEM CADASTRO
# Permite pesquisar os livros para uma venda
# que não possui cliente cadastrado.
# ============================================================

@vendas_bp.route('/vendas/sem-cadastro/livros')
@login_required
def selecionar_livros_sem_cadastro():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    venda = session.get('venda')

    # Verifica se existe uma venda sem cadastro

    if not venda or venda.get('comprador_id') is not None:

        return redirect(
            url_for('vendas.nova_venda')
        )

    busca = request.args.get(
        'busca',
        ''
    ).strip()

    livros = []

    if busca:

        livros = Livro.query.join(Genero).filter(

            Livro.empresa_id == current_user.empresa_id,

            Genero.empresa_id == current_user.empresa_id,

            or_(
                Livro.titulo.ilike(f'%{busca}%'),

                Livro.autor.ilike(f'%{busca}%'),

                Genero.nome.ilike(f'%{busca}%')
            )

        ).all()

    return render_template(
        'vendas/escolher_livros.html',
        comprador=None,
        livros=livros,
        sem_cadastro=True
    )


# ============================================================
# SELECIONAR LIVRO E QUANTIDADE SEM CADASTRO
# Adiciona um livro à venda sem precisar
# de um cliente cadastrado.
# ============================================================

@vendas_bp.route(
    '/vendas/sem-cadastro/livro',
    methods=['GET', 'POST']
)
@login_required
def selecionar_livro_sem_cadastro():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    venda = session.get('venda')

    # Verifica se existe uma venda sem cadastro

    if not venda or venda.get('comprador_id') is not None:

        return redirect(
            url_for('vendas.nova_venda')
        )

    livro_id = request.args.get('livro_id')

    livro = Livro.query.filter_by(
        id=livro_id,
        empresa_id=current_user.empresa_id
    ).first()

    if not livro:

        return redirect(
            url_for(
                'vendas.selecionar_livros_sem_cadastro'
            )
        )

    # ========================================================
    # QUANDO O FORMULÁRIO FOR ENVIADO
    # ========================================================

    if request.method == 'POST':

        # Tenta transformar a quantidade em número

        try:

            quantidade = int(
                request.form.get(
                    'quantidade',
                    0
                )
            )

        except (ValueError, TypeError):

            quantidade = 0

        # Verifica quantidade

        if quantidade <= 0:

            return redirect(
                url_for(
                    'vendas.selecionar_livro_sem_cadastro',
                    livro_id=livro.id
                )
            )

        # Verifica estoque

        if quantidade > livro.estoque:

            return redirect(
                url_for(
                    'vendas.selecionar_livro_sem_cadastro',
                    livro_id=livro.id
                )
            )

        # ====================================================
        # PROCURA SE O LIVRO JÁ ESTÁ NA VENDA
        # ====================================================

        livro_existente = None

        for item in venda['itens']:

            if item['livro_id'] == livro.id:

                livro_existente = item
                break

        # ====================================================
        # SE JÁ EXISTIR, SOMA A QUANTIDADE
        # ====================================================

        if livro_existente:

            nova_quantidade = (
                livro_existente['quantidade']
                + quantidade
            )

            # Não deixa passar do estoque

            if nova_quantidade > livro.estoque:

                return redirect(
                    url_for(
                        'vendas.selecionar_livro_sem_cadastro',
                        livro_id=livro.id
                    )
                )

            livro_existente['quantidade'] = nova_quantidade

        # ====================================================
        # SE NÃO EXISTIR, ADICIONA O LIVRO
        # ====================================================

        else:

            venda['itens'].append({
                'livro_id': livro.id,
                'quantidade': quantidade
            })

        # Informa ao Flask que a session foi alterada

        session.modified = True

        return redirect(
            url_for('vendas.nova_venda')
        )

    # ========================================================
    # MOSTRA A PÁGINA PARA INFORMAR A QUANTIDADE
    # ========================================================

    return render_template(
        'vendas/quantidade.html',
        comprador=None,
        livro=livro,
        sem_cadastro=True
    )
    
    

# ============================================================
# HISTÓRICO DE VENDAS
# Mostra todas as vendas da empresa do usuário.
# ============================================================

# ============================================================
# HISTÓRICO DE VENDAS
# Mostra as vendas da empresa e permite pesquisar
# por cliente, funcionário ou número da venda.
# ============================================================

# ============================================================
# HISTÓRICO DE VENDAS
# ============================================================

@vendas_bp.route('/vendas/historico')
@login_required
def historico_vendas():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    vendas = Venda.query.filter_by(
        empresa_id=current_user.empresa_id
    ).order_by(
        Venda.data_venda.desc()
    ).all()

    return render_template(
        'vendas/historico.html',
        vendas=vendas
    )
    
# ============================================================
# BUSCAR CLIENTE NO HISTÓRICO
# ============================================================

@vendas_bp.route('/vendas/historico/clientes')
@login_required
def buscar_clientes_historico():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    busca = request.args.get(
        'busca',
        ''
    ).strip()

    clientes = []

    if busca:

        clientes = Comprador.query.filter(
            Comprador.empresa_id == current_user.empresa_id,
            Comprador.nome.ilike(f'%{busca}%')
        ).order_by(
            Comprador.nome
        ).all()

    return render_template(
        'vendas/buscar_clientes.html',
        clientes=clientes,
        busca=busca
    )
    
# ============================================================
# HISTÓRICO DE COMPRAS DO CLIENTE
# ============================================================

@vendas_bp.route('/vendas/historico/cliente/<int:cliente_id>')
@login_required
def historico_cliente(cliente_id):

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    cliente = Comprador.query.filter_by(
        id=cliente_id,
        empresa_id=current_user.empresa_id
    ).first_or_404()

    vendas = Venda.query.filter_by(
        comprador_id=cliente.id,
        empresa_id=current_user.empresa_id
    ).order_by(
        Venda.data_venda.desc()
    ).all()

    total_gasto = sum(
        venda.total
        for venda in vendas
    )

    return render_template(
        'vendas/historico_cliente.html',
        cliente=cliente,
        vendas=vendas,
        total_gasto=total_gasto
    )
    
# ============================================================
# BUSCAR VENDA PELO NÚMERO
# ============================================================

@vendas_bp.route('/vendas/historico/buscar-venda')
@login_required
def buscar_venda_historico():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    busca = request.args.get(
        'numero',
        ''
    ).strip()

    if not busca.isdigit():
        return redirect(
            url_for(
                'vendas.historico_vendas'
            )
        )

    venda_id = int(busca)

    venda = Venda.query.filter_by(
        id=venda_id,
        empresa_id=current_user.empresa_id
    ).first_or_404()

    return redirect(
        url_for(
            'vendas.detalhes_venda',
            venda_id=venda.id
        )
    )
    
# ============================================================
# BUSCAR FUNCIONÁRIO
# ============================================================

@vendas_bp.route('/vendas/historico/funcionarios')
@login_required
def buscar_funcionarios_historico():

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    busca = request.args.get(
        'busca',
        ''
    ).strip()

    funcionarios = []

    if busca:

        funcionarios = Usuario.query.filter(
            Usuario.empresa_id == current_user.empresa_id,
            Usuario.nome.ilike(f'%{busca}%'),
            Usuario.tipo.in_([
                'dono',
                'admin_empresa',
                'funcionario'
            ])
        ).order_by(
            Usuario.nome
        ).all()

    return render_template(
        'vendas/buscar_funcionarios.html',
        funcionarios=funcionarios,
        busca=busca
    )
    
# ============================================================
# HISTÓRICO DE VENDAS DO FUNCIONÁRIO
# ============================================================

@vendas_bp.route('/vendas/historico/funcionario/<int:usuario_id>')
@login_required
def historico_funcionario(usuario_id):

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    funcionario = Usuario.query.filter_by(
        id=usuario_id,
        empresa_id=current_user.empresa_id
    ).first_or_404()

    vendas = Venda.query.filter_by(
        usuario_id=funcionario.id,
        empresa_id=current_user.empresa_id
    ).order_by(
        Venda.data_venda.desc()
    ).all()

    return render_template(
        'vendas/historico_funcionario.html',
        funcionario=funcionario,
        vendas=vendas
    )
    
# ============================================================
# DETALHES DE UMA VENDA
# ============================================================

@vendas_bp.route('/vendas/historico/<int:venda_id>')
@login_required
def detalhes_venda(venda_id):

    if not usuario_pode_vender():
        return redirect(url_for('home'))

    venda = Venda.query.filter_by(
        id=venda_id,
        empresa_id=current_user.empresa_id
    ).first_or_404()

    return render_template(
        'vendas/detalhes.html',
        venda=venda
    )