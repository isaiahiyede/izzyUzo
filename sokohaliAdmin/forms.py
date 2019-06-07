from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, CharField, BooleanField
import datetime
from sokohaliAdmin.models import *
# from export.models import *
from shipping.models import *
from general.models import UserAccount, UserSpecialRate
from general.modelfield_choices import SHIPPING_METHOD as SM
from django.contrib.admin import widgets

from service_provider.models import *


BATCH_STATUS = (

    ('New', 'New'),
    ('Processing', 'Processing'),
    ('DeliveredToCarrier', 'Delivered To Carrier'),
    ('Departed', 'Departed'),
    ('ClearingCustoms', 'Clearing Customs'),
    ('ProcessingForDelivery', 'Processing For Delivery'),
    ('Archive', 'Archive'),
    ('Cancel', 'Cancel'),

)

BATCH_TYPE = (
    ('USA-NGA', 'USA-NGA'),
    ('NGA-USA', 'NGA-USA'),
)

FREIGHT_TYPE = (

    ('Air-Freight','Air-Freight'),
    ('Sea-Freight','Sea-Freight'),
    ('Express Air','Express Air'),

)

SHIPPING_METHOD = (

    ('Air Cargo','Air Cargo'),
    ('Sea Cargo','Sea Cargo'),
    ('Express Air','Expresss Air'),
)

WEIGHT_UNIT = (
    ('kg', 'kilogram(kg)'),
    ('lbs', 'pounds(lb)'),
    )


class BatchForm(forms.ModelForm):

    shipping_method = forms.ChoiceField(choices=SHIPPING_METHOD,widget=forms.Select(attrs={'placeholder':'SHIPPING METHOD','required':'required'}))
    carrier = forms.CharField(max_length=50,help_text="",widget=forms.TextInput(attrs={'placeholder':'CARRIER','required':'required'}))
    status = forms.ChoiceField(choices=BATCH_STATUS,widget=forms.Select(attrs={'placeholder':'BATCH STATUS','required':'required'}))
    freight_type = forms.ChoiceField(choices=FREIGHT_TYPE,widget=forms.Select(attrs={'placeholder':'FREIGHT TYPE','required':'required'}))
    awb_doc = forms.FileField(required=False)
    bol_doc = forms.FileField(required=False)


    class Meta:
        model = Batch
        fields = ('shipping_method','carrier','status','awb_doc','bol_doc')


class BatchEditHistoryForm(forms.ModelForm):

    class Meta:
        model  = BatchEditHistory
        fields =  ('batch_status','created_on','eta','updated_on',)


class ShippingPackageForm(forms.ModelForm):
    class Meta:
        model = ShippingPackage
        fields = ['box_length', 'box_height', 'box_weight', 'box_width', 'pkg_image']


class TruckingForm(forms.ModelForm):
    class Meta:
        model = Trucking
        fields = ['job_number', 'cargo_decsription', 'actual_cargo_weight', 'total_cargo_weight', 'bol_number', 'origin','destination', 'pick_up_time', 'drop_off_time', 'status', 'paid', 'bol_image','time_to_pick_up', 'time_to_drop_off']


class notifyUserForm(forms.ModelForm):
    class Meta:
        model = NotifyUser
        fields = ['name', 'last_four_digits', 'suite_no', 'address', 'item_description', 'image_field','weight']

        
class AwbForm(forms.ModelForm):
    shippers_name_and_address = forms.CharField(help_text="Shippers Name and Address",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Shippers Name and Address', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    shippers_number = forms.CharField( widget=TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Shippers Phone Number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    shippers_acct_no =forms.CharField(help_text = "Shippers Account Number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Shippers Account Number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    consignees_name_and_address = forms.CharField(widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Consignee Name and Address', 'cols': 2, 'rows': 2, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    consignees_number = forms.CharField( widget=TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Consignee Phone Number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    consignees_acct_no = forms.CharField(help_text = "Consignee Account Number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Consignee Account Number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    carrier_agent_name_and_city = forms.CharField(widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Carrier Agent Name and City', 'cols': 2, 'rows': 2, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    carrier_agent_iata_code = forms.CharField(help_text = "Carrier Agent IATA Code",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Carrier Agent IATA Code', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    agent_acct_no = forms.CharField(widget=TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Agent Account Number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    airport_of_departure = forms.CharField(help_text = "Airport of Departure",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Airport of Departure', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    origin_routing_code = forms.CharField(help_text = "Origin Routing (Code e.g. IAD)",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Origin Routing (Code e.g. IAD)', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    origin_airline_carrier = forms.CharField(help_text = "Origin Airline Carrier (Code e.g. AF)",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Origin Airline Carrier (Code e.g. AF)', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    destination_and_departure_routing_code1 = forms.CharField(help_text = "Airport of Destination/Departure (Code e.g. CDG)",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Airport of Destination/Departure (Code e.g. CDG)', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    second_airline_carrier = forms.CharField(help_text = "Airline Carrier (Code e.g. AF)",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Airline Carrier (Code e.g. AF)', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    state_of_destination = forms.CharField(help_text = "State of Destination (Code e.g. LOS)",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'State of Destination (Code e.g. LOS)', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    third_airline_carrier = forms.CharField(help_text = "Airport Carrier (Code e.g. AF)",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Airport Carrier (Code e.g. AF)', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    airport_of_destination = forms.CharField(help_text = "Airport of Destination",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Airport of Destination', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    requested_flight_and_date1 = forms.CharField(help_text = "First Requested Flight/Date",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'First Requested Flight/Date', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    requested_flight_and_date2 = forms.CharField(help_text = "Second Requested Flight/Date",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Second Requested Flight/Date', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    handling_info = forms.CharField(help_text = "Handling Information",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Handling Information', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    issued_airline_carrier_and_address = forms.CharField(widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Issued Airline Carrier and Address', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    accounting_info = forms.CharField(help_text = "Accounting Information",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Accounting Information', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    ref_number = forms.CharField(help_text = "Reference Number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Reference Number', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    currency_code = forms.CharField(help_text = "Currency Code e.g. USD",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Currency Code e.g. USD', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    value_for_carriage = forms.CharField(help_text = "Declared Value for Carriage (Code e.g. NVD)",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Declared Value for Carriage (Code e.g. NVD)', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    value_for_custom = forms.CharField(help_text = "Declared Value for Customs (Code e.g. NCV)",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Declared Value for Customs (Code e.g. NCV)', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    amount_of_insurance = forms.CharField(widget=TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Amount of Insurance', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    number_of_pieces_to_ship = forms.CharField(widget=TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Number of Pieces RCP', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    gross_weight = forms.CharField( widget=TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Gross Weight', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    chargeable_rate = forms.CharField(widget=TextInput(attrs={'class': "red", 'type':'number', 'step':'0.01','placeholder': 'Chargeable Rate', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    note_on_the_package = forms.CharField(help_text="Note concerning the PACKAGE been Shipped",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Note concerning the PACKAGE been Shipped', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    nature_and_quantity_of_goods = forms.CharField(help_text="Nature and Quantity of Goods",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Nature and Quantity of Goods', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    regulation_of_goods = forms.CharField(help_text="Regulation on the type of  Goods",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Regulation on the type of  Goods', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    tracking_number_prefix = forms.CharField( widget=TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Airline Tracking Number Prefix', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    airline_tracking_number = forms.CharField( widget=TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Airline Tracking Number ', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    other_charges_due_carrier = forms.CharField( widget=TextInput(attrs={'class': "red", 'type':'number', 'step':'0.01','placeholder': 'Total Other Charges Due Carrier ', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    # total_prepaid = forms.DecimalField(max_digits=20,decimal_places=2,null=True, blank=True)
    place_of_execution = forms.CharField(help_text = "Place of Execution",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Place of Execution', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    shippers_name = forms.CharField(help_text = "Shippers Name",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Shippers Name', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    carrier_name = forms.CharField(help_text = "Carrier Name",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Carrier Name', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))

    class Meta:
        model = AirwayBill
        fields = ('shippers_name_and_address','shippers_number','shippers_acct_no','consignees_name_and_address','consignees_number','consignees_acct_no','carrier_agent_name_and_city','carrier_agent_iata_code',
            'agent_acct_no','airport_of_departure','origin_routing_code','origin_airline_carrier','destination_and_departure_routing_code1','second_airline_carrier','state_of_destination','third_airline_carrier',
            'airport_of_destination','requested_flight_and_date1','requested_flight_and_date2','handling_info','issued_airline_carrier_and_address','accounting_info','ref_number','currency_code','value_for_carriage',
            'amount_of_insurance','number_of_pieces_to_ship','gross_weight','chargeable_rate','note_on_the_package','nature_and_quantity_of_goods','regulation_of_goods','tracking_number_prefix','airline_tracking_number',
            'other_charges_due_carrier','place_of_execution','shippers_name','carrier_name')



class AdminCreateuserForm(forms.ModelForm):
    first_name      = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name', 'required':'required'}), error_messages = {'required': 'Please provide your first name.'})
    last_name       = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'required':'required'}), error_messages = {'required': 'Please provide your last name.'})
    #telephone       = forms.CharField(error_messages = {'required': 'Please provide your telephone.'})
    #how_did_you_find_us = forms.ChoiceField(choices = HOW_DID_YOU_FIND_US, error_messages = {'required': 'Please how did you get to know about us.'})
    username        = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'required':'required'}), error_messages = {'required': 'Please provide your username.'})
    email           = forms.EmailField(label=(u'Email Address'), widget=forms.TextInput(attrs={'placeholder': 'Email', 'required':'required'}), error_messages={'required': 'Please provide your email address.'})

    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'username', 'email']


class BatchPromoForm(forms.ModelForm):
    # shipping_method = forms.ChoiceField(choices=SHIPPING_METHOD,widget=forms.Select(attrs={'placeholder':'SHIPPING METHOD','required':'required'}))


    class Meta:
        model = BatchPromo
        fields = ('shipment_type','available_space','estimated_departure_time','current_rate','origin','destination','weight_range_at_rate','is_active',)


class SpecialRateForm(forms.ModelForm):
    freight_type = forms.ChoiceField(choices=SM, widget=forms.Select(attrs={'placeholder':'SHIPPING METHOD','required':'required', 'class':'select-styled2'}))


    class Meta:
        model = UserSpecialRate
        fields = ('rate_per_lb_D', 'freight_type')


class DockReceiptForm(forms.ModelForm):
    exporter_name_and_address = forms.CharField(help_text="Exporter Name and Address",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Exporter Name and Address', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    zip_code = forms.CharField(help_text = "Zip Code",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Zip Code', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    consigned_to = forms.CharField(help_text="Consigned To",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Consigned To', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    notify_party_name_and_address = forms.CharField(help_text="Notify Party Name and Address",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Notify Party Name and Address', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    document_number = forms.CharField(help_text="Document Number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Document Number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    bl_or_awb_number = forms.CharField(help_text="Bill of Lading or AWB number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Bill of Lading or AWB number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    export_references = forms.CharField(help_text="Export References",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Export References', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    forwarding_agent_fmc_no = forms.CharField(help_text="Forwarding Agent FMC Number",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Forwarding Agent FMC Number', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    state_and_country_of_origin_or_ftz_number = forms.CharField(help_text="State and Country of Origin or FTZ number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'State and Country of Origin or FTZ number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    domestic_routing = forms.CharField(help_text="Domestic Routing / Export Instruction",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Domestic Routing / Export Instruction', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    loading_pier = forms.CharField(help_text="Loading Pier / Terminal",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Loading Pier / Terminal', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    type_of_move = forms.CharField(help_text="Type of Move",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Type of Move', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    containerized = forms.BooleanField(required=False, initial=False, label='Containerized')
    precarriage_by = forms.CharField(help_text="Pre-Carriage By",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Pre-Carriage By', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    place_of_receipt_by_precarrier = forms.CharField(help_text="Place of Receipt by Pre-Carrier",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Place of Receipt by Pre-Carrier', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    exporting_carrier = forms.CharField(help_text="Export Carrier",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Export Carrier', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    port_of_loading = forms.CharField(help_text="Port of Loading",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Port of Loading', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    foreign_port_of_unloading = forms.CharField(help_text="Foreign Port of Unloading",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Foreign Port of Unloading', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    place_of_delivery_by_oncarrier = forms.CharField(help_text="Place of Delivery by On-Carrier",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Place of Delivery by On-Carrier', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    mks_nos = forms.CharField(help_text="MKS. & NOS./CONT. NOS.",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'MKS. & NOS./CONT. NOS.', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    no_of_pkgs = forms.CharField(help_text="Number of Packages",widget=forms.TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Number of Packages', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    description_of_package_and_goods = forms.CharField(help_text="Description of Packages and Goods",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Description of Packages and Goods', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    gross_weight = forms.CharField(help_text="Gross Weight",widget=forms.TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Gross Weight', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    measurement = forms.CharField(help_text="Measurement",widget=forms.TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Measurement (lbs)', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    lighter_truck = forms.CharField(help_text="Lighter Truck",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Lighter Truck', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # arrived_date = forms.DateField(help_text="Arrived Date",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Arrived Date', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # arrived_time = forms.TimeField(widget=widgets.AdminTimeWidget)
    # unloaded_date = forms.DateField(help_text="Unloaded Date",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Unloaded Date', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # unloaded_time =  forms.DateField(help_text="Unloaded Time",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Unloaded Time', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    checked_by = forms.CharField(help_text="Checked By",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Checked By', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    placed_location = forms.CharField(help_text="Placed Location",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Placed Location', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    receiving_clerk_name = forms.CharField(help_text="Receiving Clerk Name",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Receiving Clerk Name', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # date_from_receiving_clerk = forms.DateField(help_text="Arrived Date",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Lighter Truck', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # created_on
    # created_by = forms.CharField(help_text="Created By",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Created By', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))

    class Meta:
        model = DockReceipt
        fields = ('exporter_name_and_address','zip_code','consigned_to','notify_party_name_and_address','document_number','bl_or_awb_number','export_references','forwarding_agent_fmc_no','state_and_country_of_origin_or_ftz_number',
            'domestic_routing','loading_pier','type_of_move','containerized','precarriage_by','place_of_receipt_by_precarrier','exporting_carrier','port_of_loading','foreign_port_of_unloading','place_of_delivery_by_oncarrier','mks_nos',
            'no_of_pkgs','description_of_package_and_goods','gross_weight', 'measurement','lighter_truck','arrived_date','arrived_time','created_by','unloaded_date','unloaded_time','checked_by','placed_location','receiving_clerk_name','date_from_receiving_clerk')



class LocalDistributionMemberForm(forms.ModelForm):
    courier_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Courier Name', 'required':'required'}), error_messages = {'required': 'Please provide courier_name.'})
    # country = 
    active = forms.BooleanField(required=False, initial=False, label='Active')
    has_api = forms.BooleanField(required=False, initial=False, label='Has API')
    has_configured_rates = forms.BooleanField(required=False, initial=False, label='Has Configured Rate')
    # marketing_member

    class Meta:
        model = LocalDistributionMember
        fields = ('courier_name','active','has_api','has_configured_rates')

class LocalDistributorRegionForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Region Name', 'required':'required'}), error_messages = {'required': 'Please provide a region.'})

    class Meta:
        model = LocalDistributorRegion
        fields = ('name',)


class LocalDistributorLocationForm(forms.ModelForm):
    address1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 1', 'required':'required'}), error_messages = {'required': 'Please provide your address.'})
    address2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 2', 'required':'required'}), error_messages = {'required': 'Please provide your address.'})
    city = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City', 'required':'required'}), error_messages = {'required': 'Please provide your city.'})
    # state
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'required':'required'}), error_messages = {'required': 'Please provide Phone Number.'})
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number','required':'required'}), error_messages = {'required': 'Please provide Zip Code.'})
    pickup_available = forms.BooleanField(required=False, initial=False, label='pickup_available')
    drop_off_available = forms.BooleanField(required=False, initial=False, label='drop_off_available')
    offered_location = forms.BooleanField(required=False, initial=False, label='offered_location')

    class Meta:
        model = LocalDistributorLocation
        fields = ('address1','address2','city','phone_number','zip_code','pickup_available','drop_off_available','offered_location')


class LocalDistributorPriceForm(forms.ModelForm):
    weight = forms.CharField(widget=forms.TextInput(attrs={'type':'number', 'step':'0.1', 'placeholder': 'Weight', 'required':'required'}), error_messages = {'required': 'Please provide your Weight.'})
    weight_unit = forms.ChoiceField(choices=WEIGHT_UNIT,widget=forms.Select(attrs={'placeholder':'Weight Unit','required':'required'}))
    price = forms.CharField(widget=forms.TextInput(attrs={'type':'number', 'step':'0.1', 'placeholder': 'Price', 'required':'required'}), error_messages = {'required': 'Please provide your Price.'})
    markup_value = forms.CharField(widget=forms.TextInput(attrs={'type':'number', 'step':'0.1', 'placeholder': 'Markup Value', 'required':'required'}), error_messages = {'required': 'Please provide Markup Value.'})

    class Meta:
        model = LocalDistributorLocation
        fields = ('weight','weight_unit','price','markup_value')