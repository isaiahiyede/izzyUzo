from django.forms import ModelForm
from models import SokoPay, MarketerPayment


class SokoPayForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SokoPayForm, self).__init__(*args, **kwargs)

    class Meta:
        model = SokoPay
        #fields = ('amount',)
        exclude = ('purchase_type_1','payment_gateway_tranx_id', 'teller_no', 'created_at', 'status', 'exchange_rate')
        
        
class SokoPayAddForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SokoPayAddForm, self).__init__(*args, **kwargs)

    class Meta:
        model = SokoPay
        #fields = ('amount',)
        exclude = ('payment_gateway_tranx_id', 'created_at', 'status', 'exchange_rate')
        
        
class MarketerPaymentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MarketerPaymentForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = MarketerPayment
        fields = ('amount', 'payment_channel', 'ref_no', 'bank', 'teller_no',)
        #exclude = ('payment_gateway_tranx_id', 'created_at', 'status', 'message', 'marketer','package')

