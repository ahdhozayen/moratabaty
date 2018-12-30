from django.db import models

class Requester(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    done = models.BooleanField(default=False)

    def clean(self):
        self.name = self.name.capitalize()
        self.email = self.email.lower()
    
    def __str__(self):
        return self.email
