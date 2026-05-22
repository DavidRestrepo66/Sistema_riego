from flask import Blueprint, jsonify

from repositories.mongo_extra_repository import MongoExtraRepository

from utils.decorators import login_required

mongo_bp = Blueprint('mongo', __name__, url_prefix='/api/mongo')


@mongo_bp.route('/alertas')
@login_required
def api_alertas():

    try:

        datos = MongoExtraRepository.get_alertas()

        return jsonify(datos)

    except Exception as e:

        return jsonify({"error": str(e)}), 500


@mongo_bp.route('/configuraciones')
@login_required
def api_configuraciones():

    try:

        datos = MongoExtraRepository.get_configuraciones()

        return jsonify(datos)

    except Exception as e:

        return jsonify({"error": str(e)}), 500
