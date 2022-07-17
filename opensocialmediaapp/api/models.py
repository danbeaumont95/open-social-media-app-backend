from django.db import models

# Create your models here.


class User(models.Model):
    first_name = models.CharField('First Name', max_length=60)
    last_name = models.CharField('Last Name', max_length=60)
    email = models.EmailField('Email', max_length=100)
    password = models.CharField('Password', max_length=30)

    # Below allows this model to appear in admin page
    def __str__(self):
        return self.first_name + ' ' + self.last_name


class LinkedAccounts(models.Model):
    website = models.CharField('Website', max_length=60)
    user = models.ManyToManyField(User, blank=True)
