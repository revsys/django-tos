from django.contrib.auth.models import User 
from django.contrib.flatpages.models import FlatPage
from django.core.exceptions import ValidationError 
from django.db import models
from django.utils.translation import ugettext_lazy as _ 

class BaseModel(models.Model):
    
    created     = models.DateTimeField(auto_now_add=True, editable=False)
    modified    = models.DateTimeField(auto_now=True, editable=False)
    
    class Meta:
        abstract = True

class TermsOfService(BaseModel):
    
    flat_page   = models.ForeignKey(FlatPage, related_name='flatpage')
    active      = models.BooleanField(_('active'), _('Only one terms of service is allowed to be active'))
    
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

        super(TermsOfService,self).save(*args, **kwargs)
        
class UserAgreement(BaseModel):
    
    terms_of_service = models.ForeignKey(TermsOfService, related_name='terms')
    user            = models.ForeignKey(User, related_name='user_agreement')
    
    def __unicode__(self):
        return '%s agreed to TOS: %s ' % (self.user.username, self.terms_of_service.__unicode__())