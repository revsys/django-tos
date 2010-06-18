from django.contrib.auth.models import User 
from django.contrib.flatpages import FlatPage
from django.core.exceptions import ValidationError 
from django.db import models
from django.utils.translation import ugettext_lazy as _ 

class BaseModel(models.Model):
    
    created     = models.DateTimeField(label=_('created'), auto_now_add=False, editable=False)
    modified    = models.DateTimeField(label=_('modified'), auto_now=False, editable=False)
    
    class Meta:
        abstract = True

class TermsOfService(BaseModel):
    
    flat_page   = models.ForeignKey(FlatPage, label=_('terms of service'), related_name='flatpage')
    active      = models.BooleanField(_('active'), _('Only one terms of service is allowed to be active'))
    
    class Meta: 
        ordering = ('created')
        verbose_name=_('Terms of Service')
        verbose_name_plural=_('Terms of Service')        

    def __unicode__(self):
        active = 'inactive'
        if self.active:
            active = 'active'            
        return '%s: %s' % (self.created, active)
        
    def save(self, *args, **kwargs): 
        """ Ensure we're being saved properly """ 

        self.objects.exclude(id=self.id).update(active=False)

        super(TermsOfService,self).save(*args, **kwargs)
        
class UserAgreement(BaseModel):
    
    terms_of_service = models.ForeignKey(FlatPage, label=_('terms of service'), related_name='terms')
    user            = models.ForeignKey(User related_name='user')
    
    def __unicode__(self):
        return self.terms_of_service