from flask import Blueprint, render_template, redirect, url_for

from utils.decorators import login_required

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return redirect(url_for('auth.login'))


@views_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@views_bp.route('/analisis')
@login_required
def analisis():
    return render_template('analisis.html')


@views_bp.route('/graficos')
@login_required
def graficos():
    return render_template('graficos.html')


@views_bp.route('/graficos/<tipo>')
@login_required
def grafico_detalle(tipo):

    allowed = [
        'temp_dht',
        'temp_bmp',
        'humedad',
        'presion',
        'luz'
    ]

    if tipo not in allowed:
        return "Tipo inválido", 400

    return render_template(
        'detalle.html',
        tipo=tipo
    )