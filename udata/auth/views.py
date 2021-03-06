# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import request

from udata.auth import current_user

from flask.ext.security.views import change_password
from flask.ext.security.views import confirm_email
from flask.ext.security.views import forgot_password
from flask.ext.security.views import login
from flask.ext.security.views import logout
from flask.ext.security.views import register
from flask.ext.security.views import reset_password
from flask.ext.security.views import send_confirmation
from flask.ext.security.views import send_login
from flask.ext.security.views import token_login


def slash_url_suffix(url, suffix):
    """Adds a slash either to the beginning or the end of a suffix
       (which is to be appended to a URL), depending on whether or not
       the URL ends with a slash.
    """

    return url.endswith('/') and ('%s/' % suffix) or ('/%s' % suffix)


def create_security_blueprint(state, import_name):
    from udata.i18n import I18nBlueprint
    # from flask.ext.security.utils import slash_url_suffix

    """
    Creates the security extension blueprint
    This creates an I18nBlueprint to use as a base.
    """

    bp = I18nBlueprint(state.blueprint_name, import_name,
                       url_prefix=state.url_prefix,
                       subdomain=state.subdomain,
                       template_folder='templates')

    bp.route(state.logout_url, endpoint='logout')(logout)

    if state.passwordless:
        bp.route(state.login_url,
                 methods=['GET', 'POST'],
                 endpoint='login')(send_login)
        bp.route(
            state.login_url + slash_url_suffix(state.login_url, '<token>'),
            endpoint='token_login'
        )(token_login)
    else:
        bp.route(state.login_url,
                 methods=['GET', 'POST'],
                 endpoint='login')(login)

    if state.registerable:
        bp.route(state.register_url,
                 methods=['GET', 'POST'],
                 endpoint='register')(register)

    if state.recoverable:
        bp.route(state.reset_url,
                 methods=['GET', 'POST'],
                 endpoint='forgot_password')(forgot_password)
        bp.route(
            state.reset_url + slash_url_suffix(state.reset_url, '<token>'),
            methods=['GET', 'POST'],
            endpoint='reset_password'
        )(reset_password)

    if state.changeable:
        bp.route(state.change_url,
                 methods=['GET', 'POST'],
                 endpoint='change_password')(change_password)

    if state.confirmable:
        bp.route(state.confirm_url,
                 methods=['GET', 'POST'],
                 endpoint='send_confirmation')(send_confirmation)
        bp.route(
            state.confirm_url + slash_url_suffix(state.confirm_url, '<token>'),
            methods=['GET', 'POST'],
            endpoint='confirm_email'
        )(confirm_email)

    return bp

auth = Blueprint('auth', __name__)


@auth.before_app_request
def ensure_https_authenticated_users():
    # Force authenticated users to use https
    if (not current_app.config.get('TESTING', False) and
            current_app.config.get('USE_SSL', False) and
            current_user.is_authenticated and not
            request.is_secure):
        return redirect(request.url.replace('http://', 'https://'))
