from flask import Blueprint, jsonify, request
from app import app, redis

import json


api_bp = Blueprint('api', __name__)


def fail(message, code=400):
    return (
        jsonify({
            'error': message,
        }),
        code
    )


@api.errorhandler(404)
def not_found(error):
    return fail('Not found.', 404)


@api.errorhandler(401)
def unauthorized(error):
    return fail('You\'re not authorized to perform this action.', 401)


@api.errorhandler(403)
def forbidden(error):
    return fail('You don\'t have permission to do this.', 403)


@api_bp.route('/alert_level')
def api_alert_level():
    alert_level = redis.get('alert_level')
    return {
        'alert_level': alert_level,
    }


@api_bp.route('/<realm>')
def api_statistics(realm: str):
    """
    Fetch statistics on COVID at Yale or in Connecticut.
    :param realm: the context for which to get statistics - 'yale' or 'connecticut'.
    """
    if realm not in ('yale', 'connecticut'):
        abort(404)
    statistics = json.loads(redis.get('yale'))
    return jsonify(statistics)
