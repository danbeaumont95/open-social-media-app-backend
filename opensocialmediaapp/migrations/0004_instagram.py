# Generated by Django 4.0.6 on 2022-07-23 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opensocialmediaapp', '0003_userlogintokens'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instagram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instagram_user_id', models.CharField(max_length=50, verbose_name='Instagram User ID')),
                ('access_token', models.CharField(max_length=700, verbose_name='Instagram Access Token')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='opensocialmediaapp.user')),
            ],
        ),
    ]