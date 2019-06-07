  function maxLengthCheck(object) {
    if (object.value.length > object.maxLength)
      object.value = object.value.slice(0, object.maxLength)
  }

  function isNumeric (evt) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    key = String.fromCharCode (key);
    var regex = /[0-9]/;
    if ( !regex.test(key) ) {
      theEvent.returnValue = false;
      if(theEvent.preventDefault) theEvent.preventDefault();
    }
  }

$('#details_form').validate();
$('#card_details_form').validate();

$('#submit_card').click(function(e){
    //e.preventDefault();
    if ($('#card_details_form').valid()) {
      //$('.divLoading').addClass('show');
      $('.loading').addClass('show');
        //$('#submit_shipment_form').submit();
        $.ajax({
          url: '',
          type: 'POST',
          data: $('#detail_form, #card_details_form').serialize(),

          success: function(data){
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
                return false
            }else{
              if (data.decoded_responsehtml){
                //$('#card_payment').replaceWith(data.decoded_responsehtml)
                window.location.href = data.intl_card_verification_url
                return false;
              }
              if (data.response_msg) {
                $('#card_details').addClass('hidden');
                $('#otp_details').removeClass('hidden');
                $("#response_msg").html(data.response_msg);
                $("#id_otptransactionidentifier").val(data.otptransactionidentifier)
                $('#id_amount_N').val('=N= '+data.actual_amount_N);
                $('#id_txn_charge_N').val('=N= '+data.markup_charge_N);
                $('#id_total_N').val('=N= '+data.total_N);
                $("#id_jejepay_ref").val(data.jejepay_ref)
                //add css
                var css_style = {'position': 'relative', 'width' : '102%', 'border-color': 'rgb(121, 121, 121) !important',
                                'color': 'rgb(121, 121, 121) !important', 'background-color': 'white', 'color': '#333'}

                var fields = ['id_amount_N', 'id_txn_charge_N', 'id_total_N']
                for (var i=0; i<fields.length; i++) {
                    $('#'+fields[i]).css(css_style)
                }
                $('.loading').removeClass('show');
              }
            }

          }
        })
    }

})

$("#submit_otp").click(function(e){
  $('#otp_form').validate();
  if ($('#otp_form').valid()) {
    $(this).prop('disabled', true)
    $('.loading').addClass('show');
    $.ajax({
      url: '',
      type: 'POST',
      data: $('#detail_form, #otp_form').serialize(),

      success: function(data){
        if (data.redirect_url) {
                window.location.href = data.redirect_url;
          }else{
            //if (data.response_msg.indexOf("success") != -1) {
            //    window.location.href = data.redirect_url;
            //}else{
              $("#response_msg").html(data.response_msg);
              $('.loading').removeClass('show');
            //}
          }
        }

    })
  }
})
