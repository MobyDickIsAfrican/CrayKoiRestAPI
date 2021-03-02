from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser

#creare Auth Token when a user is created: can i refresh token after some period
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=50, unique=True)

class Page(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pages");
    title = models.CharField(max_length=50, default=None)

class Component(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="components")
    secondary_state = models.JSONField()
    left = models.IntegerField()
    top = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    comp_id = models.CharField(max_length=250)
    parent = models.CharField(max_length=250, null=True)

    def getStyles(self):
        if self.parent is None:
            width = "100%"
            height = "100%"
            style = self.secondary_state
            style.update({"width": width, "height": height})
            return style
        try:
            parent = self.page.components.get(comp_id=self.parent)
            width = round((self.width / parent.width)*100)
            if width > 98:
                width = 100
            left = round((self.left / parent.left)*100)
            if left < 1:
                left = 0
            top = round((self.top / parent.top)*100)
            if top < 1:
                top = 0
            height = round((self.height / parent.height)*100)
            if height > 98:
                height = 100
            left = f'{left}%'
            width = f'{width}%'
            height = f'{height}%'
            top = f'{top}%'
            style = self.secondary_state
            style.update({"width": width, "height": height, "left": left, "top": top,})
            return style
        except Component.DoesNotExist:
            #perform some logging here
            raise TypeError
    def getData(self):
        data = {}
        data.update(self.secondary_state)
        data.update({"left": self.left, "top": self.top, "width": self.width, "height": self.height, "id": self.comp_id, "parent": self.parent})
        return data