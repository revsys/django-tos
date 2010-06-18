from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError 
from django.db import models

from django.utils.translation import ugettext_lazy as _ 

class BaseModel(models.Model):
    
    created     = models.DateTimeField(auto_now_add=True, editable=False)
    modified    = models.DateTimeField(auto_now=True, editable=False)
    
    class Meta:
        abstract = True
        
class TermsOfServiceManager(models.Manager):
    
    def get_current_tos(self):
        return super(TermsOfServiceManager, self).get_query_set().get(active=True)
        

class TermsOfService(BaseModel):

    active      = models.BooleanField(_('active'), _('Only one terms of service is allowed to be active'))    
    content     = models.TextField(_('content'), blank=True)
    objects     = TermsOfServiceManager()
    
    class Meta: 
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name=_('Terms of Service')
        verbose_name_plural=_('Terms of Service')        

    def __unicode__(self):
        active = 'inactive'
        if self.active:
            active = 'active'            
        return '%s: %s' % (self.created, active)
        
    def save(self, *args, **kwargs): 
        """ Ensure we're being saved properly """ 

        if self.active:
            TermsOfService.objects.exclude(id=self.id).update(active=False)
            
        else:
            if not TermsOfService.objects.exclude(id=self.id).filter(active=True):
                raise ValidationError('One of the terms of service must be marked active')

        super(TermsOfService,self).save(*args, **kwargs)
        
class UserAgreement(BaseModel):
    
    terms_of_service = models.ForeignKey(TermsOfService, related_name='terms')
    user            = models.ForeignKey(User, related_name='user_agreement')
    
    def __unicode__(self):
        return '%s agreed to TOS: %s ' % (self.user.username, self.terms_of_service.__unicode__())
    
        
def has_user_agreed_latest_tos(user):
    if UserAgreement.objects.filter(terms_of_service=TermsOfService.objects.get_current_tos(),user=user):
        return True
    return False