# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g, url_for
from werkzeug.routing import BuildError

from udata.i18n import I18nBlueprint, language

from . import DBTestMixin, WebTestMixin, TestCase
from .factories import UserFactory


bp = I18nBlueprint('i18nbp', __name__, static_folder='static')


@bp.route('/lang/<msg>/')
def lang(msg):
    return g.lang_code


@bp.route('/hardcoded/')
def hardcoded():
    out = g.lang_code + '-'
    with language('fr'):
        out += g.lang_code
    return out


class I18nBlueprintTest(WebTestMixin, DBTestMixin, TestCase):
    def create_app(self):
        app = super(I18nBlueprintTest, self).create_app()
        app.config['DEFAULT_LANGUAGE'] = 'en'
        app.config['LANGUAGES'] = {
            'en': 'English',
            'fr': 'Français',
        }
        app.register_blueprint(bp)
        return app

    def test_lang_inserted_url_for(self):
        self.assertEqual(url_for('i18nbp.lang', msg='test'), '/en/lang/test/')

    def test_redirect_url_for(self):
        self.assertEqual(
            url_for('i18nbp.lang_redirect', msg='test'), '/lang/test/')

    def test_lang_ignored_for_static(self):
        self.assertEqual(url_for('i18nbp.static', filename='test.jpg'),
                         '/static/test.jpg')
        with self.assertRaises(BuildError):
            url_for('i18nbp.static_redirect', filename='test.jpg')

    def test_redirect_on_missing_lang(self):
        response = self.get('/lang/test/?q=test')
        self.assertRedirects(response, '/en/lang/test/?q=test')

    def test_do_not_redirect_and_set_lang(self):
        self.assertEqual(self.get('/fr/lang/test/').data, 'fr')
        self.assertEqual(self.get('/en/lang/test/').data, 'en')

    def test_redirect_on_default_lang_for_unknown_lang(self):
        self.assertRedirects(self.get('/sk/lang/test/'), '/en/lang/test/')

    def test_404_on_default_lang_for_unknown_lang(self):
        self.assert404(self.get('/sk/not-found/'))

    def test_language_contact_manager(self):
        self.assertEqual(self.get('/fr/hardcoded/').data, 'fr-fr')
        self.assertEqual(self.get('/en/hardcoded/').data, 'en-fr')

    def test_redirect_user_prefered_lang(self):
        self.login(UserFactory(prefered_language='fr'))

        response = self.get('/lang/test/?q=test')
        self.assertRedirects(response, '/fr/lang/test/?q=test')
