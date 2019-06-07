# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('service_provider', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shipping', '0001_initial'),
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketerPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_channel', models.CharField(default=b'Card Payment', max_length=20, choices=[(b'Card Payment', b'Card Payment'), (b'Bank Deposit', b'Bank Deposit'), (b'Wire Transfer', b'Wire Transfer'), (b'PayPal', b'PayPal'), (b'SokoPay', b'SokoPay')])),
                ('purchase_type_2', models.CharField(default=b'Add', max_length=20, choices=[(b'Add', b'Add'), (b'Remove', b'Remove'), (b'Refund', b'Refund')])),
                ('purchase_type_3', models.CharField(max_length=20, null=True, blank=True)),
                ('amount', models.FloatField(max_length=15)),
                ('ref_no', models.CharField(max_length=50, null=True, blank=True)),
                ('payment_gateway_tranx_id', models.CharField(max_length=30, null=True, blank=True)),
                ('bank', models.CharField(max_length=50, null=True, blank=True)),
                ('teller_no', models.CharField(max_length=100, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved_by', models.CharField(max_length=100, null=True, blank=True)),
                ('status', models.CharField(default=b'Pending Approval', max_length=100)),
                ('message', models.CharField(max_length=100, null=True, blank=True)),
                ('local_package', models.ForeignKey(blank=True, to='shipping.DomesticPackage', null=True)),
                ('marketer', models.ForeignKey(blank=True, to='service_provider.MarketingMember', null=True)),
                ('package', models.ForeignKey(blank=True, to='shipping.ShippingPackage', null=True)),
                ('user', models.ForeignKey(to='general.UserAccount', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SokoPay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('purchase_type_1', models.CharField(default=b'Card Payment', max_length=20)),
                ('purchase_type_2', models.CharField(max_length=20, choices=[(b'Add', b'Add'), (b'Remove', b'Remove'), (b'Refund', b'Refund')])),
                ('amount', models.FloatField(default=0.0)),
                ('ref_no', models.CharField(max_length=50, null=True, blank=True)),
                ('payment_gateway_tranx_id', models.CharField(max_length=30, null=True, blank=True)),
                ('bank', models.CharField(max_length=50, choices=[('Wells Fargo', 'Wells Fargo'), ('Fidelity Bank', 'Fidelity Bank'), ('GTBank', 'GTBank'), ('UBA', 'UBA'), ('Zenith Bank', 'Zenith Bank'), ('Suntrust Bank', 'Suntrust Bank'), ('WebPay', 'WebPay'), ('Admin', 'Admin'), ('SokoPay', 'SokoPay'), ('Interswitch', 'Interswitch'), ('Bank Deposit', 'Bank Deposit'), ('PayStack', 'PayStack'), ('Flutterwave', 'Flutterwave'), ('PayPal', 'PayPal')])),
                ('teller_no', models.CharField(max_length=100, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'Pending Approval', max_length=100)),
                ('message', models.CharField(max_length=100, null=True, blank=True)),
                ('exchange_rate', models.FloatField(default=0)),
                ('user', models.ForeignKey(related_name='jejepay', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SubscriberPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.CharField(max_length=50, choices=[(b'ORIGIN WAREHOUSE', b'ORIGIN WAREHOUSE'), (b'DESTINATION WAREHOUSE', b'DESTINATION WAREHOUSE'), (b'SHIPPING', b'SHIPPING'), (b'CLEARING', b'CLEARING')])),
                ('amount', models.FloatField(max_length=50)),
                ('ref_no', models.CharField(max_length=30)),
                ('sokohali_fee', models.FloatField(max_length=50)),
                ('total_value', models.FloatField(max_length=15)),
                ('status', models.CharField(default=b'Pending Approval', max_length=100)),
                ('message', models.CharField(max_length=100, null=True, blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('chain', models.ForeignKey(blank=True, to='service_provider.ShippingChain', null=True)),
                ('owned_by', models.ForeignKey(related_name='owned_by', to='service_provider.Subscriber')),
                ('rented_by', models.ForeignKey(related_name='rentee', to='service_provider.Subscriber')),
            ],
        ),
    ]
