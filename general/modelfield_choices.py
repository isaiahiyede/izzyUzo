# -*- coding: utf-8 -*-

STATE = (
    ('', 'Select state'),
    ('Abia', 'Abia'),
    ('Abuja','Abuja'),
    ('Adamawa','Adamawa'),
    ('Akwa Ibom','Akwa Ibom'),
    ('Anambra','Anambra'),
    ('Bauchi','Bauchi'),
    ('Bayelsa','Bayelsa'),
    ('Benue','Benue'),
    ('Borno','Borno'),
    ('Cross River', 'Cross River'),
    ('Delta', 'Delta'),
    ('Ebonyi','Ebonyi'),
    ('Edo','Edo'),
    ('Ekiti','Ekiti'),
    ('Enugu','Enugu'),
    ('Gombe','Gombe'),
    ('Imo','Imo'),
    ('Jigawa','Jigawa'),
    ('Kaduna','Kaduna'),
    ('Kano','Kano'),
    ('Katsina','Katsina'),
    ('Kebbi','Kebbi'),
    ('Kogi','Kogi'),
    ('Kwara','Kwara'),
    ('Lagos','Lagos'),
    ('Nasarawa','Nasarawa'),
    ('Niger','Niger'),
    ('Ogun','Ogun'),
    ('Ondo','Ondo'),
    ('Osun','Osun'),
    ('Oyo','Oyo'),
    ('Plateau','Plateau'),
    ('Rivers','Rivers'),
    ('Sokoto','Sokoto'),
    ('Taraba','Taraba'),
    ('Yobe','Yobe'),
    ('Zamfara','Zamfara'),
)

# COUNTRY = (
#     ('', 'Select country'),
#     ('Nigeria', 'Nigeria'),
# )

INDUSTRY = (
    ('', 'Select industry'),
    ('Retail', 'Retail'),
    ('Oil & Gas', 'Oil & Gas'),
    ('Aviation | Travel Agencies', 'Aviation | Travel Agencies'),
    ('Consulting | Legal Services', 'Consulting | Legal Services'),
    ('Eduction', 'Education'),
    ('Financial', 'Financial'),
    ('Health', 'Health'),
    ('Hospitality', 'Hospitality'),
    ('IT Services', 'IT Services'),
    ('Manufacturing', 'Manufacturing'),
    ('Public Sector', 'Public Sector'),
    ('E-Commerce', 'E-Commerce'),
    ('Telecommunication', 'Telecommunication'),
    ('FMCG', 'FMCG'),
)

# Create your models here.
PURCHASED   = 'purchased'
RECEIVED    = 'received'
RETURNED_TO_VENDOR = 'returned to vendor'
NOT_YET_RECEIVED = "not_yet_received"

PRODUCT_STATUS = (
    ('', ''),
    ('approved', 'approved'),
    ('archived', 'archived'),
    ('in-question', 'in-question'),
    (PURCHASED, PURCHASED),
    (RECEIVED, RECEIVED),
    (RETURNED_TO_VENDOR, RETURNED_TO_VENDOR),
)

PREPARED_FOR_SHIPPING   = 'prepared for shipping'
SHIPPED                 = 'shipped'
ASSIGNED_TO_BATCH       = 'assigned to batch'
PREPARED_FOR_DELIVERY   = 'prepared for delivery'

PACKAGE_STATUS = (
    ('', ''),
    (PREPARED_FOR_SHIPPING, PREPARED_FOR_SHIPPING),
    #(SHIPPED, SHIPPED),
    (ASSIGNED_TO_BATCH, ASSIGNED_TO_BATCH),
    (PREPARED_FOR_DELIVERY, PREPARED_FOR_DELIVERY),
    ('delivered', 'delivered'),
)

HOW_DID_YOU_FIND_US = (
    ('', 'How did you find us'),
    ('Google Ad', 'Google Ad'),
    ('Google Search', 'Google Search'),
    ('BellaNaija', 'BellaNaija'),
    ('Nairaland', 'Nairaland'),
    ('Twitter', 'Twitter'),
    ('Facebook', 'Facebook'),
    ('A Friend', 'A Friend'),
    ('Other', 'Other'),
)
TITLE = (
    ('', 'Choose Title'),
    # ('Dr.', 'Dr.'),
    ('Mr.', 'Mr.'),
    ('Mrs.', 'Mrs.'),
    ('Ms.', 'Ms.'),
)


BANKS = (
    ('', 'Please select your bank'),
    ('ACCESS BANK NIGERIA LTD', 'ACCESS BANK NIGERIA LTD'),
    ('DIAMOND BANK LTD', 'DIAMOND BANK LTD'),
    ('ECOBANK NIGERIA PLC', 'ECOBANK NIGERIA LTD'),
    ('ENTERPRISE BANK LTD', 'ENTERPRISE BANK LTD'),
    ('FIDELITY BANK PLC', 'FIDELITY BANK PLC'),
    ('FIRST BANK OF NIGERIA PLC', 'FIRST BANK OF NIGERIA PLC'),
    ('FIRST CITY MONUMENT BANK', 'FIRST CITY MONUMENT BANK'),
    ('GUARANTY TRUST BANK PLC', 'GUARANTY TRUST BANK PLC'),
    ('HERITAGE BANK', 'HERITAGE BANK'),
    ('JAIZ BANK PLC', 'JAIZ BANK PLC'),
    ('KEYSTONE BANK LTD', 'KEYSTONE BANK LTD'),
    ('MAINSTREET BANK', 'MAINSTREET BANK'),
    ('NIGERIA INTERNATINAL BANK (CITYBANK)', 'NIGERIA INTERNATINAL BANK (CITYBANK)'),
    ('SKYE BANK PLC', 'SKYE BANK PLC'),
    ('STANBIC IBTC BANK PLC', 'STANBIC IBTC BANK PLC'),
    ('STANDARD CHARTERED BANK NIGERIA LTD', 'STANDARD CHARTERED BANK NIGERIA LTD'),
    ('STERLING BANK PLC', 'STERLING BANK PLC'),
    ('UNION BANK OF NIGERIA PLC', 'UNION BANK OF NIGERIA PLC'),
    ('UNITED BANK FOR AFRICA PLC', 'UNITED BANK FOR AFRICA PLC'),
    ('UNITY BANK PLC', 'UNITY BANK PLC'),
    ('WEMA BANK PLC', 'WEMA BANK PLC'),
    ('ZENITH INTERNATIONAL BANK LTD', 'ZENITH INTERNATIONAL BANK LTD'),
)

COUNTRIES = ['us', 'uk', 'china', 'Nigeria']

COUNTRIES_1 = ['USA', 'UK', 'China', 'Nigeria']

COUNTRY = (
        (COUNTRIES_1[0], 'USA'),
        (COUNTRIES_1[1], 'UK'),
        (COUNTRIES_1[2], 'China'),
        (COUNTRIES_1[3], 'Nigeria')
)


MARKETER_COUNTRIES = (
        ('Afghanistan','Afghanistan'),
        ('Albania','Albania'),
        ('Algeria','Algeria'),
        ('Andorra','Andorra'),
        ('Angola','Angola'),
        ('Antigua and Barbuda','Antigua and Barbuda'),
        ('Argentina','Argentina'),
        ('Armenia','Armenia'),
        ('Australia','Australia'),
        ('Austria','Austria'),
        ('Azerbaijan','Azerbaijan'),
        ('Bahamas','Bahamas'),
        ('Bahrain','Bahrain'),
        ('Bangladesh','Bangladesh'),
        ('Barbados','Barbados'),
        ('Belarus','Belarus'),
        ('Belgium','Belgium'),
        ('Belize','Belize'),
        ('Benin','Benin'),
        ('Bhutan','Bhutan'),
        ('Bolivia','Bolivia'),
        ('Bosnia and Herzegovina','Bosnia and Herzegovina'),
        ('Botswana','Botswana'),
        ('Brazil','Brazil'),
        ('Brunei','Brunei'),
        ('Bulgaria','Bulgaria'),
        ('Burkina Faso','Burkina Faso'),
        ('Burundi','Burundi'),
        ('Cabo Verde','Cabo Verde'),
        ('Cambodia','Cambodia'),
        ('Cameroon','Cameroon'),
        ('Canada','Canada'),
        ('Central African Republic','Central African Republic'),
        ('Chad','Chad'),
        ('Chile','Chile'),
        ('China','China'),
        ('Colombia','Colombia'),
        ('Comoros','Comoros'),
        ('Democratic Republic of the Congo','Democratic Republic of the Congo'),
        ('Republic of the Congo','Republic of the Congo'),
        ('Costa Rica','Costa Rica'),
        ('Croatia','Croatia'),
        ('Cuba','Cuba'),
        ('Cyprus','Cyprus'),
        ('Czech Republic','Czech Republic'),
        ('Denmark','Denmark'),
        ('Djibouti','Djibouti'),
        ('Dominica','Dominica'),
        ('Dominican Republic','Dominican Republic'),
        ('Ecuador','Ecuador'),
        ('Egypt','Egypt'),
        ('El Salvador','El Salvador'),
        ('Equatorial Guinea','Equatorial Guinea'),
        ('Eritrea','Eritrea'),
        ('Estonia','Estonia'),
        ('Ethiopia','Ethiopia'),
        ('Fiji','Fiji'),
        ('Finland','Finland'),
        ('France','France'),
        ('Gabon','Gabon'),
        ('Gambia','Gambia'),
        ('Georgia','Georgia'),
        ('Germany','Germany'),
        ('Ghana','Ghana'),
        ('Greece','Greece'),
        ('Grenada','Grenada'),
        ('Guatemala','Guatemala'),
        ('Guinea','Guinea'),
        ('Guinea-Bissau','Guinea-Bissau'),
        ('Guyana','Guyana'),
        ('Haiti','Haiti'),
        ('Honduras','Honduras'),
        ('Hungary','Hungary'),
        ('Iceland','Iceland'),
        ('India','India'),
        ('Indonesia','Indonesia'),
        ('Iran','Iran'),
        ('Iraq','Iraq'),
        ('Ireland','Ireland'),
        ('Italy','Italy'),
        ('Ivory Coast','Ivory Coast'),
        ('Jamaica','Jamaica'),
        ('Japan','Japan'),
        ('Jordan','Jordan'),
        ('Kazakhstan','Kazakhstan'),
        ('Kenya','Kenya'),
        ('Kiribati','Kiribati'),
        ('Kosovo','Kosovo'),
        ('Kuwait','Kuwait'),
        ('Kyrgyzstan','Kyrgyzstan'),
        ('Laos','Laos'),
        ('Latvia','Latvia'),
        ('Lebanon','Lebanon'),
        ('Lesotho','Lesotho'),
        ('Liberia','Liberia'),
        ('Libya','Libya'),
        ('Liechtenstein','Liechtenstein'),
        ('Lithuania','Lithuania'),
        ('Luxembourg','Luxembourg'),
        ('Macedonia','Macedonia'),
        ('Madagascar','Madagascar'),
        ('Malawi','Malawi'),
        ('Malaysia','Malaysia'),
        ('Maldives','Maldives'),
        ('Mali','Mali'),
        ('Malta','Malta'),
        ('Marshall Islands','Marshall Islands'),
        ('Mauritania','Mauritania'),
        ('Mauritius','Mauritius'),
        ('Mexico','Mexico'),
        ('Micronesia','Micronesia'),
        ('Moldova','Moldova'),
        ('Monaco','Monaco'),
        ('Mongolia','Mongolia'),
        ('Montenegro','Montenegro'),
        ('Morocco','Morocco'),
        ('Mozambique','Mozambique'),
        ('Myanmar','Myanmar'),
        ('Namibia','Namibia'),
        ('Nauru','Nauru'),
        ('Nepal','Nepal'),
        ('Netherlands','Netherlands'),
        ('New Zealand','New Zealand'),
        ('Nicaragua','Nicaragua'),
        ('Niger','Niger'),
        ('Nigeria','Nigeria'),
        ('North Korea','North Korea'),
        ('Norway','Norway'),
        ('Oman','Oman'),
        ('Pakistan','Pakistan'),
        ('Palau','Palau'),
        ('Palestine','Palestine'),
        ('Panama','Panama'),
        ('Papua New Guinea','Papua New Guinea'),
        ('Paraguay','Paraguay'),
        ('Peru','Peru'),
        ('Poland','Poland'),
        ('Portugal','Portugal'),
        ('Qatar','Qatar'),
        ('Romania','Romania'),
        ('Russia','Russia'),
        ('Rwanda','Rwanda'),
        ('Saint Kitts and Nevis','Saint Kitts and Nevis'),
        ('Saint Lucia','Saint Lucia'),
        ('Saint Vincent and the Grenadines','Saint Vincent and the Grenadines'),
        ('Samoa','Samoa'),
        ('San Marino','San Marino'),
        ('Sao Tome and Principe','Sao Tome and Principe'),
        ('Saudi Arabia','Saudi Arabia'),
        ('Senegal','Senegal'),
        ('Serbia','Serbia'),
        ('Seychelles','Seychelles'),
        ('Sierra Leone','Sierra Leone'),
        ('Singapore','Singapore'),
        ('Slovakia','Slovakia'),
        ('Slovenia','Slovenia'),
        ('Solomon Islands','Solomon Islands'),
        ('Somalia','Somalia'),
        ('South Africa','South Africa'),
        ('South Korea','South Korea'),
        ('South Sudan','South Sudan'),
        ('Spain','Spain'),
        ('Sri Lanka','Sri Lanka'),
        ('Sudan','Sudan'),
        ('Suriname','Suriname'),
        ('Swaziland','Swaziland'),
        ('Sweden','Sweden'),
        ('Switzerland','Switzerland'),
        ('Taiwan','Taiwan'),
        ('Tajikistan','Tajikistan'),
        ('Tanzania','Tanzania'),
        ('Thailand','Thailand'),
        ('Timor-Leste','Timor-Leste'),
        ('Togo','Togo'),
        ('Tonga','Tonga'),
        ('Trinidad and Tobago','Trinidad and Tobago'),
        ('Tunisia','Tunisia'),
        ('Turkey','Turkey'),
        ('Turkmenistan','Turkmenistan'),
        ('Tuvalu','Tuvalu'),
        ('Uganda','Uganda'),
        ('Ukraine','Ukraine'),
        ('United Arab Emirates','United Arab Emirates'),
        ('United Kingdom','United Kingdom'),
        ('United States','United States'),
        ('Uruguay','Uruguay'),
        ('Uzbekistan','Uzbekistan'),
        ('Vanuatu','Vanuatu'),
        ('Vatican City','Vatican City'),
        ('Venezuela','Venezuela'),
        ('Vietnam','Vietnam'),
        ('Yemen','Yemen'),
        ('Zambia','Zambia'),
        ('Zimbabwe','Zimbabwe'),

)

DELIVERY_COUNTRIES = (
    ('', 'Select country'),
    ('Nigeria', 'Nigeria'),
    #('Ghana', 'Ghana')
)


ORDER_SOURCES = (
    ('M', 'Mobile'),
    ('W', 'Web'),
)

WEIGHT_UNIT = (
    ('kg', 'kilogram(kg)'),
    ('lbs', 'pounds(lb)'),
)

# LOCAL_DELIVERY_CHOICES = (
#     ('AF - OP', 'Office Pickup'),
#     ('AF - AP', 'Office Pickup outside Lagos'),
#     ('AF - WL', 'Home delivery within Lagos'),
#     ('AF - AL', 'Home delivery outside Lagos'),
#     ('SF - OP', 'Office Pickup'),
#     ('SF - AP', 'Office Pickup outside Lagos'),
#     ('SF - WL', 'Home delivery within Lagos'),
#     ('SF - AL', 'Home delivery outside Lagos'),
#     ('EX - OP', 'Office Pickup'),
#     ('EX - AP', 'Office Pickup outside Lagos'),
#     ('EX - WL', 'Home Delivery within Lagos'),
#     ('EX - AL', 'Home Delivery outside Lagos'),
# )


LOCAL_DELIVERY_CHOICES = (
    ('AF - OP', 'Air Freight - Office Pickup'),
    ('AF - HD', 'Air Freight - Home delivery'),
    ('SF - OP', 'Sea Freight - Office Pickup'),
    ('SF - HD', 'Sea Freight - Home delivery'),
    ('EX - OP', 'Express Air - Office Pickup'),
    ('EX - HD', 'Express Air - Home delivery'),
)

PAYMENT =(
    ('Shipping Credit', 'Apply Shipping Credit'),
    ('PP', 'Pay-Pal'),
    ('Card Payment', 'Card Payment'),
    ('Bank Deposit', 'Bank Deposit'),
    ('Payment on hold', 'Payment on hold'),
)

SENDING_METHOD = (
    ('send from shop','send from shop'),
    ('export import', 'export import'),
    ('pick up package', 'pick up package'),
)

SERVICE_TYPE = (
    ('shipping', 'shipping'),
    ('shopping', 'shopping'),
)

# DIRECTION_TYPE = (
#     ('import', 'Import'),
#     ('export', 'Export'),
#     ('import_export', 'Import & Export'),
# )
DIRECTION_TYPE = (
    ('uni-directional', 'Uni-Directional'),
    ('bi-directional', 'Bi-Directional'),
)

CURRENCY = (
    ('naira', "=N="),
    ('pounds', "£"),
    ('dollars', "$"),
)

BANK_CURRENCY = (
    ('Nigerian Naira', 'Naira (=N=)'),
    ('British Pounds', 'Pounds (£)'),
    ('American Dollars', 'Dollars ($)'),
)

ShippingMethod = (
    ('air', 'Air'),
    ('sea', 'Sea'),
    ('express','Express'),
    ('ground', 'ground'),
)

SHIPPING_METHOD = (
    ('air_freight', 'Air Freight'),
    ('sea_freight', 'Sea Freight'),
    ('express_air', 'Express Air'),
 )

DELIVERY_METHOD = (
    ('Office pickup', 'Office pickup'),
    ('Home delivery', 'Home delivery'),
)

MARKETINGMEMBER_COLORS = (
    ('#0b71b9', 'Blue'),
    ('#ffd014', 'Yellow'),
    ('#3ab54a', 'Green'),
)

OFFERED_SERVICES = (
    ('ORIGIN WAREHOUSE', 'ORIGIN WAREHOUSE'),
    ('DESTINATION WAREHOUSE', 'DESTINATION WAREHOUSE'),
    ('SHIPPING', 'SHIPPING'),
    ('CLEARING', 'CLEARING'),
)
