$('#delivery_rate_form').validate();


$(document).ready(function(){
  $('#id_direction').html('<option value>-----------</option>');
})

$('#delivery_rate_form').submit(function(){
  $('input').each(function(index, obj){
    if($(obj).val() == ""){
      $(obj).remove()
    }
  })
})


$('#add_rate').click(function(){
    document.getElementById('delivery_rate_form').reset();

    if ($(this).attr('route_id')){
      $('#id_shipping_chain').val($(this).attr('route_id')).prop('disabled', true)
      $('#id_tx_shipping_chain').val(($('#id_shipping_chain').val()))
    }
    $('#DeliveryRateModal .add').removeClass('hidden')
    $('#DeliveryRateModal .edit').addClass('hidden')
    $('#DeliveryRateModal').modal('show');
})

$('.route_sm').on('change', function(){
  var shipping_chain  = $('#id_shipping_chain option:selected').val();
  var shipping_method = $('#id_shipping_method option:selected').val();

  if (shipping_chain != '' && shipping_method != ''){
      $trs = $('.tb-'+shipping_chain).find('.'+shipping_method);
      var to_weight = 0;
      $trs.each(function(){
        var to_weight_val = parseFloat($(this).find('td').eq(3).html());
        if (to_weight_val > to_weight){
          to_weight = to_weight_val;
        }
      })
      $('#id_from_range').val(to_weight+0.01)
  }

});


$('.edit_rate').on('click', function(){
  $('.loading').addClass('show');

    var edit_route = $(this).attr('edit_route')
  // $.get('', {'edit_route': edit_route}, function(data){
  //   $('#route_rate_inner').replaceWith(data);

    $('#DeliveryRateModal .add').addClass('hidden')
    $('#DeliveryRateModal .edit').removeClass('hidden')

    $('.edit #route_val').html($(this).attr('route'))
    $('.edit #sm_val').html($(this).attr('sm'))
    $('.edit #wrg_val').html($(this).attr('wrg')+' lbs')
    $('.edit #id_edit_route').val($(this).attr('route_id'));
    $('.edit #id_rate_D').val($(this).attr('rate_D'))

    $('#DeliveryRateModal').modal('show');

    //$('#id_direction').html('<option value>-----------</option>');

    $('.loading').removeClass('show');

  //})
})

function capFirstLetter(string_val){
  new_string = string_val.charAt(0).toUpperCase() + string_val.slice(1)
  return new_string
}

$('body').on('change', '#id_service_chain', function(){
    //alert($(this).val());

    if ($(this).val() != ''){

      $('#id_direction').html('<option value>Loading...</option>');

      $.get('', {'service_chain_id': $(this).val()}, function(data){
          var route_direction = data.route_direction;

          var directions = route_direction.split('_');

          //clear options
          $('#id_direction').html('<option value>-----------</option>');

          for (i=0; i<directions.length; i++){
            $('#id_direction').append('<option value='+directions[i]+'>'+capFirstLetter(directions[i])+'</option>');
          }
      })
    }
})
