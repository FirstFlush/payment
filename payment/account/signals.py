from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
# from payment.hmac_auth.models import HMACKey


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_hmac_key(sender, instance=None, created=False, **kwargs):
#     print('hiiiii dis a signal boii')
#     if created:
#         HMACKey.objects.create(vendor_id=instance)