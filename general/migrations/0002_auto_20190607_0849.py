# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shipping', '0001_initial'),
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagecenter',
            name='package',
            field=models.ForeignKey(to='shipping.ShippingPackage', null=True),
        ),
        migrations.AddField(
            model_name='messagecenter',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='addressbook',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='actionhistory',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
