# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('currency', models.CharField(max_length=20, choices=[(b'naira', b'=N='), (b'pounds', b'\xc2\xa3'), (b'dollars', b'$')])),
                ('dollar_exchange_rate', models.FloatField(default=200)),
            ],
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_name', models.CharField(max_length=50)),
                ('account_no', models.CharField(max_length=50)),
                ('bank', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=300, null=True, blank=True)),
                ('currency', models.CharField(max_length=50, choices=[(b'Nigerian Naira', b'Naira (=N=)'), (b'British Pounds', b'Pounds (\xc2\xa3)'), (b'American Dollars', b'Dollars ($)')])),
                ('routing_no', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClearingPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=50)),
                ('price', models.FloatField(default=0, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='ConfiguredPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('log', models.ImageField(upload_to=b'configured_payments/%d/%m/%y/')),
            ],
        ),
        migrations.CreateModel(
            name='CustomClearingAgent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75, null=True, blank=True)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=75)),
                ('state', models.CharField(max_length=125)),
                ('country', models.CharField(max_length=125)),
                ('phone_number', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('key_official_name', models.CharField(max_length=50)),
                ('key_official_address', models.TextField(null=True)),
                ('iac_license', models.FileField(null=True, upload_to=b'warehouse-member/IAC-License', blank=True)),
                ('incorportation_doc', models.FileField(null=True, upload_to=b'warehouse-member/Incorportation-Doc', blank=True)),
                ('key_official_passport_id', models.FileField(null=True, upload_to=b'warehouse-member/Key-Official-Passport-ID', blank=True)),
                ('key_official_photo', models.FileField(null=True, upload_to=b'warehouse-member/Key-Official-Photo', blank=True)),
                ('contract_doc', models.FileField(null=True, upload_to=b'warehouse-member/Contract-Doc', blank=True)),
                ('registration_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('process_charge_per_kg', models.FloatField(default=0, max_length=10)),
                ('storage_charge_per_day', models.FloatField(default=0, max_length=10)),
                ('working_hrs_start', models.CharField(max_length=5)),
                ('working_hrs_end', models.CharField(max_length=5)),
                ('auto_subscriber_approval', models.BooleanField(default=False)),
                ('publish_reviews', models.BooleanField(default=False)),
                ('about_service', models.TextField()),
                ('offered_for_rent', models.BooleanField(default=True)),
                ('activated_for_offerer', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('clearing_per_kg', models.FloatField(default=0, max_length=10)),
                ('quote_per_cosignment', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Custom Clearing Agent',
            },
        ),
        migrations.CreateModel(
            name='FixedShipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
                ('unit_price_D', models.FloatField(default=0)),
                ('extra_charges', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='LocalDistributionMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('courier_name', models.CharField(max_length=50, null=True)),
                ('active', models.BooleanField(default=False)),
                ('has_api', models.BooleanField(default=False)),
                ('has_configured_rates', models.BooleanField(default=False)),
                ('country', models.ForeignKey(blank=True, to='service_provider.AvailableCountry', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocalDistributorLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75, null=True, blank=True)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=75)),
                ('state', models.CharField(max_length=125)),
                ('country', models.CharField(max_length=125)),
                ('phone_number', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('pickup_available', models.BooleanField(default=False)),
                ('drop_off_available', models.BooleanField(default=False)),
                ('offered_location', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LocalDistributorPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight_unit', models.CharField(max_length=5, choices=[(b'kg', b'kilogram(kg)'), (b'lbs', b'pounds(lb)')])),
                ('weight', models.FloatField(default=1)),
                ('price', models.FloatField(default=1)),
                ('mark_up_value', models.FloatField(default=30)),
            ],
            options={
                'ordering': ['-weight'],
            },
        ),
        migrations.CreateModel(
            name='LocalDistributorRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('courier', models.ForeignKey(blank=True, to='service_provider.LocalDistributionMember', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MarketingMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=75)),
                ('state', models.CharField(max_length=125)),
                ('country', models.CharField(max_length=125)),
                ('phone_number', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('active', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254)),
                ('subdomain_name', models.CharField(max_length=30, null=True, blank=True)),
                ('storefront', models.BooleanField(default=False, verbose_name=b'Do you want a Customisable Storefront?')),
                ('storefront_name', models.CharField(help_text=b'***Example: storefront_name.sokohali.com***', max_length=50)),
                ('storefront_color', models.CharField(default=b'blue', max_length=20, choices=[(b'#0b71b9', b'Blue'), (b'#ffd014', b'Yellow'), (b'#3ab54a', b'Green')])),
                ('logo', models.ImageField(upload_to=b'marketer_logos/%Y/%m/%d', verbose_name=b'Storefront Logo')),
                ('ico', models.ImageField(upload_to=b'marketer_icons/%Y/%m/%d', verbose_name=b'Storefront Icon')),
                ('package_pickup', models.BooleanField(default=False)),
                ('package_dropoff', models.BooleanField(default=False)),
                ('store', models.BooleanField(default=False)),
                ('bank_deposit', models.BooleanField(default=False, verbose_name=b'Bank Deposit')),
                ('card_payment', models.BooleanField(default=False, verbose_name=b'Debit cards: Visa, Mastercard, Verve')),
                ('stripe', models.BooleanField(default=False, verbose_name=b'Stripe')),
                ('paypal', models.BooleanField(default=False, verbose_name=b'PayPal')),
                ('facebook_link', models.CharField(max_length=100, null=True, blank=True)),
                ('twitter_link', models.CharField(max_length=100, null=True, blank=True)),
                ('googleplus_link', models.CharField(max_length=100, null=True, blank=True)),
                ('linkedin_link', models.CharField(max_length=100, null=True, blank=True)),
                ('fax_number', models.CharField(max_length=50, null=True, blank=True)),
                ('domestic_shipping', models.BooleanField(default=False)),
                ('email_text', models.TextField(null=True, blank=True)),
                ('faq', models.TextField(null=True, blank=True)),
                ('terms_and_cond', models.TextField(null=True, blank=True)),
                ('random_code', models.CharField(max_length=5, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OfferedServiceRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service_name', models.CharField(max_length=50, choices=[(b'ORIGIN WAREHOUSE', b'ORIGIN WAREHOUSE'), (b'DESTINATION WAREHOUSE', b'DESTINATION WAREHOUSE'), (b'SHIPPING', b'SHIPPING'), (b'CLEARING', b'CLEARING')])),
                ('charge', models.FloatField(default=0)),
                ('extra_charges', models.FloatField(default=0, null=True, blank=True)),
                ('extra_charges_info', models.CharField(max_length=250, null=True, blank=True)),
                ('unit', models.CharField(max_length=50, choices=[(b'kg', b'kilogram(kg)'), (b'lbs', b'pounds(lb)')])),
            ],
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=250, null=True, blank=True)),
                ('price_range', models.FloatField(default=0)),
                ('image', models.ImageField(null=True, upload_to=b'image-of-box/%Y/%m/%d', blank=True)),
                ('currency', models.CharField(max_length=50, choices=[(b'Nigerian Naira', b'Naira (=N=)'), (b'British Pounds', b'Pounds (\xc2\xa3)'), (b'American Dollars', b'Dollars ($)')])),
                ('dimensions', models.CharField(max_length=150, null=True, blank=True)),
                ('marketer', models.ForeignKey(blank=True, to='service_provider.MarketingMember', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ShippingChain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('origin', models.CharField(max_length=100, null=True, blank=True)),
                ('destination', models.CharField(max_length=100, null=True, blank=True)),
                ('complete', models.BooleanField(default=False)),
                ('air', models.BooleanField(default=False)),
                ('air_delivery_time', models.CharField(max_length=50, null=True, blank=True)),
                ('sea', models.BooleanField(default=False)),
                ('sea_delivery_time', models.CharField(max_length=50, null=True, blank=True)),
                ('ground', models.BooleanField(default=False)),
                ('ground_delivery_time', models.CharField(max_length=50, null=True, blank=True)),
                ('express', models.BooleanField(default=False)),
                ('express_delivery_time', models.CharField(max_length=50, null=True, blank=True)),
                ('clearing_agent', models.ForeignKey(related_name='origin_clearing_agent', blank=True, to='service_provider.CustomClearingAgent', null=True)),
                ('destination_distributor', models.ForeignKey(related_name='destination_distributor', blank=True, to='service_provider.LocalDistributionMember', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShippingMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75, null=True, blank=True)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=75)),
                ('state', models.CharField(max_length=125)),
                ('country', models.CharField(max_length=125)),
                ('phone_number', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('key_official_name', models.CharField(max_length=50)),
                ('key_official_address', models.TextField(null=True)),
                ('iac_license', models.FileField(null=True, upload_to=b'warehouse-member/IAC-License', blank=True)),
                ('incorportation_doc', models.FileField(null=True, upload_to=b'warehouse-member/Incorportation-Doc', blank=True)),
                ('key_official_passport_id', models.FileField(null=True, upload_to=b'warehouse-member/Key-Official-Passport-ID', blank=True)),
                ('key_official_photo', models.FileField(null=True, upload_to=b'warehouse-member/Key-Official-Photo', blank=True)),
                ('contract_doc', models.FileField(null=True, upload_to=b'warehouse-member/Contract-Doc', blank=True)),
                ('registration_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('process_charge_per_kg', models.FloatField(default=0, max_length=10)),
                ('storage_charge_per_day', models.FloatField(default=0, max_length=10)),
                ('working_hrs_start', models.CharField(max_length=5)),
                ('working_hrs_end', models.CharField(max_length=5)),
                ('auto_subscriber_approval', models.BooleanField(default=False)),
                ('publish_reviews', models.BooleanField(default=False)),
                ('about_service', models.TextField()),
                ('offered_for_rent', models.BooleanField(default=True)),
                ('activated_for_offerer', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShippingMemberRoute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('origin', models.CharField(max_length=50)),
                ('destination', models.CharField(max_length=50)),
                ('rate', models.FloatField(default=0, max_length=10)),
                ('shipping_method', models.CharField(default=b'Air Freight', max_length=20, choices=[(b'air_freight', b'Air Freight'), (b'sea_freight', b'Sea Freight'), (b'express_air', b'Express Air')])),
                ('shipper', models.ForeignKey(to='service_provider.ShippingMember')),
            ],
        ),
        migrations.CreateModel(
            name='ShippingRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shipping_method', models.CharField(max_length=30, choices=[(b'air', b'Air'), (b'sea', b'Sea'), (b'express', b'Express')])),
                ('weight_unit', models.CharField(default=b'lbs', max_length=5)),
                ('from_range', models.FloatField(default=1.0, verbose_name=b'From Weight')),
                ('to_range', models.FloatField(default=1.0, verbose_name=b'To Weight')),
                ('rate_D', models.FloatField(default=1, verbose_name=b'Rate ($/lbs)')),
                ('shipping_chain', models.ForeignKey(verbose_name=b'Delivery Route', to='service_provider.ShippingChain')),
            ],
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=75)),
                ('state', models.CharField(max_length=125)),
                ('country', models.CharField(max_length=125)),
                ('phone_number', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('photo_id', models.ImageField(null=True, upload_to=b'subscriber-photo-id/%Y/%m/%d', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TariffZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_city', models.CharField(max_length=100, null=True, blank=True)),
                ('to_city', models.CharField(max_length=100, null=True, blank=True)),
                ('from_state', models.CharField(max_length=100, null=True, blank=True)),
                ('to_state', models.CharField(max_length=100, null=True, blank=True)),
                ('country', models.CharField(max_length=100, null=True, blank=True)),
                ('region', models.ForeignKey(blank=True, to='service_provider.LocalDistributorRegion', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WarehouseLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75, null=True, blank=True)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=75)),
                ('state', models.CharField(max_length=125)),
                ('country', models.CharField(max_length=125)),
                ('phone_number', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('location_prefix', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WarehouseMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key_official_name', models.CharField(max_length=50)),
                ('key_official_address', models.TextField(null=True)),
                ('iac_license', models.FileField(null=True, upload_to=b'warehouse-member/IAC-License', blank=True)),
                ('incorportation_doc', models.FileField(null=True, upload_to=b'warehouse-member/Incorportation-Doc', blank=True)),
                ('key_official_passport_id', models.FileField(null=True, upload_to=b'warehouse-member/Key-Official-Passport-ID', blank=True)),
                ('key_official_photo', models.FileField(null=True, upload_to=b'warehouse-member/Key-Official-Photo', blank=True)),
                ('contract_doc', models.FileField(null=True, upload_to=b'warehouse-member/Contract-Doc', blank=True)),
                ('registration_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('process_charge_per_kg', models.FloatField(default=0, max_length=10)),
                ('storage_charge_per_day', models.FloatField(default=0, max_length=10)),
                ('working_hrs_start', models.CharField(max_length=5)),
                ('working_hrs_end', models.CharField(max_length=5)),
                ('auto_subscriber_approval', models.BooleanField(default=False)),
                ('publish_reviews', models.BooleanField(default=False)),
                ('about_service', models.TextField()),
                ('offered_for_rent', models.BooleanField(default=True)),
                ('activated_for_offerer', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('warehouse_size', models.CharField(max_length=10)),
                ('country', models.CharField(max_length=100, null=True, blank=True)),
                ('company_name', models.CharField(max_length=50)),
                ('company_name_slug', models.SlugField(editable=False)),
                ('logo', models.ImageField(null=True, upload_to=b'warehouse-member/Logo', blank=True)),
                ('offered_by', models.OneToOneField(null=True, blank=True, to='service_provider.Subscriber')),
            ],
            options={
                'ordering': ['-registration_time'],
                'verbose_name_plural': 'Warehouse Member',
            },
        ),
        migrations.AddField(
            model_name='warehouselocation',
            name='owned_by',
            field=models.ForeignKey(to='service_provider.WarehouseMember'),
        ),
        migrations.AddField(
            model_name='shippingmember',
            name='offered_by',
            field=models.OneToOneField(null=True, blank=True, to='service_provider.Subscriber'),
        ),
        migrations.AddField(
            model_name='shippingchain',
            name='destination_warehouse',
            field=models.ForeignKey(related_name='destination_warehouse', blank=True, to='service_provider.WarehouseMember', null=True),
        ),
        migrations.AddField(
            model_name='shippingchain',
            name='origin_distributor',
            field=models.ForeignKey(related_name='origin_distributor', blank=True, to='service_provider.LocalDistributionMember', null=True),
        ),
        migrations.AddField(
            model_name='shippingchain',
            name='origin_warehouse',
            field=models.ForeignKey(related_name='origin_warehouse', blank=True, to='service_provider.WarehouseMember', null=True),
        ),
        migrations.AddField(
            model_name='shippingchain',
            name='shipper',
            field=models.ForeignKey(related_name='origin_shipper', blank=True, to='service_provider.ShippingMember', null=True),
        ),
        migrations.AddField(
            model_name='shippingchain',
            name='subscriber',
            field=models.ForeignKey(blank=True, to='service_provider.Subscriber', null=True),
        ),
        migrations.AddField(
            model_name='offeredservicerate',
            name='chain',
            field=models.ForeignKey(blank=True, to='service_provider.ShippingChain', null=True),
        ),
        migrations.AddField(
            model_name='offeredservicerate',
            name='offered_by',
            field=models.ForeignKey(related_name='offered_by', to='service_provider.Subscriber'),
        ),
        migrations.AddField(
            model_name='offeredservicerate',
            name='rented_by',
            field=models.ForeignKey(related_name='rented_by', to='service_provider.Subscriber'),
        ),
        migrations.AddField(
            model_name='marketingmember',
            name='subscriber',
            field=models.OneToOneField(null=True, blank=True, to='service_provider.Subscriber'),
        ),
        migrations.AddField(
            model_name='localdistributorprice',
            name='region',
            field=models.ForeignKey(blank=True, to='service_provider.LocalDistributorRegion', null=True),
        ),
        migrations.AddField(
            model_name='localdistributorlocation',
            name='region',
            field=models.ForeignKey(blank=True, to='service_provider.LocalDistributorRegion', null=True),
        ),
        migrations.AddField(
            model_name='localdistributionmember',
            name='marketing_member',
            field=models.ForeignKey(blank=True, to='service_provider.MarketingMember', null=True),
        ),
        migrations.AddField(
            model_name='fixedshipment',
            name='chain',
            field=models.ForeignKey(blank=True, to='service_provider.ShippingChain', null=True),
        ),
        migrations.AddField(
            model_name='fixedshipment',
            name='subscriber',
            field=models.ForeignKey(blank=True, to='service_provider.Subscriber', null=True),
        ),
        migrations.AddField(
            model_name='customclearingagent',
            name='offered_by',
            field=models.OneToOneField(null=True, blank=True, to='service_provider.Subscriber'),
        ),
        migrations.AddField(
            model_name='clearingprice',
            name='clearing_agent',
            field=models.ForeignKey(to='service_provider.CustomClearingAgent'),
        ),
        migrations.AddField(
            model_name='bankaccount',
            name='marketing_member',
            field=models.ForeignKey(blank=True, to='service_provider.MarketingMember', null=True),
        ),
        migrations.AddField(
            model_name='availablecountry',
            name='payment_options',
            field=models.ManyToManyField(to='service_provider.ConfiguredPayment', blank=True),
        ),
    ]
