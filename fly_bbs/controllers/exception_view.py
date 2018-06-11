from flask import Blueprint, request,session,jsonify, url_for, current_app
from fly_bbs.models import GlobalApiException

exception_view = Blueprint('exception', __name__)


@exception_view.app_errorhandler(GlobalApiException)
def api_exception(ex):
    return jsonify(ex.code_msg)
