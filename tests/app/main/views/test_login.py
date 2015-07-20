from functools import wraps
from lxml import html
from nose.tools import assert_equal, assert_in
import mock
try:
    from urlparse import urlsplit
except ImportError:
    from urllib.parse import urlsplit

from ...helpers import BaseApplicationTest


def authenticate_user(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        with mock.patch('app.main.views.login.data_api_client') as p:
            p.authenticate_user.return_value = {
                'users': {
                    'id': 12345,
                    'emailAddress': 'valid@example.com',
                    'role': 'admin',
                    'locked': False,
                }
            }
            return func(*args, **kwargs)

    return wrapped


class TestLogin(BaseApplicationTest):
    def test_should_be_redirected_to_login_page(self):
        res = self.client.get('/admin')
        assert_equal(res.status_code, 302)
        assert_equal(urlsplit(res.location).path, '/admin/login')

    def test_should_show_login_page(self):
        res = self.client.get("/admin/login")
        assert_equal(res.status_code, 200)
        assert_in("Administrator login", res.get_data(as_text=True))

    @authenticate_user
    def test_valid_login(self):
        res = self.client.post('/admin/login', data={
            'email_address': 'valid@email.com',
            'password': '1234567890'
        })
        assert_equal(res.status_code, 302)

        res = self.client.get('/admin')
        assert_equal(res.status_code, 200)

    @authenticate_user
    def test_ok_next_url_redirects_on_login(self):
        res = self.client.post('/admin/login?next=/admin/safe', data={
            'email_address': 'valid@example.com',
            'password': '1234567890',
        })
        assert_equal(res.status_code, 302)
        assert_equal(urlsplit(res.location).path, '/admin/safe')

    @authenticate_user
    def test_bad_next_url_takes_user_to_dashboard(self):
        res = self.client.post('/admin/login?next=http://badness.com', data={
            'email_address': 'valid@example.com',
            'password': '1234567890',
        })
        assert_equal(res.status_code, 302)
        assert_equal(urlsplit(res.location).path, '/admin')

    @authenticate_user
    def test_should_have_cookie_on_redirect(self):
        with self.app.app_context():
            self.app.config['SESSION_COOKIE_DOMAIN'] = '127.0.0.1'
            self.app.config['SESSION_COOKIE_SECURE'] = True
            res = self.client.post('/admin/login', data={
                'email_address': 'valid@example.com',
                'password': '1234567890',
            })
            cookie_parts = res.headers['Set-Cookie'].split('; ')
            assert_in('Secure', cookie_parts)
            assert_in('HttpOnly', cookie_parts)
            assert_in('Path=/admin', cookie_parts)

    @authenticate_user
    def test_should_redirect_to_login_on_logout(self):
        self.client.post('/admin/login', data={
            'email_address': 'valid@example.com',
            'password': '1234567890',
        })
        res = self.client.get('/admin/logout')
        assert_equal(res.status_code, 302)
        assert_equal(urlsplit(res.location).path, '/admin/login')

    @authenticate_user
    def test_logout_should_log_user_out(self):
        self.client.post('/admin/login', data={
            'email_address': 'valid@example.com',
            'password': '1234567890',
        })
        self.client.get('/admin/logout')
        res = self.client.get('/admin')
        assert_equal(res.status_code, 302)
        assert_equal(urlsplit(res.location).path, '/admin/login')

    @mock.patch('app.main.views.login.data_api_client')
    def test_should_return_a_403_for_invalid_login(self, data_api_client):
        data_api_client.authenticate_user.return_value = None

        res = self.client.post('/admin/login', data={
            'email_address': 'valid@example.com',
            'password': '1234567890',
        })

        assert_equal(res.status_code, 403)

    @mock.patch('app.main.views.login.data_api_client')
    def test_should_return_a_403_if_invalid_role(self, data_api_client):
        data_api_client.authenticate_user.return_value = {
            'users': {
                'id': 12345,
                'email_address': 'valid@example.com',
                'role': 'supplier',
            }
        }

        res = self.client.post('/admin/login', data={
            'email_address': 'valid@example.com',
            'password': '1234567890',
        })

        assert_equal(res.status_code, 403)

    def test_should_be_validation_error_if_no_email_or_password(self):
        res = self.client.post('/admin/login', data={})
        assert_equal(res.status_code, 400)

    def test_should_be_validation_error_if_invalid_email(self):
        res = self.client.post('/admin/login', data={
            'email_address': 'invalid',
            'password': '1234567890',
        })
        assert_equal(res.status_code, 400)


class TestSession(BaseApplicationTest):
    def test_url_with_non_canonical_trailing_slash(self):
        response = self.client.get('/admin/')
        self.assertEquals(301, response.status_code)
        self.assertEquals("http://localhost/admin", response.location)


class TestLoginFormsNotAutofillable(BaseApplicationTest):

    def _forms_and_inputs_not_autofillable(
            self, url, expected_title
    ):
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        document = html.fromstring(response.get_data(as_text=True))

        page_title = document.xpath(
            '//div[@class="page-container"]//h1/text()')[0].strip()
        self.assertEqual(expected_title, page_title)

        forms = document.xpath('//div[@class="page-container"]//form')

        for form in forms:
            self.assertEqual("off", form.get('autocomplete'))
            non_hidden_inputs = form.xpath('//input[@type!="hidden"]')

            for input in non_hidden_inputs:
                self.assertEqual("off", input.get('autocomplete'))

    def test_login_form_and_inputs_not_autofillable(self):
        self._forms_and_inputs_not_autofillable(
            "/admin/login",
            "Administrator login"
        )
