# Generated by Django 2.2.13 on 2020-08-10 07:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_auto_20200716_1625'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonCompleted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, null=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True, verbose_name='modified')),
                ('lesson_page', models.CharField(max_length=255)),
                ('lesson', models.IntegerField()),
                ('topic', models.IntegerField()),
                ('module', models.IntegerField()),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'lesson')},
            },
        ),
    ]