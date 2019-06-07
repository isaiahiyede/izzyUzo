# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('service_provider', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddInventory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_image', models.ImageField(upload_to=b'ZeAC/static/images/document/%Y%m%d', blank=True)),
                ('title', models.CharField(max_length=255, unique=True, null=True, blank=True)),
                ('description', models.CharField(max_length=2500, null=True, blank=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('colour', models.CharField(max_length=25, null=True, blank=True)),
                ('brand', models.CharField(max_length=100, null=True, blank=True)),
                ('size', models.PositiveIntegerField(default=0)),
                ('weight', models.FloatField(default=0.1)),
                ('unit', models.CharField(default=b'kg', max_length=5)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('sold', models.PositiveIntegerField(default=0)),
                ('specifications', models.CharField(max_length=2500, null=True, blank=True)),
                ('item_type', models.CharField(default=b'inventory', max_length=20)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('marketer', models.ForeignKey(blank=True, to='service_provider.MarketingMember', null=True)),
            ],
            options={
                'verbose_name_plural': 'Inventory',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('ordered', models.BooleanField(default=False)),
                ('client', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('item', models.ForeignKey(blank=True, to='shoppingCenter.AddInventory', null=True)),
                ('shipping_items', models.ForeignKey(blank=True, to='shipping.DomesticPackage', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cat_name', models.CharField(max_length=2500, null=True, blank=True)),
                ('marketer', models.ForeignKey(blank=True, to='service_provider.MarketingMember', null=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.CharField(max_length=12)),
                ('payable', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=20)),
                ('zip_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=20)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('item', models.ForeignKey(blank=True, to='shoppingCenter.AddInventory', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, null=True, blank=True)),
                ('desc', models.CharField(max_length=250, null=True, blank=True)),
                ('created_by', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'ShoppingCategory',
            },
        ),
        migrations.CreateModel(
            name='ShoppingItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_by', models.CharField(max_length=50, null=True, blank=True)),
                ('name', models.CharField(max_length=150, null=True, blank=True)),
                ('desc', models.CharField(max_length=250, null=True, blank=True)),
                ('weight', models.DecimalField(max_digits=15, decimal_places=1)),
                ('shoppingItem_image', models.ImageField(null=True, upload_to=b'shoppingItem_image/%Y/%m/%d', blank=True)),
                ('price', models.FloatField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, to='shoppingCenter.ShoppingCategory', null=True)),
            ],
            options={
                'ordering': ['created_on'],
                'verbose_name_plural': 'ShoppingItem',
            },
        ),
        migrations.CreateModel(
            name='ShoppingOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tracking_number', models.CharField(max_length=50, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('shipping_cost', models.FloatField(default=0)),
                ('user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'ShoppingOrder',
            },
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sub_cat_name', models.CharField(max_length=2500, null=True, blank=True)),
                ('sub_cat', models.ForeignKey(blank=True, to='shoppingCenter.Category', null=True)),
            ],
            options={
                'verbose_name_plural': 'SubCategories',
            },
        ),
        migrations.CreateModel(
            name='UserOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.CharField(max_length=12)),
                ('payable', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('intl_pkg', models.ForeignKey(blank=True, to='shipping.ShippingPackage', null=True)),
                ('local_pkg', models.ForeignKey(blank=True, to='shipping.DomesticPackage', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='shoppingitem',
            name='shopping_order',
            field=models.ForeignKey(blank=True, to='shoppingCenter.ShoppingOrder', null=True),
        ),
        migrations.AddField(
            model_name='addinventory',
            name='sub_sub_cat',
            field=models.ForeignKey(blank=True, to='shoppingCenter.SubCategory', null=True),
        ),
        migrations.AddField(
            model_name='addinventory',
            name='user_order',
            field=models.ForeignKey(blank=True, to='shoppingCenter.UserOrder', null=True),
        ),
    ]
