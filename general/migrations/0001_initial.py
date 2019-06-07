# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('service_provider', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('obj_id', models.IntegerField(default=0)),
                ('obj_model_name', models.CharField(max_length=100)),
                ('action', models.CharField(max_length=200, null=True)),
                ('obj_description', models.CharField(max_length=1000, null=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-created_on'],
                'verbose_name_plural': 'Action History',
            },
        ),
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=10, choices=[(b'', b'Choose Title'), (b'Mr.', b'Mr.'), (b'Mrs.', b'Mrs.'), (b'Ms.', b'Ms.')])),
                ('first_name', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('address_line1', models.CharField(max_length=300, null=True)),
                ('address_line2', models.CharField(max_length=300, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('state', models.CharField(max_length=50, null=True)),
                ('country', models.CharField(max_length=20, null=True)),
                ('telephone', models.CharField(max_length=100, null=True)),
                ('zip_code', models.CharField(max_length=20, null=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-created_on'],
                'verbose_name_plural': 'Addresses Book',
            },
        ),
        migrations.CreateModel(
            name='JoinWaitingList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('joined_on', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='MessageCenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('related_to', models.CharField(max_length=50, null=True)),
                ('booking_ref', models.CharField(max_length=50)),
                ('message', models.TextField()),
                ('no_of_comments', models.IntegerField(default=0)),
                ('new', models.BooleanField(default=True)),
                ('replied', models.BooleanField(default=False)),
                ('replied_on', models.DateTimeField(null=True)),
                ('archive', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='MessageCenterComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('message_obj', models.ForeignKey(to='general.MessageCenter', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SecurityQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=100, null=True, blank=True)),
                ('answer', models.CharField(max_length=250, null=True, blank=True)),
                ('created', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Security Questions',
            },
        ),
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('title', models.CharField(max_length=10, choices=[(b'', b'Choose Title'), (b'Mr.', b'Mr.'), (b'Mrs.', b'Mrs.'), (b'Ms.', b'Ms.')])),
                ('telephone', models.CharField(max_length=100, null=True)),
                ('address', models.CharField(max_length=300, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('state', models.CharField(max_length=50, null=True)),
                ('country', models.CharField(max_length=50, null=True, blank=True)),
                ('username', models.CharField(max_length=50)),
                ('activation_code', models.CharField(max_length=120, null=True)),
                ('registration_time', models.DateTimeField(auto_now_add=True)),
                ('credit_amount_D', models.FloatField(default=0, max_length=20)),
                ('credit_amount_N', models.FloatField(default=0, max_length=20)),
                ('pending_amount_N', models.FloatField(default=0, max_length=20)),
                ('suite_no', models.CharField(max_length=10, null=True)),
                ('image', models.ImageField(null=True, upload_to=b'user_photo', blank=True)),
                ('deactivated', models.BooleanField(default=False)),
                ('flagged', models.BooleanField(default=False)),
                ('business_account', models.BooleanField(default=False)),
                ('company_name', models.CharField(max_length=50, null=True)),
                ('industry', models.CharField(max_length=50, null=True, choices=[(b'', b'Select industry'), (b'Retail', b'Retail'), (b'Oil & Gas', b'Oil & Gas'), (b'Aviation | Travel Agencies', b'Aviation | Travel Agencies'), (b'Consulting | Legal Services', b'Consulting | Legal Services'), (b'Eduction', b'Education'), (b'Financial', b'Financial'), (b'Health', b'Health'), (b'Hospitality', b'Hospitality'), (b'IT Services', b'IT Services'), (b'Manufacturing', b'Manufacturing'), (b'Public Sector', b'Public Sector'), (b'E-Commerce', b'E-Commerce'), (b'Telecommunication', b'Telecommunication'), (b'FMCG', b'FMCG')])),
                ('enquiry', models.TextField()),
                ('how_did_you_find_us', models.CharField(max_length=50, null=True, choices=[(b'', b'How did you find us'), (b'Google Ad', b'Google Ad'), (b'Google Search', b'Google Search'), (b'BellaNaija', b'BellaNaija'), (b'Nairaland', b'Nairaland'), (b'Twitter', b'Twitter'), (b'Facebook', b'Facebook'), (b'A Friend', b'A Friend'), (b'Other', b'Other')])),
                ('photo_id', models.ImageField(null=True, upload_to=b'Photo_ID', blank=True)),
                ('utility_bill', models.ImageField(null=True, upload_to=b'UtilityBill', blank=True)),
                ('address_activation', models.BooleanField(default=False)),
                ('address_activation_completed', models.BooleanField(default=False)),
                ('address_act_completed_date', models.DateTimeField(null=True)),
                ('bank', models.CharField(default=b'', max_length=30, blank=True, choices=[(b'', b'Please select your bank'), (b'ACCESS BANK NIGERIA LTD', b'ACCESS BANK NIGERIA LTD'), (b'DIAMOND BANK LTD', b'DIAMOND BANK LTD'), (b'ECOBANK NIGERIA PLC', b'ECOBANK NIGERIA LTD'), (b'ENTERPRISE BANK LTD', b'ENTERPRISE BANK LTD'), (b'FIDELITY BANK PLC', b'FIDELITY BANK PLC'), (b'FIRST BANK OF NIGERIA PLC', b'FIRST BANK OF NIGERIA PLC'), (b'FIRST CITY MONUMENT BANK', b'FIRST CITY MONUMENT BANK'), (b'GUARANTY TRUST BANK PLC', b'GUARANTY TRUST BANK PLC'), (b'HERITAGE BANK', b'HERITAGE BANK'), (b'JAIZ BANK PLC', b'JAIZ BANK PLC'), (b'KEYSTONE BANK LTD', b'KEYSTONE BANK LTD'), (b'MAINSTREET BANK', b'MAINSTREET BANK'), (b'NIGERIA INTERNATINAL BANK (CITYBANK)', b'NIGERIA INTERNATINAL BANK (CITYBANK)'), (b'SKYE BANK PLC', b'SKYE BANK PLC'), (b'STANBIC IBTC BANK PLC', b'STANBIC IBTC BANK PLC'), (b'STANDARD CHARTERED BANK NIGERIA LTD', b'STANDARD CHARTERED BANK NIGERIA LTD'), (b'STERLING BANK PLC', b'STERLING BANK PLC'), (b'UNION BANK OF NIGERIA PLC', b'UNION BANK OF NIGERIA PLC'), (b'UNITED BANK FOR AFRICA PLC', b'UNITED BANK FOR AFRICA PLC'), (b'UNITY BANK PLC', b'UNITY BANK PLC'), (b'WEMA BANK PLC', b'WEMA BANK PLC'), (b'ZENITH INTERNATIONAL BANK LTD', b'ZENITH INTERNATIONAL BANK LTD')])),
                ('bank_account_no', models.CharField(default=b'', max_length=100, blank=True)),
                ('bvn_no', models.CharField(default=b'', max_length=100, blank=True)),
                ('special_user', models.BooleanField(default=False)),
                ('sokohali_admin', models.BooleanField(default=False)),
                ('marketer', models.ForeignKey(to='service_provider.MarketingMember', null=True)),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-registration_time'],
                'verbose_name_plural': 'User Accounts',
            },
        ),
        migrations.CreateModel(
            name='UserSpecialRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('origin', models.CharField(max_length=100)),
                ('destination', models.CharField(max_length=100)),
                ('rate_per_lb_D', models.FloatField(default=0)),
                ('freight_type', models.CharField(max_length=50, choices=[(b'air_freight', b'Air Freight'), (b'sea_freight', b'Sea Freight'), (b'express_air', b'Express Air')])),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(related_name='created_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_on'],
                'verbose_name_plural': 'User Special Rates',
            },
        ),
        migrations.AddField(
            model_name='securityquestion',
            name='user',
            field=models.OneToOneField(null=True, to='general.UserAccount'),
        ),
    ]
