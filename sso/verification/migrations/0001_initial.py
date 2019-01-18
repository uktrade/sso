# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-18 19:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.crypto
import django_cryptography.fields
import django_extensions.db.fields
import functools


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, null=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True, verbose_name='modified')),
                ('code', django_cryptography.fields.encrypt(models.CharField(default=functools.partial(django.utils.crypto.get_random_string, *(), **{'length': 16}), max_length=128))),
                ('user_id', models.IntegerField(null=True)),
                ('is_verified', models.BooleanField(default=False, help_text='Designates whether this user has verified the code', verbose_name='verified')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
