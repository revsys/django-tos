from django.db.models.signals import post_syncdb
import tos.models

def create_default_tos_on_sync(sender, **kwargs): 
    """ Create a default TOS is an active one does not exist """ 

    try: 
        active_tos = tos.models.TermsOfService.objects.get(active=True) 
    except tos.models.TermsOfService.DoesNotExist: 
        new_tos = tos.models.TermsOfService.objects.create(
                    active = True, 
                    content = 'blank terms of service'
                )

post_syncdb.connect(create_default_tos_on_sync, sender=tos.models)
