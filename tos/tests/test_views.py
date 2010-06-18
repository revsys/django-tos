from django.conf import settings
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError 
from django.core.urlresolvers import reverse 
from django.test import TestCase 

from tos.models import TermsOfService, UserAgreement, has_user_agreed_latest_tos

class TestViews(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'user1pass')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'user2pass')
        
        self.tos1 = TermsOfService.objects.create(
            content     = "first edition of the terms of service",
            active      = True
        )
        self.tos2 = TermsOfService.objects.create(
            content     = "second edition of the terms of service",
            active      = False
        )        
        
        self.login_url = getattr(settings, 'LOGIN_URL','/login/')
        
        UserAgreement.objects.create(
            terms_of_service    = self.tos1,
            user                = self.user1
            )

    def test_login(self):
        """ Make sure we didn't break the authentication system
            This assumes that login urls are named 'login'
        """
        
        self.assertTrue(has_user_agreed_latest_tos(self.user1))        
        login = self.client.login(username='user1', password='user1pass')
        self.failUnless(login, 'Could not log in')
        self.assertTrue(has_user_agreed_latest_tos(self.user1))                
        
    def test_need_agreement(self):
        """ user2 tries to login and then has to go and agree to terms"""
        
        self.assertFalse(has_user_agreed_latest_tos(self.user2))        
        
        response = self.client.post(self.login_url, dict(username='user2', password='user2pass'))
        self.assertContains(response, "first edition of the terms of service")
        
        self.assertFalse(has_user_agreed_latest_tos(self.user2))        
        
    def test_reject_agreement(self):
        
        self.assertFalse(has_user_agreed_latest_tos(self.user2))        
        
        response = self.client.post(self.login_url, dict(username='user2', password='user2pass'))
        self.assertContains(response, "first edition of the terms of service")
        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept':'reject'})
        self.assertContains(response, "You cannot login without agreeing to the terms of this site.")
        
        self.assertFalse(has_user_agreed_latest_tos(self.user2))        
        
    def test_accept_agreement(self):

        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        
        response = self.client.post(self.login_url, dict(username='user2', password='user2pass'))
        self.assertContains(response, "first edition of the terms of service")
        self.assertFalse(has_user_agreed_latest_tos(self.user2))        
        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept':'accept'})
        
        self.assertTrue(has_user_agreed_latest_tos(self.user2))
        
    def test_bump_new_agreement(self):
        
        # Change the tos
        self.tos2.active = True
        self.tos2.save()
        
        # is user1 agreed now?
        self.assertFalse(has_user_agreed_latest_tos(self.user1))                
        
        # user1 agrees again
        response = self.client.post(self.login_url, dict(username='user1', password='user1pass'))
        self.assertContains(response, "second edition of the terms of service")
        self.assertFalse(has_user_agreed_latest_tos(self.user2))        
        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept':'accept'})
        
        self.assertTrue(has_user_agreed_latest_tos(self.user1))
        