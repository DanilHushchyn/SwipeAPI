from django.utils import timezone

from SwipeAPI.celery import app
from client.models import Subscription, Announcement, Promotion


@app.task(bind=True, ignore_result=True)
def subscriptions(self):
    subs = Subscription.objects.filter(auto_renewal=True, expiration_date__lt=timezone.now())
    subs_deactivate_list = Subscription.objects.filter(is_active=True, auto_renewal=False,
                                                       expiration_date__lt=timezone.now())
    for sub in subs:
        sub.expiration_date = timezone.now() + timezone.timedelta(days=30)
        sub.is_active = True
        sub.save()
        print('Renewed successfully')
    for sub in subs_deactivate_list:
        sub.is_active = False
        sub.save()
        print('Subscription deactivated successfully')


@app.task(bind=True, ignore_result=True)
def deactivate_promotions(self):
    promotions = Promotion.objects.filter(is_active=True, expiration_date__lt=timezone.now())
    if promotions.exists():
        promotions.update(is_active=False)
        print('Promotion deactivated successfully')
