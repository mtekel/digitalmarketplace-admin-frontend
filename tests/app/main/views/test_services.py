try:
    from urlparse import urlsplit
    from StringIO import StringIO
except ImportError:
    from urllib.parse import urlsplit
    from io import BytesIO as StringIO
import mock

from dmutils.apiclient import HTTPError, REQUEST_ERROR_MESSAGE
from ...helpers import LoggedInApplicationTest


class TestServiceView(LoggedInApplicationTest):
    @mock.patch('app.main.views.services.data_api_client')
    def test_service_response(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {}}
        response = self.client.get('/admin/services/1')

        data_api_client.get_service.assert_called_with('1')

        self.assertEquals(200, response.status_code)

    @mock.patch('app.main.views.services.data_api_client')
    def test_service_view_with_no_features_or_benefits(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {}}
        response = self.client.get('/admin/services/1')

        data_api_client.get_service.assert_called_with('1')

        self.assertEquals(200, response.status_code)

    @mock.patch('app.main.views.services.data_api_client')
    def test_redirect_with_flash_for_api_client_404(self, data_api_client):
        response = mock.Mock()
        response.status_code = 404
        data_api_client.get_service.side_effect = HTTPError(response)

        response1 = self.client.get('/admin/services/1')
        self.assertEquals(302, response1.status_code)
        self.assertEquals(response1.location, 'http://localhost/admin')
        response2 = self.client.get(response1.location)
        self.assertIn(b'Error trying to retrieve service with ID: 1',
                      response2.data)

    @mock.patch('app.main.views.services.data_api_client')
    def test_independence_of_viewing_services(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'lot': 'SCS'
        }}
        response = self.client.get('/admin/services/1')
        self.assertIn(b'Termination cost', response.data)

        data_api_client.get_service.return_value = {'services': {
            'lot': 'SaaS'
        }}
        response = self.client.get('/admin/services/1')
        self.assertNotIn(b'Termination cost', response.data)

        data_api_client.get_service.return_value = {'services': {
            'lot': 'SCS'
        }}
        response = self.client.get('/admin/services/1')
        self.assertIn(b'Termination cost', response.data)


class TestServiceEdit(LoggedInApplicationTest):
    @mock.patch('app.main.views.services.data_api_client')
    def test_service_edit_documents_get_response(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {}}
        response = self.client.get('/admin/services/1/edit/documents')

        data_api_client.get_service.assert_called_with('1')

        self.assertEquals(200, response.status_code)

    @mock.patch('app.main.views.services.data_api_client')
    def test_service_edit_documents_empty_post(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'id': 1,
            'supplierId': 2
        }}
        response = self.client.post(
            '/admin/services/1/edit/documents',
            data={}
        )

        data_api_client.get_service.assert_called_with('1')
        self.assertFalse(data_api_client.update_service.called)

        self.assertEquals(302, response.status_code)
        self.assertEquals(
            "/admin/services/1", urlsplit(response.location).path
        )

    @mock.patch('app.main.views.services.data_api_client')
    def test_service_edit_documents_post(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'id': 1,
            'supplierId': 2,
            'pricingDocumentURL': "http://assets/documents/1/2-pricing.pdf",
            'serviceDefinitionDocumentURL': "http://assets/documents/1/2-service-definition.pdf",  # noqa
            'termsAndConditionsDocumentURL': "http://assets/documents/1/2-terms-and-conditions.pdf",  # noqa
            'sfiaRateDocumentURL': None
        }}
        response = self.client.post(
            '/admin/services/1/edit/documents',
            data={
                'serviceDefinitionDocumentURL': (StringIO(), ''),
                'pricingDocumentURL': (StringIO(b"doc"), 'test.pdf'),
                'sfiaRateDocumentURL': (StringIO(b"doc"), 'test.pdf'),
                'termsAndConditionsDocumentURL': (StringIO(b''), ''),
            }
        )

        data_api_client.get_service.assert_called_with('1')
        data_api_client.update_service.assert_called_with(1, {
            'pricingDocumentURL': 'https://assets.test.digitalmarketplace.service.gov.uk/documents/2/1-pricing-document-2015-01-01-1200.pdf',  # noqa
            'sfiaRateDocumentURL': 'https://assets.test.digitalmarketplace.service.gov.uk/documents/2/1-sfia-rate-card-2015-01-01-1200.pdf',  # noqa
        }, 'test@example.com', 'admin app')

        self.assertEquals(302, response.status_code)

    @mock.patch("app.main.views.services.data_api_client")
    def test_service_edit_documents_post_with_validation_errors(
            self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'id': 1,
            'supplierId': 2,
            'lot': 'SCS',
            'serviceDefinitionDocumentURL': "http://assets/documents/1/2-service-definition.pdf",  # noqa
            'pricingDocumentURL': "http://assets/documents/1/2-pricing.pdf",
            'sfiaRateDocumentURL': None
        }}
        response = self.client.post(
            '/admin/services/1/edit/documents',
            data={
                'serviceDefinitionDocumentURL': (StringIO(), ''),
                'pricingDocumentURL': (StringIO(b"doc"), 'test.pdf'),
                'sfiaRateDocumentURL': (StringIO(b"doc"), 'test.txt'),
                'termsAndConditionsDocumentURL': (StringIO(), 'test.pdf'),
            }
        )

        data_api_client.get_service.assert_called_with('1')
        data_api_client.update_service.assert_called_with(1, {
            'pricingDocumentURL': 'https://assets.test.digitalmarketplace.service.gov.uk/documents/2/1-pricing-document-2015-01-01-1200.pdf',  # noqa
        }, 'test@example.com', 'admin app')

        self.assertIn(b'Your document is not in an open format', response.data)
        self.assertIn(b'This question requires an answer', response.data)
        self.assertEquals(200, response.status_code)

    @mock.patch('app.main.views.services.data_api_client')
    def test_service_edit_with_one_service_feature(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'id': 1,
            'supplierId': 2,
            'lot': 'IaaS',
            'serviceFeatures': [
                "foo",
            ],
            'serviceBenefits': [
                "foo",
            ],
        }}
        response = self.client.get(
            '/admin/services/1/edit/features_and_benefits'
        )
        self.assertEquals(200, response.status_code)
        self.assertIn(
            b'id="serviceFeatures-item-1" class="text-box" value="foo"',
            response.data)
        self.assertIn(
            b'id="serviceFeatures-item-2" class="text-box" value=""',
            response.data)
        response = self.client.post(
            '/admin/services/1/edit/features_and_benefits',
            data={
                'serviceFeatures': 'foo',
                'serviceBenefits': 'foo',
            }
        )
        data_api_client.update_service.assert_called_with(1, {
            'serviceFeatures': ['foo'],
            'serviceBenefits': ['foo'],
        }, 'test@example.com', 'admin app')
        self.assertEquals(response.status_code, 302)

    @mock.patch('app.main.views.services.data_api_client')
    def test_service_edit_with_no_features_or_benefits(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'lot': 'SaaS'
        }}
        response = self.client.get(
            '/admin/services/1/edit/features_and_benefits')

        data_api_client.get_service.assert_called_with('1')

        self.assertEquals(200, response.status_code)
        self.assertIn(
            b'id="serviceFeatures-item-1" class="text-box" value=""',
            response.data)

    @mock.patch('app.main.views.services.data_api_client')
    def test_service_edit_when_API_returns_error(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'id': 1,
            'supplierId': 2,
            'pricingDocumentURL': "http://assets/documents/1/2-pricing.pdf",
            'sfiaRateDocumentURL': None
        }}
        error = mock.Mock()
        data_api_client.update_service.side_effect = HTTPError(error)

        response = self.client.post(
            '/admin/services/1/edit/documents',
            data={
                'pricingDocumentURL': (StringIO(b"doc"), 'test.pdf'),
                'sfiaRateDocumentURL': (StringIO(b"doc"), 'test.txt'),
                'termsAndConditionsDocumentURL': (StringIO(), 'test.pdf'),
            }
        )
        self.assertIn(REQUEST_ERROR_MESSAGE.encode('utf-8'), response.data)


class TestServiceStatusUpdate(LoggedInApplicationTest):
    @mock.patch('app.main.views.services.data_api_client')
    def test_cannot_make_removed_service_public(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'id': 1,
            'supplierId': 2,
            'status': 'disabled'
        }}
        response = self.client.get('/admin/services/1')
        self.assertIn(b'<input type="radio" name="service_status" id="service_status_disabled" value="removed" checked="checked" />', response.data)  # noqa
        self.assertIn(b'<input type="radio" name="service_status" id="service_status_private" value="private"  />', response.data)  # noqa
        self.assertNotIn(b'<input type="radio" name="service_status" id="service_status_published" value="public"  />', response.data)  # noqa

    @mock.patch('app.main.views.services.data_api_client')
    def test_can_make_private_service_public_or_removed(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'id': 1,
            'supplierId': 2,
            'status': 'enabled'
        }}
        response = self.client.get('/admin/services/1')
        self.assertIn(b'<input type="radio" name="service_status" id="service_status_disabled" value="removed"  />', response.data)  # noqa
        self.assertIn(b'<input type="radio" name="service_status" id="service_status_private" value="private" checked="checked" />', response.data)  # noqa
        self.assertIn(b'<input type="radio" name="service_status" id="service_status_published" value="public"  />', response.data)  # noqa

    @mock.patch('app.main.views.services.data_api_client')
    def test_can_make_public_service_private_or_removed(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {
            'id': 1,
            'supplierId': 2,
            'status': 'published'
        }}
        response = self.client.get('/admin/services/1')
        self.assertIn(b'<input type="radio" name="service_status" id="service_status_disabled" value="removed"  />', response.data)  # noqa
        self.assertIn(b'<input type="radio" name="service_status" id="service_status_private" value="private"  />', response.data)  # noqa
        self.assertIn(b'<input type="radio" name="service_status" id="service_status_published" value="public" checked="checked" />', response.data)  # noqa

    @mock.patch('app.main.views.services.data_api_client')
    def test_status_update_to_removed(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {}}
        response1 = self.client.post('/admin/services/status/1',
                                     data={'service_status': 'removed'})
        data_api_client.update_service_status.assert_called_with(
            '1', 'disabled', 'Digital Marketplace admin user',
            "Status changed to 'disabled'")
        self.assertEquals(302, response1.status_code)
        self.assertEquals(response1.location,
                          'http://localhost/admin/services/1')
        response2 = self.client.get(response1.location)
        self.assertIn(b'Service status has been updated to: Removed',
                      response2.data)

    @mock.patch('app.main.views.services.data_api_client')
    def test_status_update_to_private(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {}}
        response1 = self.client.post('/admin/services/status/1',
                                     data={'service_status': 'private'})
        data_api_client.update_service_status.assert_called_with(
            '1', 'enabled', 'Digital Marketplace admin user',
            "Status changed to 'enabled'")
        self.assertEquals(302, response1.status_code)
        self.assertEquals(response1.location,
                          'http://localhost/admin/services/1')
        response2 = self.client.get(response1.location)
        self.assertIn(b'Service status has been updated to: Private',
                      response2.data)

    @mock.patch('app.main.views.services.data_api_client')
    def test_status_update_to_published(self, data_api_client):
        data_api_client.get_service.return_value = {'services': {}}
        response1 = self.client.post('/admin/services/status/1',
                                     data={'service_status': 'public'})
        data_api_client.update_service_status.assert_called_with(
            '1', 'published', 'Digital Marketplace admin user',
            "Status changed to 'published'")
        self.assertEquals(302, response1.status_code)
        self.assertEquals(response1.location,
                          'http://localhost/admin/services/1')
        response2 = self.client.get(response1.location)
        self.assertIn(b'Service status has been updated to: Public',
                      response2.data)

    @mock.patch('app.main.views.services.data_api_client')
    def test_bad_status_gives_error_message(self, data_api_client):
        response1 = self.client.post('/admin/services/status/1',
                                     data={'service_status': 'suspended'})
        self.assertEquals(302, response1.status_code)
        self.assertEquals(response1.location,
                          'http://localhost/admin/services/1')
        response2 = self.client.get(response1.location)
        self.assertIn(b"Not a valid status: 'suspended'",
                      response2.data)

    def test_services_with_missing_id(self):
        response = self.client.get('/admin/services')
        self.assertEquals(404, response.status_code)
