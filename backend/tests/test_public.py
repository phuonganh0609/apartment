from .base import DomainTestCase
from buildings.models import Apartment
from regulations.models import Regulation


class PublicTests(DomainTestCase):
    def setUp(self):
        self.public = Apartment.objects.create(building=self.building, code='PUBLIC-UNIT', floor=2, area=40, rent=3000000, is_listed=True)

    def test_public_pages_without_login(self):
        for path in ('/', '/apartments/', '/about/', '/contact/', '/faq/', '/register/', '/accounts/password-reset/'):
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_listed_only_and_detail_private(self):
        page = self.client.get('/apartments/')
        self.assertContains(page, 'PUBLIC-UNIT')
        self.assertNotContains(page, self.contract.code)
        self.assertEqual(self.client.get(f'/apartments/{self.apartment.pk}/').status_code, 404)
        self.assertEqual(self.client.get(f'/apartments/{self.public.pk}/').status_code, 200)
        self.public.status = 'maintenance'
        self.public.save()
        self.assertEqual(self.client.get(f'/apartments/{self.public.pk}/').status_code, 404)

    def test_filters_and_invalid_price(self):
        self.assertNotContains(self.client.get('/apartments/', {'max_price': '100'}), 'PUBLIC-UNIT')
        self.assertEqual(self.client.get('/apartments/', {'min_price': 'NaN'}).status_code, 200)

    def test_faq_never_exposes_internal_rules(self):
        Regulation.objects.create(title='PRIVATE-RULE', content='Secret', document_type='Test')
        Regulation.objects.create(title='PUBLIC-RULE', content='Public', audience='public', document_type='Test')
        page = self.client.get('/faq/')
        self.assertContains(page, 'PUBLIC-RULE')
        self.assertNotContains(page, 'PRIVATE-RULE')
