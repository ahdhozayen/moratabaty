from django.db import models

class Country(models.Model):
    class Meta:
        verbose_name_plural = 'Countries'

    name = models.CharField(max_length=255, unique=True)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name

class Nationality(models.Model):
    class Meta:
        verbose_name_plural = 'Nationalities'

    country_id = models.OneToOneField('countries.Country', on_delete=models.PROTECT)
    name = models.CharField(max_length=255)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name

class City(models.Model):
    class Meta:
        verbose_name_plural = 'Cities'
        unique_together = (('country_id','name'))

    country_id = models.ForeignKey('countries.Country', related_name='cities', on_delete=models.PROTECT)
    name = models.CharField(max_length=255)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.country_id.name
