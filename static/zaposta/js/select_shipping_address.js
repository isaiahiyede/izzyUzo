
$('#add_address').validate();

$('#show_add_address_modal').click(function(){
        $('#addaddr').find('#id_action').val('add_address')
        $('#addaddr').modal('show');
});


function process_address_form() {
    if ($('#add_address').valid()) {
                //$('#add_alert').html("Saving... Please wait");
                $('.loading').addClass('show');
                var form_values = $('#add_address').serialize()+'&'+$.param({'add_address': 'add_address'});
                $.post('', form_values, function(data){
                        if (data.result != 'fail'){
                            //$('#addresses_div').replaceWith(data);
                            //$('#add_alert').html("Address successfully created");
                            location.reload();
                        }else{
                            //$('#alert').css('color', 'red !important');
                            $('#add_alert').html(data.alert);
                        }
                });
                $('.loading').removeClass('show');
        }
}

$('body').on('click', '#add_shipping_address', function(){
        process_address_form();
        return false;
});

// function un_select_address(this){
//   //this.parent().parent().find('.panel.addr').removeClass('active');
//   this.toggleClass('active');
//   $('#p_select_address').html("");
// }

// $('.credit.two .panel.addr.two').click(function () {
// alert('here')
// })

$('.addr_chkbx').change(function(){

        if (confirm('Are you sure you want to use this address?')) {
          $('.loading').addClass('show');
          $(this).parent().parent().find('.panel.addr').toggleClass('active');
          $(this).toggleClass('active');
          if (this.checked){
            //$('#p_select_address').html("Please wait...");
            var address_id = $(this).attr('address_id');
            $.get('', {'address_id': address_id, 'select_address': 'select_address'}, function(data){
                $('#p_select_address').html(data.result);
                $('#p_select_address').css('color', 'green');

            });
          }else{
            $('#p_select_address').html("");
          }
          $('.loading').removeClass('show');

        }else{
          $(this).prop('checked', false)
        }


});

$('.edit.address').on('click', function (){
      $(this).parent().find('.panel.addr').removeClass('active');
      $('#p_select_address').html("");

	    var id = $(this).attr('id');
	    var edit_address = 'edit_address';
	    $.get('', {'id': id, 'edit_address': edit_address}, function(data){
  		if (data.result != 'fail'){
                  $('#addaddr').replaceWith(data);
                  $('#addaddr').show();
                   $('.loading').removeClass('show');
                  //activate_custom_select();
                  //$('#shadow').fadeTo(200,0.7);
                  }
  	  });
      $('#addaddr').find('#id_action').val('edit_address|'+id);
});

$('.delete.address').on('click', function(){
        var parent_div = $(this).parent();
        //var deleteAddress = confirm('Are you absolutely sure you want to delete this item?');
        if (confirm('Are you absolutely sure you want to delete this item?')) {
                $('.loading').addClass('show');
                var id = $(this).attr('id');
                var delete_address = 'delete_address';
                $.get('', {'id': id, 'delete_address': delete_address}, function(data){
                    if (data.result == 'Ok'){
                        parent_div.remove()
                        //$('#addresses_div').replaceWith(data);
                        //$('#alert').html("Address deleted successfully");
                        $('.loading').removeClass('show');
                    }
                });
        }
        return false;
});

//$('.edit.address').on('click', function(e){
//        e.preventDefault();
//        $('#addaddr').find('#id_action').val('edit_address')
//
//        $.ajax({
//                url: '',
//                method: GET,
//                data: {},
//                success: function(data){
//                      $('#addaddr').replaceWith(data)
//                      $('#addaddr').show();
//                }
//        })
//        return false;
//});


//$('#add_shipping_address').on('click', function(){
//        console.log("working here");
//        $('#add_alert').html("Saving... Please wait");
//        var form_values = $('#add_address').serialize()+'&'+$.param({'add_address': 'add_address'});
//        $.post('', form_values, function(data){
//                if (data.result == 'success'){
//                    $('#add_alert').html(data.result);
//                    location.reload();
//                    //$('#addresses_div').replaceWith(data);
//                    //$('#add_alert').html("Address successfully created");
//                }else{
//                    //$('#alert').css('color', 'red !important');
//                    //$('#add_alert').html(data.alert);
//                    $('#add_alert').html("Error. Please complete the highlighted fields below");
//                    $('#addaddr').replaceWith(data);
//
//                    activate_custom_select();
//                    $('#addaddr').show();
//                }
//        });
//
//        return false;
//});

$('#add_addr_btn').on('click', function(){
        $("#"+$(this).attr('rel')).show();
        //activate_custom_select();
});



//$('body').on('click', '#save_edit_address', function(){
//    $('#alert').html("Saving...");
//    var address_id = $(this).attr('address_id');
//    var form_values = $('#edit_address').serialize()+'&'+$.param({'save_edit_address': 'save_edit_address', 'edit_address_id': address_id});
//    $.post('', form_values, function(data){
//        if (data.result != 'fail'){
//            //$('#addresses_div').replaceWith(data);
//            $('#alert').html("Address edited successfully");
//            location.reload();
//        }else{
//            //$('#alert').css('color', 'red !important');
//            $('#alert').html(data.alert);
//        }
//    });
//});

function validateAddressSelection(next_page){
        var p_select_address = $('#p_select_address').html();

        //if ((p_select_address.indexOf("successful") > -1)) {
        if ((p_select_address.indexOf("successfully") > -1)) {
                window.location.href = next_page;
        }else{
                $('#p_select_address').html("Please select a shipping address before you proceed to the next page.");
                $('#p_select_address').css('color', 'red');
        }
        return false
}
