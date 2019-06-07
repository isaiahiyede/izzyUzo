


 //    function showSuggestedBoxWidget(selectedBox){
	// 	//var selectedBox = $('#selecteaboxId option:selected').val();
 //        //console.log(selectedBox);
	// 	var divs = document.getElementsByName("SuggestedBoxWidget");
	// 	for (var i = 0; i < divs.length; i++) {
	// 		divs[i].style.display = 'none';
	// 	}
	// 	$("#SuggestedBoxWidget"+selectedBox).show();
	// 	return false;
	// }

 //    $(".btn.predefined_box").on('click', function(){
 //        var qty_val = $('#id_quantity option:selected').val();
 //        var box_id = $(this).attr('data_box_id');
 //        $(this).parent().find("#id_box_quantity").val(qty_val);
 //        $(this).parent().find("#id_selectabox").val(box_id);

 //        $("#box_form_"+box_id).submit();

 //    });
 //    //function addPreConfiguredBox(box_id){
 //    //    //var btn = $(this).parent().parent().parent().parent()
 //    //    var qty_val = $('#id_quantity option:selected').val();
 //    //    $("#id_box_quantity_"+box_id).val(qty_val);
 //    //    //var box_id = $(this).attr('data-box-id');
 //    //    console.log(qty_val);
 //    //    $("#box_form_"+box_id).submit();
 //    //    //document.getElementById("box_form_"+box_id).submit();
 //    //    //document
 //    //
 //    //}

 //    $(".delivery_method_radio").click(function(){
 //        //console.log("getting here");
 //        $(this).parent().parent().find('.search_outer').show();
 //    });

	// //$('input[type="radio"]').click(function(){
	// //	var radio = $(this);
	// //	var selectOptionDiv = radio.attr("rel");
	// //	console.log(selectOptionDiv);
	// //	var divs = document.getElementsByName("locations");
	// //	for (var i=0; i <divs.length; i++) {
	// //		divs[i].style.display = 'none';
	// //	}
	// //	$("#"+selectOptionDiv).show();
	// //
	// //	$("#id_delivery_zone").val("");
	// //	$("#id_delivery_city").val("");
	// //})

	// function updateLocalShippingCost(select_val){
 //        //console.log(select_val);
	// 	//console.log(select_innerHTML);
	// 	//$("#id_delivery_zone").val(select_val);
	// 	//$("#id_delivery_city").val(select_val);
 //        $("#id_location_info").val(select_val)



	// }
	// //function updateLocalShippingCost(select_id){
	// //	var select_field = $("#"+select_id);
	// //	console.log(select_field);
	// //	var s_field_val = select_field.val();
	// //	var s_field_loc = $("#"+select_id+">option:selected").html();
	// //	//console.log(s_field_val);
	// //	//console.log(s_field_loc)
	// //	$("#id_delivery_zone").val(s_field_val);
	// //	$("#id_delivery_city").val(s_field_loc);
	// //
	// //
	// //
	// //}


	// function showAlert(){
	// 	var location = $("#id_location_info").val();
	// 	if (location != "") {
	// 		return true;
	// 	}
	// 	alert("Please choose a location before you proceed.");
	// 	return false;
	// }


	// function validateDeliveryOption(){
	// 	var dvm = $("input[name='delivery_method']:checked").val();
	// 	//alert(dvm);
	// 	if (dvm == undefined) {
	// 		alert("Please choose a delivery option before you proceed.");
	// 		return false;
	// 	}
	// 	if (dvm == "AF - HD" || dvm == "SF - HD" ) {
	// 		return true;
	// 	}
	// 	else{
	// 		if (dvm == "AF - OP" || dvm == "SF - OP") {

	// 			return showAlert();
	// 		}
	// 		else{

	// 			return showAlert();
	// 		}
	// 		return false;
	// 	}
	// 	return false;
	// }


 //    $("#proceed_btn").click(function(){
 //        if (validateDeliveryOption()){
 //                $("#proceed_form").submit()
 //        }
 //        return validateDeliveryOption();
 //    })













    function showSuggestedBoxWidget(selectedBox){
		//var selectedBox = $('#selecteaboxId option:selected').val();
        //console.log(selectedBox);
		var divs = document.getElementsByName("SuggestedBoxWidget");
		for (var i = 0; i < divs.length; i++) {
			divs[i].style.display = 'none';
		}
		$("#SuggestedBoxWidget"+selectedBox).show();
		return false;
	}

    $(".btn.predefined_box").on('click', function(){
        var qty_val = $('#id_quantity option:selected').val();
        var box_id = $(this).attr('data_box_id');
        $(this).parent().find("#id_box_quantity").val(qty_val);
        $(this).parent().find("#id_selectabox").val(box_id);

        $("#box_form_"+box_id).submit();

    });
    //function addPreConfiguredBox(box_id){
    //    //var btn = $(this).parent().parent().parent().parent()
    //    var qty_val = $('#id_quantity option:selected').val();
    //    $("#id_box_quantity_"+box_id).val(qty_val);
    //    //var box_id = $(this).attr('data-box-id');
    //    console.log(qty_val);
    //    $("#box_form_"+box_id).submit();
    //    //document.getElementById("box_form_"+box_id).submit();
    //    //document
    //
    //}

    $(".delivery_method_radio").click(function(){
        //console.log("getting here");
        $(this).parent().parent().find('.search_outer').show();
    });

	//$('input[type="radio"]').click(function(){
	//	var radio = $(this);
	//	var selectOptionDiv = radio.attr("rel");
	//	console.log(selectOptionDiv);
	//	var divs = document.getElementsByName("locations");
	//	for (var i=0; i <divs.length; i++) {
	//		divs[i].style.display = 'none';
	//	}
	//	$("#"+selectOptionDiv).show();
	//
	//	$("#id_delivery_zone").val("");
	//	$("#id_delivery_city").val("");
	//})

	function updateLocalShippingCost(select_val){
        //console.log(select_val);
		//console.log(select_innerHTML);
		//$("#id_delivery_zone").val(select_val);
		//$("#id_delivery_city").val(select_val);
        $("#id_location_info").val(select_val)



	}
	//function updateLocalShippingCost(select_id){
	//	var select_field = $("#"+select_id);
	//	console.log(select_field);
	//	var s_field_val = select_field.val();
	//	var s_field_loc = $("#"+select_id+">option:selected").html();
	//	//console.log(s_field_val);
	//	//console.log(s_field_loc)
	//	$("#id_delivery_zone").val(s_field_val);
	//	$("#id_delivery_city").val(s_field_loc);
	//
	//
	//
	//}


	function showAlert(){
		var location = $("#id_location_info").val();
		if (location != "") {
			return true;
		}
		alert("Please choose a location before you proceed.");
		return false;
	}


	function validateDeliveryOption(){
		var dvm = $("input[name='delivery_method']:checked").val();
		//alert(dvm);
		if (dvm == undefined) {
			alert("Please choose a delivery option before you proceed.");
			return false;
		}
		if (dvm == "AF - HD" || dvm == "SF - HD" ) {
			return true;
		}
		else{
			if (dvm == "AF - OP" || dvm == "SF - OP") {

				return showAlert();
			}
			else{

				return showAlert();
			}
			return false;
		}
		return false;
	}


    $("#proceed_btn").click(function(){
        if (validateDeliveryOption()){
                $("#proceed_form").submit()
        }
        return validateDeliveryOption();
    })




 $('#select_all_items').on('click', function(event){
      if (this.checked) {
        $('.selected-items').each(function(){
          $(this).prop('checked', true);
        });
    }
    else
    {
      $('.selected-items').each(function(){
          $(this).prop('checked', false);
        });
    }
  })


 // function check_item_selection(){
 //  var choice = $('#id_packaging_choice');
 //  var count  = document.getElementByClassName('selected_item').length;
 //  alert(count);
 //  return false;

 //  if ( choice === 'enterdimension' && selected_items.length < 1){
 //    alert('you have not selected any items yet');
 //    return false;
 //  }
 // }



      $("#i_accept").click(function(){
        //$('#id_i_accept_no_invoice').val('yes');
        //$("#id_no_invoice").trigger('click');
        $("#id_no_invoice").attr('disabled', 'disabled');
        //$("#id_no_invoice").attr('checked', 'checked');
        $("#no_invoice_text").html("Yes, I accept I don't have invoices for the items listed above.");
        $("#no_invoice_text").css('color', 'red');
        $("#id_i_accept_no_invoice").val('yes');
        $('#id_upload_invoices').removeClass('hidden');
        //hide upload invoice container
        $(".upload_invoice.container").hide();

		$("#id_no_invoice").prop('checked', false);
		show_hide_warning()
		$("#id_no_invoice").attr('checked', true);

		return false;
      });

      //$(".inpp").change(function(){
        $("body").on('change', '.inpp', function(){
          var filename = $(this).val().replace(/.*(\/|\\)/, '');
          $(this).parent().parent().find('.inpl').html(filename);
          var div_inner = '<div class="upld_outer">'+
                        '<div class="upld">'+
                            '<input type="file" name="pic" class="inpp" id="upload-image" accept="image/*,.pdf">'+
                        '</div>'+
                        '<label class="inpl file_name">Attach Another Invoice</label>'+
                    '</div>'
          $(".col-md-12.upload_div").append(div_inner);

          //hide i don't have invoice div
          $(".noinvoice").hide();
        });

	function show_hide_warning(){
  // $('#id_no_invoice').is(':checked') ? $('#no_invoice_warning').removeClass('hidden') : $('#no_invoice_warning').addClass('hidden');
    if ($('#id_no_invoice').is(':checked')){
      $('#no_invoice_warning').removeClass('hidden');
      $('#id_upload_invoices').addClass('hidden');
      } else {
        $('#no_invoice_warning').addClass('hidden');
        $('#id_upload_invoices').removeClass('hidden');
      }
    }




    function update_choice(choice,value){
      $('#id_packaging_choice').val(value);
      $('#id_packaging_choice').attr('name', choice);

      var input_id_list = ['id_box_length','id_box_width','id_box_height','id_box_weight_Actual','id_weight_unit_0','id_weight_unit_1']

      for (id = 0; id < input_id_list.length; id++ ){
          $('#' +input_id_list[id]).attr('required', false)
        }

      if (choice === "enterdimension"){

        for (id = 0; id < input_id_list.length; id++ ){
          $('#' +input_id_list[id]).attr('required', true)
        }
        $('#package_dimension').removeClass('hidden');
        $('#title_2').removeClass('hidden');
        $('#title_1').addClass('hidden');
        $('#billmelater_info').addClass('hidden');
        $('.item_selector').removeClass('hidden');
        $('.item_selector_all').removeClass('hidden');

      } else if (choice === "accept_do_later") {
        $('#billmelater_info').removeClass('hidden');
        $('#package_dimension').addClass('hidden');
        $('#title_2').addClass('hidden');
        $('#title_1').addClass('hidden');
        $('.item_selector').addClass('hidden');
        $('.item_selector_all').addClass('hidden');
      } else {
        $('#billmelater_info').addClass('hidden');
        $('#package_dimension').addClass('hidden');
        $('#title_2').addClass('hidden');
        $('#title_1').removeClass('hidden');
        $('.item_selector').addClass('hidden');
        $('.item_selector_all').addClass('hidden');
      }

      return true;
    }



    function count_selected_items(){
      var choice = $('#id_packaging_choice').attr('value');
      var checked_item  =  $("#item_selection_table input[name='selected_item']:checked").length;
      if (choice == "enterdimension" && checked_item < 1) {
        alert("You have not selected any item for this package");
        return false;
      }
      return true;
     }


      function validateItemsCountAndInvoice(){

        var no_invoice_checkbox_state = $("#id_no_invoice").is(':checked');
        no_invoice_checkbox_state ? $('#id_i_accept_no_invoice').val('yes') : $('#id_i_accept_no_invoice').val('no');
        var selected_files_count = 0;
        $('.inpl.file_name').each(function(){
          file_name = $(this)[0].innerHTML;
          if (!(file_name == 'Attach Invoice') && !(file_name == 'Attach Another Invoice')) {
            selected_files_count++;
          }
        });
        var items_count = $('tr.tr_item').length;
        if (items_count > 0) {
            if (selected_files_count > 0 || no_invoice_checkbox_state == true){
              $("#id_i_accept_no_invoice").attr('disabled', false);
                return count_selected_items();
                $("#upload_invoices").submit();
                //$('#id_upload_invoices').attr('disabled', 'disabled')
                // $("#upload_invoices").submit();

            } else {
              alert("Please upload invoices for your items / Accept i don't have an invoice before you proceed to the next page.");
              return false;
            }
            return false;
        }
        alert("Please add 1 or more items before you proceed to the next page.");
        return false;
        //return items_count > 0;
      }
