from django.contrib.auth.models import User 
from django.contrib.flatpages.models import FlatPage
from django.test import TestCase 

from tos.models import TermsOfService, UserAgreement

class TestBasics(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'user1pass')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'user2pass')
        self.user3 = User.objects.create_user('user3', 'user3@example.com', 'user3pass')
        self.flatpage1 = FlatPage.objects.create(
                url                     = '/terms-of-service/',
                title                   = 'Terms of Service',
                content                 = 'lorem ipsum and stuff',
                enable_comments         = 0,
                registration_required   = False
        )
        
        self.tos1 = TermsOfService.objects.create(
            flat_page   = self.flatpage1,
            active      = True
        )
        self.tos2 = TermsOfService.objects.create(
            flat_page   = self.flatpage1,
            active      = False
        )        
        
    def test_terms_of_service(self):
        
        self.assertEquals(TermsOfService.objects.count(),2)
        
        # order is by -created
        latest = TermsOfService.objects.latest()
        self.assertFalse(latest.active)
        
        # setting a tos to True changes all others to False
        latest.active = True
        latest.save()
        first = TermsOfService.objects.get(id=self.tos1.id)
        self.assertFalse(first.active)
        
    def test_user_agreement(self):
        
        #agreement = UserAgreement.objects.create()