	  max_usps_pkg_weight_lbs = 70;

      jQuery.validator.addMethod("numericCheck", function (value, element){
	    return this.optional(element) || /^[0-9\.]+$/.test(value) && (parseFloat(value) > 0);
		}, "* Value must be a postive integer");

	  $("#add_item_form").validate({
			ignore: [],
			//rules: {
			//  naira_value: "required"
			//}
	  });

	  $("#customized_box_form").validate({
			rules: {
			  box_length: {numericCheck : true },
			  box_width: {numericCheck : true },
			  box_height: {numericCheck : true },
				box_weight: {numericCheck: true},
			  naira_value: {numericCheck: true }
			}
	  });

	  $("#consd_weight_form").validate({
			rules: {
			  consd_weight: {numericCheck: true}
			}
	  })

	//  jQuery.validator.addClassRules('inp1', {
	//	required: true,
	//	minlength: 5
	//  });

      //$(".custom-option").on("click", function(){
	  $("body").on("click", ".custom-option", function(){

		    var selected_val = $(this).data("value");
            var select_type = $(this).parents(".custom-select-wrapper").find("select").attr('id');
			//console.log(state_id)
			//if (select_type == "box_type"){
			//  $("#"+selected_val).show();
			//  if (selected_val == "predefined_box") {
			//	$("#customized_box").hide()
			//  }else{
			//	$("#predefined_box").hide()
			//  }
			//
			//}
            if (select_type == "export_category") {

				$('.loading').addClass('show');

				$.ajax({
				  url: '',
				  type: 'GET',
				  //dataType: "json",
				  data: {'export_category': selected_val},
				  success: function(data){
					//$('#export_sub_category').html()
					//console.log(data.response);
					//$('#export_sub_category').html(''); commented because of jquery validation
					$('#export_sub_category').html('<option value=""></option>');
					$("#export_sub_category").parent().find('.custom-options').html('');
					$("#export_sub_category").parent().find('.custom-select-trigger').html('Select From Export Sub-Category');

					$.each($.parseJSON(data.response), function(index, element){
					  $('#export_sub_category').append('<option value="'+element.id+'"data-content="'+element.content+'">'+ element.name+'</option>');
					  $("#export_sub_category").parent().find('.custom-options').append('<span class="custom-option" data-value="'+element.id+'"data-content="'+element.content+'">'+ element.name+'</span>')
					  //$("#export_sub_category").parent().parent().find('.col-md-6.txt').append('<p>'+element.content+'</p>')
					  //console.log(element.content);
					});

					//other subcategory
					$('#export_sub_category').append('<option value="other" data-content="Other sub category not listed here">Other</option>');
					$("#export_sub_category").parent().find('.custom-options').append('<span class="custom-option" data-value="other" data-content="Other sub category not listed here">Other</span>')

					$('.loading').removeClass('show');

				  }
				})
            }
			else if (select_type == "export_sub_category") {
			  $sub_category_info = $("#export_sub_category").parent().parent().parent().parent().find('.col-md-6.txt');

			  if (selected_val == 'other') {
				$('#other_entry_div').removeClass('hidden');
				$sub_category_info.html('');
              }else{
				var alert_icon = '<span class="qinfo" style="margin-right:0px;"><i class="fa fa-info"></i></span>'
				//console.log('$(this).data("content"): '+$(this).data("content"))
				$sub_category_info.html(alert_icon + '<span>'+$(this).data("content")+'</span>');
				$('#other_entry_div').addClass('hidden');
			  }
			}

			else if (select_type == "id_usps_delivery_speed") {

			  	$('#courier_speed_popup').find('.custom-options span[data-value="'+$(this).data('value')+'"]').trigger('click');

				$('#id_delivery_speed_text').val($(this).data('value'))
            }

			else if (select_type == "id_delivery_speed") {

			  $("#id_delivery_speed_text").val($(this).data('value'));
			  $("#id_save_pkg_box").trigger('click');
			//  //console.log('$(this).data("content"): '+$(this).data("content"))
			//  //$("#export_sub_category").parent().parent().parent().parent().find('.col-md-6.txt').html('<p>'+$(this).data("content")+'</p>');
			//  $("#delivery_speed_sub_info").html('<p>'+$(this).data("duration")+'</p>');

			}



	  });

	  $("body").on("click", ".active-result", function(){
		$select_element = $(this).parent().parent().parent().parent().find('select');
		var select_id = $select_element.attr('id');
		var selected_text = $(this).text();//data("option-array-index");
		var selected_option = $(this).data("option-array-index");

		  if (select_id == "id_dest_country" || select_id == "id_retn_country") {
				var country_state_id = $select_element.attr('data-state');
				//console.log(country_state_id)
				//console.log(selected_text)
				if (select_id == "id_dest_country") {
                    $("#dest_country_val").val(selected_text);
					$("#dest_zipcode_val").val($('#id_dest_postal_code').val());
                }

				$('.loading').addClass('show');

				var $state_id = $("#"+country_state_id);
				$.ajax({
				  url: '',
				  type: 'GET',
				  //dataType: "json",
				  data: {'get_country_states': selected_text},
				  success: function(data){
					//$('#export_sub_category').html()
					//console.log(data.response);
					//clear existing values
					$state_id.html('');
					//$state_id.parent().find('.custom-options').html('');
					//$state_id.parent().find('.custom-select-trigger').html('Select State');
					//$state_id.parent().html('');

					$.each($.parseJSON(data.response), function(index, element){
					  $state_id.append('<option value="'+element.id+'">'+ element.name+'</option>');
					  //$state_id.parent().find('.custom-options').append('<span class="custom-option" data-value="'+element.id+'">'+ element.name+'</span>')
					});
					$state_id.trigger('chosen:updated');

					$('.loading').removeClass('show');

				  }
				})
            }
	  });


	function addSerialNumberToTr(table_id){
		$('#'+table_id+' tr').each(function(index){
			var count = index
			if (count > 1) {
				count = index++;
			}
			$(this).find('td:nth-child(2)').html(count);
		});
	};

	function hideItemDeleteBtn(table_id){
		$('#'+table_id+' tr').each(function(index){
			$(this).find('td:nth-child(5)').html('');
		});
	};

	function totalValueOfItems(table_id) {
		var total_value_of_items = 0
        $('#added_items_display').find('#'+table_id+' tr').each(function(index){
		  if (index > 0) {
			  var item_values = $(this).find('td:nth-child(4)').text().split('=');
			  total_value_of_items += parseFloat(item_values[2].split('↵')[0])
          }
		});
		return total_value_of_items;
    }


	function showDocumentsOrPkgDimension() {
        var tr_length = $('#item_listing tr').length;
		if ( (tr_length == 2) && $('#item_listing tr:contains("Document")').size() > 0 ){
		  $('#documents_div').removeClass('hidden');
		  $('#pkg_dimension_div').addClass('hidden');
		  //console.log('yaaay1')
		} else {
		  $('#documents_div').addClass('hidden');
		  $('#pkg_dimension_div').removeClass('hidden');
		  //console.log('yaaay2')
		}

    }

	$(document).ready(function(){
	  showDocumentsOrPkgDimension()
	});

    function getCSRFValue() {
        return $("input[name='csrfmiddlewaretoken']").val()
    }

	$("body").on("click", "#add_item_btn", function(){
		//validateExportCategory();
		$("#add_item_form").validate();
		if ($('#add_item_form').valid()){
			  //ignoreCsrfProtection();
			  $('.loading').addClass('show');
			  var category = $('#export_category option:selected').val();
			  var category_text = $('#export_category option:selected').text();
			  var sub_category = $('#export_sub_category option:selected').val();
			  var sub_category_text = $('#export_sub_category option:selected').text();
			  var naira_value = parseFloat($("#id_naira_value").val());
			  var other_entry = $('#id_other_entry').val();
			  //var num_of_items = parseInt($('#item_listing p').length);
			  $.ajax({
					url: '',
					type: 'POST',
					data: {'add_item': 'add_item', 'category': category,
							'sub_category': sub_category, 'naira_value': naira_value,
							'other_entry': other_entry, 'csrfmiddlewaretoken': getCSRFValue()},
					success: function(data){
					    if (data.other_entry) {
								$('.loading').removeClass('show');
								alert("We currently don't ship this item. However, we will consider it and use it to improve what people can ship through our webiste. Please check back after 48 hours. Thank you for your understanding.")
		                      } else {
									// var item_sn = num_of_items+1 ;
								   //  $("#item_listing").find('tbody').append('<p>\
								   //			  <span>' + item_sn +'. ' + category_text +' | ' + sub_category_text + ' | ' + '=N='+naira_value +'</span>\
								   //			  &nbsp &nbsp <a href="#" obj_id="'+ data.pk + '" class="delete_option"><i class="fa fa-trash-o"></i></a>\
								   //			</p>')

								 $("#item_listing").find('tbody').append("<tr><td class='td_chkbx hidden'><input name='item' value='"+data.pk+"' type='checkbox'/></td><td>"+category_text+"</td>\
																		 <td>"+sub_category_text+"</td>\
																		 <td>&#8358;"+naira_value+"</td>\
																		 <td><a href=?delete_item="+data.pk+"\
																		 obj_id="+data.pk+" class='delete_obj'><i class='fa fa-trash-o'></i></a></td>")

								 showDocumentsOrPkgDimension();
								 //addSerialNumberToTr('item_listing')
								 $('.loading').removeClass('show');

								 var select_list = {'#export_category': 'Select From Export Category',
						 											'#export_sub_category': 'Select From Export Sub-Category'}

								//  for (key in select_list){
								// 		var key_val = select_list[key]
								// 		$(key).html('<option value=""></option>');
								 // 	 	$(key).parent().find('.custom-options').html('');
								 // 	 	$(key).parent().find('.custom-select-trigger').html(key_val);
								 //  }
								 $('#id_naira_value').val('')

				    }
				}
		  })

		return false;
		//$("#item_desc_form").valid();
		}
	});

	$('.delete_obj').click(function(){
	  return confirm('Are you sure you want to delete this item?');
	})

	function getCheckedCheckboxes(div_container){
        var checkbox_values = [];
		$('#'+div_container).find('input:checked').each(function(){
		  //checkbox_values += $(this).val() + '|';
		  checkbox_values.push($(this).val())
		});
		return checkbox_values;
      }


	  //  $('.form.two .checkbox.th label').click(function (){
	//	  console.log('here');
	//	  $(this).parent().toggleClass('active');
	//	  $('.form.addrs.th#newaddrs-th').toggleClass('active');
	//  });
	//
	//  $("#saved_dest_address").click(function(){
	//	$('.col-md-12.checkbox.dest_addresses').toggleClass('active');
	//  });

	  $('body').on('click', '.docs', function(){
		  //areas
		  $('.docs_envelope').prop('checked', false);
		  $(this).parent().find('.docs_envelope').prop('checked', true);

		  //set default value of 1 for documents
		  $('#box_dimension').find('input').each(function(){
			$(this).val('1')
		  })
		  showBoxWeight('box_dimension');
	  });


	  $("body").on('click', ".label_dest_add", function(){
		//$('.dest_chkbx').prop('checked', false);
		$(this).parent().find('.dest_chkbx').prop('checked', false);
		if ($(this).attr('data-country')) {
		  //console.log($(this).attr('data-country'));
		  $("#dest_country_val").val($(this).attr('data-country'));
		  $("#dest_zipcode_val").val($(this).attr('data-zip-code'));
		}

		//var chkbx = $(this).parent().find('.dest_chkbx');
		//var chkbx_id = chkbx.attr('data-id');
		//console.log('chkbx_id: '+chkbx_id);
		//if ((chkbx.is(':checked'))) {
		//  chkbx.prop('checked', false)
		//  console.log("uncheck checked chkbox")
		//}

	  });

	  $("body").on('click', ".label_saved_new", function(){
		//uncheck all saved_new_checkboxes
		$(this).parent().parent().find('.saved_new_chkbx').prop('checked', false);
		//check this checkbox
		$(this).parent().find('.saved_new_chkbx').prop('checked', true);
		//hide all checkbox th
		$(this).parent().parent().find('.col-md-12.checkbox.th').removeClass('active');

		var label_id = $(this).attr('for');

		if (label_id == 'enter_new_address' || label_id == 'new_return_address') {
		  //console.log('label_id: '+label_id);
		  $(this).parent().parent().find('.col-md-12.checkbox.dest_addresses').removeClass('active')

		  //uncheck all address destiantions
		  $(this).parent().parent().find('.dest_chkbx').prop('checked', false);

		  $(this).parent().parent().parent().find('.form.addrs.t#'+$(this).attr('data-form-id')).addClass('active');

		}else{
		  $(this).parent().parent().parent().find('.form.addrs.t#'+$(this).attr('data-form-id')).removeClass('active');
		  $(this).parent().parent().find('.col-md-12.checkbox.dest_addresses').addClass('active')
		  //uncheck all address destiantions

		  $(this).parent().parent().find('.dest_chkbx').prop('checked', false);
		}
		$(this).parent().addClass('active');
		return false;
	  });


	  //validations for creating boxes
	//  function validatePreDefinedBox(){
	//	var export_box = $('#export_categories option:selected').val();
	//	var export_sub_category = $('#export_sub_category option:selected').val();
	//	//customized_box = '';
	//	if (export_box == '' || export_sub_category == ''){
	//	  alert("Please select a PreDefined Box and from Sublist");
	//	  return false;
	//	}
	//  }


	  function validateExportCategory(){
		var export_box = $('#export_category option:selected').val();
		var export_sub_category = $('#export_sub_category option:selected').val();
		//customized_box = '';
		if (export_box == '' || export_sub_category == ''){
		  alert("Please select a category from export category and sub-category.");
		  return false;
		}
		//$("#customized_box_form").valid();

	  }

	//  function validateCustomizedBox(){
	//	$("#customized_box_form").valid();
	//  }

	  function validateBoxDestinationSaved(){
		//console.log($("#saved_dest_address").parent().parent().find('.dest_chkbx'))
		//var $chkbxes = $("#saved_dest_address").parent().parent().find('.dest_chkbx');
		//$.each($chkbxes, function(index, element){
		//  console.log('element: '+ element);
		//});

		//var address_chkb = $("#saved_dest_address").parent().parent().find('.dest_chkbx').prop('checked');
		var address_chkb = $("#saved_dest_address").parent().parent().find('.dest_chkbx').is(':checked');
		//console.log(address_chkb)
		//console.log('address chkd: '+address_chkb);
		if (!(address_chkb)) {
		  alert("Please select package destination from your saved address(es)")
		  return false;
		}
		//return address_chkb;
	  }

	  function validateBoxDestinationNew() {
		var _validator = $("#customized_box_form").validate();
		fields_to_validate = ['id_dest_full_name', 'id_dest_address_line_1', 'id_dest_city', 'id_dest_country', 'id_dest_state'];

		$.each(fields_to_validate, function(index, element){
		  _validator.element('#'+element);
		});
		//console.log('$("#customized_box_form").valid();: '+$("#customized_box_form").valid());
		//return $("#customized_box_form").valid();
	  }

	//  function validateBoxDeliverSpeed(){
	//	var delivery_speed = $('#id_delivery_speed option:selected').val();
	//	//customized_box = '';
	//	if (delivery_speed == ''){
	//	  alert("Please select a delivery speed for your package");
	//	  return false;
	//	}
	//  }

	  function validateBoxReturnAddSaved(){
		var address_chkb = $("#saved_return_address").parent().parent().find('.dest_chkbx').is(':checked');
		//console.log('address: '+address_chkb);
		if (!(address_chkb)) {
		  alert("Please select return address from your saved address(es)")
		  return false;
		}
		//return address_chkb;
	  }

	  function validateBoxReturnAddNew() {
		var _validator = $("#customized_box_form").validate();
		fields_to_validate = ['id_retn_full_name', 'id_retn_address_line_1', 'id_retn_city', 'id_retn_country', 'id_retn_state'];

		$.each(fields_to_validate, function(index, element){
		  _validator.element('#'+element);
		});
		//return $("#customized_box_form").valid();
	  }

	  //validations for creating boxes
	  function ignoreCsrfProtection(){
            function csrfSafeMethod(method){
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
                }
                $.ajaxSetup({
                    beforeSend: function(xhr, settings){
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain){
                            xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
                        }
                    }
                });
        }

		function getCourierDeliveryText(service_duration_desc){
		  var service_text_list;
		  if (service_duration_desc.indexOf("1-Day") > -1) {
			service_text_list = service_duration_desc.split(' 1-Day')
		  }
		  else if (service_duration_desc.indexOf("2-Day") > -1) {
			service_text_list = service_duration_desc.split(' 2-Day')
		  }

		  $("#id_delivery_speed_text").val(service_text_list[0]);
		  return service_text_list[0]
		}
	  //create export box


	  //function create_box_form(){
	  $("#id_save_pkg_box").click(function(event){

        var box_weight_vals = calculateBoxDimWeight('box_dimension');
        //Math.ceil because usps requires int
        var weight_lbs = Math.ceil(box_weight_vals[0]);

        if (weight_lbs > max_usps_pkg_weight_lbs){
            alert("Please provide/modify your package dimension.");
            return false;
        }
		//event.stopPropagation()
		//console.log('length: '+$("#item_listing tr").length)
		if ($("#item_listing tr").length < 2) { //2 because of first tr for header
            alert('You need to add one or more items before saving a package.')
			return false;
        }
		//console.log($('.chosen-search').find('input:not([name])').length);
		//console.log($(".chosen-search > :input").length);

		//console.log($(this).form)
		//var pkg_type = $('#box_type option:selected').val();
		//console.log('pkg_type: '+pkg_type);
		//if (pkg_type != ''){
		//  if (pkg_type == 'predefined_box'){
		//	validateExportCategory()
		//  }else{
		//	validateCustomizedBox();
		//  }
		//}else{
		//  alert("Select box type")
		//  return false;
		//}
		//validateExportCategory();

		//$('.chosen-search').find('input').attr('disbaled', 'disabled')

		var $form_obj = $('#customized_box_form');

		//$form_obj.validate({ ignore: ':hidden:not(select)'})
		//$form_obj.validate({ ignore: ':hidden:not(select)' })
		//$form_obj.validate({ ignore: '.valid' })

		$(".chosen-search > :input").attr('name', 'search')
		$form_obj.validate({ ignore: 'input:[name=search]' })
		//$form_obj.validate({ ignore: 'input:not([name])' })
		//$(".chosen-search > :input").addClass('hidden')

		if ($form_obj.valid()) {

			var saved_add_chkb = $("#saved_dest_address").prop('checked');
			var saved_new_chkb = $("#enter_new_address").prop('checked');

			//console.log('saved_add_chkb: '+saved_add_chkb);
			//console.log('saved_new_chkb: '+saved_new_chkb);

			if (saved_add_chkb == false && saved_new_chkb == false){
			  alert("Where is this package going to? Saved or New address?")
			  return false;
			}else{
			  if (saved_add_chkb){
				try{
				  validateBoxDestinationSaved();
				}catch(e){
				}


			  }else{
				validateBoxDestinationNew();
			  }
			}

			//var delivery_speed = $('#id_delivery_speed option:selected').val();
			//if (delivery_speed == '') {
			//  alert("Please select a delivery speed for your package");
			//  return false;
			//}

			var saved_return_chkb = $("#saved_return_address").prop('checked');
			var new_return_address = $("#new_return_address").prop('checked');

			//console.log('saved_return_chkb: '+saved_return_chkb);
			if (saved_return_chkb == false && new_return_address == false){
			  alert("Where do you want this package returned to, if undelivered? Saved or New address?")
			  return false;
			}else{
			  if (saved_return_chkb){
				  validateBoxReturnAddSaved();
			  }else{
				validateBoxReturnAddNew();
			  }
			}

			//usps api query
			var box_length = $("#id_box_length").val();
			var box_width = $("#id_box_width").val();
			var box_height = $("#id_box_height").val();

			//var naira_value = parseFloat($("#id_naira_value").val());
			var naira_value = totalValueOfItems('item_listing');
			//var dollarNairaRate = {% dollarNairaRate %};
			var value_of_content_D = (naira_value / dollar_exchange_rate).toFixed(2);
			//console.log('value_of_content_D: '+value_of_content_D);
			//var box_weight_vals = calculateBoxDimWeight('box_dimension');
			//Math.ceil because usps requires int
			//var weight_lbs = Math.ceil(box_weight_vals[0]);
			//console.log('weight_lbs: '+weight_lbs);
			var dest_country_val = $("#dest_country_val").val();

			var $delivery_speed = $("#id_delivery_speed");
			//initialize select field content
			//$delivery_speed.html('');
			//$delivery_speed.parent().find('.custom-options').html('');
			//console.log('box_length: '+box_length);

			//ignoreCsrfProtection();
			$('.loading').addClass('show');
			$("#courier_speed_popup").modal('show');

			//$("#error_alert").html('Fetching available USPS delivery options. Please, bear with us.');
			//$("#error_alert").removeClass('hidden');

			$.ajax({
			  url: usps_query_url,
			  type: 'POST',
			  data: {'action': 'ShippingEstimate',
					'weight_lbs': weight_lbs, 'destination_country': dest_country_val,
					'box_length': box_length, 'box_width': box_width, 'box_height': box_height,
					'naira_value': naira_value,
					'value_of_content_D': value_of_content_D, 'destZipCode': $('#dest_zipcode_val').val(),
					'usps_delivery_speed': $("#id_delivery_speed_text").val(), 'csrfmiddlewaretoken': getCSRFValue()},
			  success: function(data){
				console.log(data)
//				try{
//				  var service_desc_text1 = data.normal_desc.split('&')[0];
//				  var service_duration1 = data.normal_duration;
//				  var service_cost1     = data.normal_commercial;
//				  var option_val1       = service_desc_text1 + ' - $' + service_cost1;
//
//				  var service_desc_text2 = data.express_desc.split('&')[0].substring(0,25)+'...';
//				  var service_duration2 = data.express_duration;
//				  var service_cost2     = data.express_commercial;
//				  var option_val2       = service_desc_text2 + ' - $' + service_cost2;
//
//				  $delivery_speed.append('<option value="'+option_val1+'"data-duration="'+service_duration1+'">'+ option_val1 +'</option>');
//				  $delivery_speed.append('<option value="'+option_val2+'"data-duration="'+service_duration2+'">'+ option_val2 +'</option>');
//
//				  $delivery_speed.parent().find('.custom-options').append('<span class="custom-option" data-value="'+option_val1+'"data-duration="'+service_duration1+'">'+ option_val1+'</span>');
//				  $delivery_speed.parent().find('.custom-options').append('<span class="custom-option" data-value="'+option_val2+'"data-duration="'+service_duration2+'">'+ option_val2+'</span>');
//
//				  //$("#delivery_speed_sub_info").append('<p>'+element.content+'</p>')
//				}catch(err){
//				  //console.log(err)
//				  var service_duration = data.domestic_description;
//				  var service_cost     = (parseFloat(data.domestic_shipping_charge) + parseFloat(data.total_shipping_cost_D)).toFixed(2);
//				  var option_val       = service_duration + ' - $' + service_cost;
//
//				  //var service_duration_desc = getCourierDeliveryText(service_duration)
//
//				  //console.log(service_duration)
//				  //console.log(service_cost)
//				  //$delivery_speed.append('<option value="'+option_val+'"data-duration="'+service_duration+'">'+ option_val +'</option>');
//				  //$delivery_speed.parent().find('.custom-options').append('<span class="custom-option" data-value="'+option_val+'"data-duration="'+service_duration+'">'+ option_val+'</span>');
//				  if (service_cost != undefined) {
//                    $('#delivery_speed_sub_info').html('Shipping Cost: $'+service_cost);
//					$("#id_delivery_speed_cost").val(service_cost);
//                  }
//
//				}

				  var service_duration = data.description;
				  var service_cost     = (parseFloat(data.shipping_charge) + parseFloat(data.local_intl_freight_cost_D)).toFixed(2);
				  var option_val       = service_duration + ' - $' + service_cost;

				  //var service_duration_desc = getCourierDeliveryText(service_duration)

				  //console.log(service_duration)
				  //console.log('service_cost: '+ service_cost)
				  //$delivery_speed.append('<option value="'+option_val+'"data-duration="'+service_duration+'">'+ option_val +'</option>');
				  //$delivery_speed.parent().find('.custom-options').append('<span class="custom-option" data-value="'+option_val+'"data-duration="'+service_duration+'">'+ option_val+'</span>');
				  if (!(isNaN(service_cost))) {
                    $('#delivery_speed_sub_info').html('Shipping Cost: $'+service_cost);
										$("#id_delivery_speed_cost").val(service_cost);
                  }

				if (data.error_msg) {
				  $("#error_alert").html(data.error_msg);//+ ' Please review your package information.');
				  $("#error_alert").removeClass('hidden');
				  $('#proceed_to_items').addClass('disabled');
				  //$("#modal_save_pkg").addClass('disabled');

				}else{
				  $("#error_alert").addClass('hidden');
				  $('#proceed_to_items').removeClass('disabled');
				  //$("#modal_save_pkg").removeClass('disabled');
				}

				//console.log(getCourierDeliveryText(service_duration))

				//console.log(getCourierDeliveryText(service_duration).length)
				//$('#courier_speed_popup').find('.custom-options span[data-value="'+ getCourierDeliveryText(service_duration)+'"]').trigger('click');

				$('.loading').removeClass('show');
				//return false


				//return false;
			  },
			  error: function(xhr, errmsg, err){
				//console.log(xhr + ' | ' + errmsg + ' | ' + err);
			  }

			});
		}
		//sdfds
		return false
	  });

	  function showItemsPopup() {
		  //var $items_table = $("#itemd_table_div");
  		  $('#items_table_div').html($('#item_listing').clone());
		  $('#items_table_div').find('.td_chkbx').removeClass()
		  $('#items_table_div').find('input:checkbox').attr('checked', 'checked');
		  hideItemDeleteBtn('items_table_div');
		  var pkg_count = parseInt($('#pkgs_listing tr').length) + 1;
		  $('#pkg_count').html('Package '+pkg_count);

		  $('#added_items_display').modal('show');
      }



	  $("#proceed").click(function(){
		//$('#consd_popup').modal('show
		getCheckedCheckboxes('items_table_div');
		var item_chkb = $("#items_table_div").find('input:checkbox').is(':checked');
		if (item_cdhkb) {
            $.ajax({
			  url: '',
			  type: 'POST',
			  data: {'assign_items_to_pkg': 'true', 'checked_items': getCheckedCheckboxes('items_table_div')},
			  success: function(data){

			  },
			})
        }else{
		  alert("Please select one or more items before you proceed.")
		}

	  });


/////////////////////////////////////////////////////////////
	       // Added by James... For Import
/////////////////////////////////////////////////////////////
	 //  $("#calc_shipping_estimate").click(function(){
	 //  	alert('we are here');
		// $('#consd_popup').modal('show')
		// getCheckedCheckboxes('items_table_div');
		// var item_chkb = $("#items_table_div").find('input:checkbox').is(':checked');
		// if (item_cdhkb) {
  //           $.ajax({
		// 	  url: '',
		// 	  type: 'POST',
		// 	  data: {'assign_items_to_pkg': 'true', 'checked_items': getCheckedCheckboxes('items_table_div')},
		// 	  success: function(data){

		// 	  },
		// 	})
  //       }else{
		//   alert("Please select one or more items before you proceed.")
		// }

	 //  });





	  //$('#modal_save_pkg').click(function(){
	  $('#proceed_to_items').click(function(){
		  $('#courier_speed_popup').modal('hide')
		  showItemsPopup();
		  //$('#customized_box_form').submit();
	  });

	  $("#show_courier_speed_modal").click(function(){
		  $('#added_items_display').modal('hide')
		  $('#courier_speed_popup').modal('show')
	  });

	  $('#submit_package').click(function(){
		  $form_obj = $('#customized_box_form');
		  var checked_items = getCheckedCheckboxes('items_table_div');
		  //console.log(checked_items)
		  var item_chkb = $("#items_table_div").find('input:checkbox').is(':checked');
		  //console.log(totalValueOfItems('item_listing'))
		  var total_value_of_items = totalValueOfItems('item_listing')
		  if (item_chkb) {
			//$form_obj.append('<input type="hidden" name="checked_items" value="'+checked_items+'"/>')
			$('#id_checked_items').val(JSON.stringify(checked_items))
			$form_obj.append('<input type="hidden" name="naira_value" value="'+total_value_of_items+'"/>')

			$form_obj.submit();
		  }else{
			alert("Please select one or more items before you proceed.");
		  }

	  });

	  function calculateBoxDimWeight(containing_div){
		var weightFactor 	= 164;
		var lb_to_kg 		= 0.45359;
		var box_length = parseFloat($("#"+containing_div).find("#id_box_length").val());
		var box_width = parseFloat($("#"+containing_div).find("#id_box_width").val());
		var box_height = parseFloat($("#"+containing_div).find("#id_box_height").val());
		var actual_weight_lbs = parseFloat($("#"+containing_div).find("#id_box_weight").val());
    $("#pkg_weight_alert").addClass('hidden')

		var dim_weight_lbs = ((box_length * box_width * box_height) / weightFactor).toFixed(2);
		var higher_weight_lbs = (dim_weight_lbs < actual_weight_lbs) ? actual_weight_lbs: dim_weight_lbs;

		if (higher_weight_lbs < 1) {
		  higher_weight_lbs = 1;

		}else if (higher_weight_lbs >= max_usps_pkg_weight_lbs) {
            //alert("Package weight cannot exceed 70lbs. Please use a package with less weight.")

			$("#pkg_weight_alert").html("Package weight cannot exceed 70lbs. Please use a package with less weight.")
			$("#pkg_weight_alert").removeClass('hidden');
			//return false;
        }

		var higher_weight_kg = (higher_weight_lbs * lb_to_kg).toFixed(2);

        //console.log('weight_lbs: '+weight_lbs);
        //console.log('weight_kg: '+weight_kg)

		return [actual_weight_lbs, dim_weight_lbs, higher_weight_lbs, higher_weight_kg];
	  }
	  function showBoxWeight(containing_div){
			//var weightFactor = 164;
			//var lb_to_kg = 0.45359;
			//var box_length = parseFloat($("#id_box_length").val());
			//var box_width = parseFloat($("#id_box_width").val());
			//var box_height = parseFloat($("#id_box_height").val());
			//
			//var weight_lbs = ((box_length * box_width * box_height) / weightFactor).toFixed(2);
			//var weight_kg = (weight_lbs * lb_to_kg).toFixed(2);
			var box_weight_vals = calculateBoxDimWeight(containing_div);
			var actual_weight_lbs 		= box_weight_vals[0];
			var dim_weight_lbs				= box_weight_vals[1];
			var higher_weight_lbs 		= box_weight_vals[2];
			var higher_weight_kg 			= box_weight_vals[3];

			if (!(isNaN(higher_weight_lbs)) && !(isNaN(actual_weight_lbs))) {
			  //console.log('weight: '+weight_lbs)
				$("#"+containing_div).find('#id_actual_weight').html('Actual Weight: <br/>' + actual_weight_lbs.toString() + 'lbs');
				$("#"+containing_div).find('#id_dim_weight').html('Dimensional Weight: ' + dim_weight_lbs.toString() + 'lbs');
			  $("#"+containing_div).find("#box_higher_weight").html('Higher Weight: ' + higher_weight_lbs.toString() + 'lbs ('+ higher_weight_kg + 'kg)');

				if (containing_div == 'consd_box_dimension') {
				$("#id_consd_weight").val(weight_lbs);
			  }
			}

	  }

	  $("#box_dimension").mouseleave(function(){
		showBoxWeight('box_dimension');
	  });

	  $("#pkg_destination").mouseenter(function(){
		showBoxWeight('box_dimension');
	  });

	  $("#consd_box_dimension").mouseleave(function(){
		showBoxWeight('consd_box_dimension');
	  });


    function show_feedback_popup(msg) {
        $("#feedback_popup").find(".col-md-12.alert").html('<p>'+msg+'</p>')
        $("#feedback_popup").modal('show');
    }
