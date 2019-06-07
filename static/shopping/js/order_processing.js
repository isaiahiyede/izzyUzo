	
$('.button.add_note_user').live('click', function(){
	
	var rel = $(this).attr('rel');
	var product = rel;
	$('#notification'+product).html("Loading...");
	var notes = $('#notes'+rel).val();
	var add_note = 'add_note';
	$.post('', {'notes': notes,'product': product, 'add_note': add_note, 'related_to': '' }, function(data){
		if (data.result != 'fail'){
			$('#product_notes'+product).replaceWith(data);
			$('#notification'+product).html("Saved");
		}
	});
	return false;
});


//ADMIN EDIT FUNCTION
$('#update_default_admin').live('click', function(){
	var id = $(this).attr('rel');
	$('#notification'+id).html("Loading...");
	//var category = $('#category'+id).val();
	//var site_in_view = $('#site_in_view'+id).val();
	var description = $('#description'+id).val();
	var item_number = $('#item_number'+id).val();
	var link = $('#link'+id).val();
	var quantity = $('#quantity'+id).val();
	var listed_price_D = $('#listed_price_D'+id).val();
	var size = $('#size'+id).val();
	var colour = $('#colour'+id).val();
	var final_vendor = $('#final_vendor'+id).val();
	var vendor_order_no = $('#vendor_order_no'+id).val();
	var vendor_tracking_no = $('#vendor_tracking_no'+id).val();
	var purchase_price_D = $('#purchase_price_D'+id).val();
	var shipping_charge_D = $('#shipping_charge_D'+id).val();
	var tax_charge_D = $('#tax_charge_D'+id).val();
	var other_charges_D = $('#other_charges_D'+id).val();
	$.post('', {'update_product': id,
		   'description': description, 'item_number': item_number, 'link': link, 'quantity': quantity, 'listed_price_D':listed_price_D, 'size': size,'colour':colour,
		   'final_vendor': final_vendor, 'vendor_order_no': vendor_order_no,
		   'vendor_tracking_no': vendor_tracking_no, 'purchase_price_D': purchase_price_D,
		   'shipping_charge_D': shipping_charge_D, 'tax_charge_D': tax_charge_D,'other_charges_D': other_charges_D },
		   function(data){
		if (data.result != 'fail'){
			$('#edit-history'+id).replaceWith(data);
			$('#notification'+id).html("Saved");
		}
	});
});
//CLIENT EDIT FUNCTION
$('#update_default_client').live('click', function(){
	var id = $(this).attr('rel');
	$('#notification'+id).html("Loading...");
	var category = $('#category'+id).val();
	var site_in_view = $('#site_in_view'+id).val();
	var description = $('#description'+id).val();
	var item_number = $('#item_number'+id).val();
	var link = $('#link'+id).val();
	var listed_price_D = $('#listed_price_D'+id).val();			
	var quantity = $('#quantity'+id).val();
	var size = $('#size'+id).val();
	var colour = $('#colour'+id).val();
	$.post('', {'update_product': id, 'category': category,'site_in_view': site_in_view, 'description': description,
		   'item_number': item_number, 'link': link,'listed_price_D': listed_price_D, 'quantity':quantity,'size': size,'colour':colour},
		   function(data){
		if (data.result == 'fail'){
			//$('#edit-history'+id).replaceWith(data.alert);
			$('#notification'+id).html(data.alert);
		}else{
			$('#edit-history'+id).replaceWith(data);
			$('#notification'+id).html("Saved");
		}
	});
});
$('#add_pkg').live('click', function(){
	$('#addbox_alert').html("Saving...");
	var order_id = $(this).attr('rel');
	var box_length = $('#box_length'+order_id).val();
	var box_width = $('#box_width'+order_id).val();
	var box_height = $('#box_height'+order_id).val();
	var box_weight_Actual = $('#box_weight_Actual'+order_id).val();
	$.post('', {'add_pkg': 'add_pkg', 'order_id': order_id, 'box_length': box_length, 'box_width': box_width, 'box_height': box_height, 'box_weight_Actual': box_weight_Actual}, function(data){
		if (data.result == 'fail'){
			//$('#box'+order_id).show();
			$('#edit-order-box').show();
			$('#addbox_alert').html(data.alert);
		}
		else {
			//$('#box'+order_id).replaceWith(data);
			//$('#box'+order_id).show();
			$('#edit-order-box').replaceWith(data);
			$('#edit-order-box').show();
			$('#addbox_alert').html("Saved");
		}
	});
	return false;
});
$('.approve_pkg').live('click', function(){
	//$('.ajax-progress').show();
	$('#addbox_alert').html("Loading....");
	var pkg_id = $(this).attr('id');
	var order_id = $(this).attr('rel');
	var approve_pkg = 'approve_pkg';
	$.post('', {'pkg_id': pkg_id, 'order_id': order_id, 'approve_pkg': approve_pkg}, function(data){
		if (data.result != 'fail'){
			//$('.ajax-progress').hide();
			//$('#box'+order_id).replaceWith(data);
			//$('#box'+order_id).show();
			$('#edit-order-box').replaceWith(data);
			$('#edit-order-box').show();
			$('#addbox_alert').html("Approved");
		}
		
	});
	return false;
});
$('.disapprove_pkg').live('click', function(){
	//$('.ajax-progress').show();
	$('#addbox_alert').html("Loading....");
	var pkg_id = $(this).attr('id');
	var order_id = $(this).attr('rel');
	var disapprove_pkg = 'disapprove_pkg';
	$.post('', {'pkg_id': pkg_id, 'order_id': order_id, 'disapprove_pkg': disapprove_pkg}, function(data){
		if (data.result != 'fail'){
			//$('.ajax-progress').hide();
			//$('#box'+order_id).replaceWith(data);
			//$('#box'+order_id).show();
			$('#edit-order-box').replaceWith(data);
			$('#edit-order-box').show();
			$('#addbox_alert').html("Disapproved");
		}
		else{
			//$('#edit-order-box').show();
			$('#addbox_alert').html(data.alert);
		}
	});
	return false;
});
$('.delete_pkg').live('click', function(){
	//$('.ajax-progress').show();
	$('#addbox_alert').html("Loading....");
	var pkg_id = $(this).attr('id');
	var order_id = $(this).attr('rel');
	var delete_pkg = 'delete_pkg';
	$.post('', {'pkg_id': pkg_id, 'order_id': order_id, 'delete_pkg': delete_pkg}, function(data){
		if (data.result != 'fail'){
			//$('.ajax-progress').hide();
			//$('#box'+order_id).replaceWith(data);
			$('#pkg'+pkg_id).hide();
			$('#addbox_alert').html("Deleted");
		}
		else{
			//$('#edit-order-box').show();
			$('#addbox_alert').html(data.alert);
		}
	});
	return false;
});
//ADMIN EDIT ACTIVATOR
$(document).ready(function(){
	$('#edit').live('click', function(){
		product_id = $(this).attr('rel');
		$('.smallinput.product_edit'+product_id).attr('readonly', !$('.smallinput.product_edit'+product_id).attr('readonly'));
		$('#notification'+product_id).html("You can now edit product details.");
	});
});
//CLIENT EDIT ACTIVATOR
$(document).ready(function(){
	$('.button.edit_order_details_by_client').live('click', function(){
		product_id = $(this).attr('rel');
		$('.smallinput.client_edit_product_details'+product_id).attr('readonly', !$('.smallinput.client_edit_product_details'+product_id).attr('readonly'));
		$('#notification'+product_id).html("You can now edit product details.");
	    
	});
});

$('#add_product').live('click', function(){
	$('#addproduct_alert').html("Saving...");
	var order_id = $(this).attr('rel');
	var category = $('#add_category').val();
	var site_in_view = $('#add_site_in_view').val();
	var link = $('#add_link').val();
	var description = $('#add_description').val();
	var listed_price_D = $('#add_listed_price_D').val();
	var item_number = $('#add_item_number').val();
	var quantity = $('#add_quantity').val();
	var size = $('#add_size').val();
	var colour = $('#add_colour').val();
	$.post('', {'add_product': 'add_product', 'order_id': order_id,
		'category': category, 'site_in_view': site_in_view,
		'link': link, 'description': description,
		'listed_price_D': listed_price_D, 'item_number': item_number, 'quantity': quantity,
		'size': size, 'colour': colour}, function(data){
		if (data.result == 'fail'){
			$('#edit-order-box').show();
			$('#addproduct_alert').html(data.alert);
		}
		else{
			$('#edit-order-box').replaceWith(data);
			$('#edit-order-box').show();
			$('#addproduct_alert').html("Saved");
		}
	});
	return false;
});
$('.delete_product').live('click', function(){
	//$('.ajax-progress').show();
	$('#addproduct_alert').html("Loading....");
	var product_id = $(this).attr('id');
	var order_id = $(this).attr('rel');
	var delete_product = 'delete_product';
	$.post('', {'product_id': product_id, 'order_id': order_id, 'delete_product': delete_product}, function(data){
		if (data.result == 'fail'){
			$('#addproduct_alert').html(data.alert);
		}
		else{
			//$('.ajax-progress').hide();
			//$('#box'+order_id).replaceWith(data);
			$('#product'+product_id).hide();
			$('#addproduct_alert').html(data.alert);
		}
	});
	return false;
});
$('#edit_handling').live('click', function(){
	$('#edit_hdo_alert').html('Saving...');
	var order_id = $(this).attr('rel');
	var insure       = { 'insure': []};
	$("input[name=insure"+order_id+"]:checked").each(function(){
		insure['insure'].push($(this).val());
	});
	var consolidate  = {'consolidate': []};
	$("input[name=consolidate"+order_id+"]:checked").each(function(){
		consolidate['consolidate'].push($(this).val());	
	});
	var strip        = {'strip': []};
	$("input[name=strip_package"+order_id+"]:checked").each(function(){
		strip['strip'].push($(this).val());	
	});
	var dm           = {'dm': []};
	$("input[name=dm"+order_id+"]:checked").each(function(){
		dm['dm'].push($(this).val());	
	});
	$.post('', {'edit_handling': 'edit_handling', 'order_id': order_id, 'insure': insure, 'consolidate': consolidate,
		   'strip': strip, 'dm': dm}, function(data){
		
		$('#edit-order-box').replaceWith(data);
		$('#edit-order-box').show();
		$('#edit_hdo_alert').html("Saved");
		
	});
	
});
		
		
//Script for checkboxes
	
//$(".uncheck-checkbox .selectalltop").click(function(){
//	//$(this).parent().parent().find('input[type="checkbox"]').attr('checked', this.checked);
//	$(this).parent().parent().find('.select-all').attr('checked', this.checked);
//	$(this).parent().parent().find('.child1').attr('checked', this.checked);
//	$(this).parent().parent().find('.child2').attr('checked', this.checked);
//});
$(".options input:checkbox.select-all").click(function(){
	$(this).parent().parent().parent().find('.child1').attr('checked', this.checked);
	$(this).parent().parent().parent().find('.child2').attr('checked', this.checked);
});

$(".child-options1 input.child1").click(function(){
	$(this).parent().parent().parent().parent().find('.select-all').removeAttr('checked');
	$(this).parent().parent().parent().parent().parent().find('.selectalltop').removeAttr('checked');
});
$("#child-options2 input.child2").click(function(){
	$(this).parent().parent().parent().parent().parent().parent().parent().find('.select-all').removeAttr('checked');
	$(this).parent().parent().parent().parent().parent().parent().parent().parent().find('.selectalltop').removeAttr('checked');
});
		
		
	
$('.topside .order_detail table .title p').live('click', function(){
	$(this).parent().parent().find('.view-detail').toggleClass('active');
	return false;
});

$('.topside .order_detail .sub .edit').click(function() {
	var id = $(this).attr('order_id');
	$.post('', {'order_id': id, 'edit-window': 'edit-window'}, function(data){
		if (data.result != 'fail'){
			//$('.topside .modal-box#'+$(this).attr('rel')).show();
			$('#edit-order-box').replaceWith(data);
			$('#edit-order-box').show();
			$("#shadow").fadeTo(200,0.5);
		}
	});
});
$('.topside .order_detail .sub .button.gray').click(function() {
	var id = $(this).attr('id');
	var post_dict = { 'product' : [], 'order_id': id, 'process-package': 'process-package', 'purchased_products': 'purchased_products'};
	$("input[name=product_id]:checked").each(function(){
		post_dict['product'].push($(this).val());
	});
	$.post('', post_dict, function(data){
		if (data.result != 'fail'){
			//$('.topside .modal-box#'+$(this).attr('rel')).show();
			//$("#shadow").fadeTo(200,0.5);
			$('#process-package-window').replaceWith(data);
			$('#process-package-window').show();
			$("#shadow").fadeTo(200,0.5);
		}
	});
	return false;
});

$('.button.purchased_products').live('click', function() {
	var id = $(this).attr('id');
	$('#pp_alert').html('<h4>Saving...</h4>');
	$.post('', {'product_id': id, 'process-package': 'process-package', 'product_received': 'product_received'}, function(data){
		if (data.result != 'fail'){
			$('#product-'+id).html(data.alert);
			if (data.allProductReceived != "") {
				$('#pp_alert').html('<h4>'+data.allProductReceived+'</h4>');
			}
			//$('#process-package-window').replaceWith(data);
			//$('#process-package-window').show();
			//$("#shadow").fadeTo(200,0.5);
		}else{
			$('#pp_alert').html('<h4>'+data.alert+'</h4>');
		}
	});
	return false;
});

$('.button.pp_step2').live('click', function() {
	var id = $(this).attr('order_id');
	$('#pp_alert').html("<h4>Loading...</h4>");
	$.post('', {'order_id': id, 'process-package': 'process-package', 'pp_step2': 'pp_step2'}, function(data){
		if (data.result != 'fail'){
			//$('#pp_alert').html('');
			//$('#pp1').hide();
			//$('#pp2').show();
			$('#process-package-window').replaceWith(data);
			$('#process-package-window').show();
			$("#shadow").fadeTo(200,0.5);
		}
		else{
			$('#pp_alert').html('<h4>'+data.alert+'</h4>');
		}
	});
	return false;
});

$('.button.pp_step3').live('click', function() {
	$('#pp_alert').html("<h4>Saving...</h4>");
	var id = $(this).attr('order_id');
	var pp_length = $('#id_pp_length').val();
	var pp_width = $('#id_pp_width').val();
	var pp_height = $('#id_pp_height').val();
	var pp_weight = $('#id_pp_weight').val();
	$.post('', {'order_id': id, 'process-package': 'process-package', 'pp_step3': 'pp_step3',
	       'pp_length': pp_length, 'pp_width': pp_width, 'pp_height': pp_height, 'pp_weight': pp_weight}, function(data){
		if (data.result != 'fail'){
			//$('#pp_alert').html('<h4>'+data.alert+'</h4>');
			//$('#pp2').hide();
			//$('#pp3').show();
			$('#process-package-window').replaceWith(data);
			$('#process-package-window').show();
			$("#shadow").fadeTo(200,0.5);
		}
		else{
			$('#pp_alert').html('<h4>'+data.alert+'</h4>');
		}
	});
	return false;
});

$('.button.pp_step4').live('click', function() {
	var id = $(this).attr('order_id');
	$('#pp_alert').html("<h4>Loading...</h4>");
	$.post('', {'order_id': id, 'process-package': 'process-package', 'pp_step4': 'pp_step4'}, function(data){
		$('#process-package-window').replaceWith(data);
		$('#process-package-window').show();
		$("#shadow").fadeTo(200,0.5);
	});
	return false;
});

$('.close-modal').live('click', function () {
	$('.modal-box').hide();
	$("#shadow").fadeTo(200,0);
	$('#shadow').hide();
});

$(document).ready(function(){
	
	$('#assign-to-batch').hide();
	
	$('#switch-order-country').hide();
	
	//$('.shipping_boxes').hide();
	
	$('.longselect#id_chosen_status').change(function(){
		var value = $(this).val();
		if (value == "assigned_to_batch") {
			$('#assign-to-batch').show();
			$("#shadow").fadeTo(200,0.5);
			}
		else if (value == "enroute_to_delivery") {
			$("#enroute_to_delivery").show();
			$("#shadow").fadeTo(200,0.5);
			//code
		}
		else if (value == "switch_order_country") {
			$('#switch-order-country').show();
			$('#shadow').fadeTo(200,0.5);
		}
	});
	
	//$("#id_batch").click(function(){
	//	var batch_id = $(this).val();
	//	$("#id_shipping_box").attr
	//	
	//});
	
	

});

	
//$(function(){
//	var conditionalSelect = $("#id_shipping_box");
//	//Save possible options
//	options = conditionalSelect.children(".conditional").clone();
//	
//	$("#id_batch").change(function(){
//		var value = $(this).val();
//		//Remove all "conditional" options
//		conditionalSelect.children(".conditional").remove();
//		// Attach options that need to be displayed for the selected value
//		options.clone().filter("."+value).appendTo(conditionalSelect);
//	}).trigger("change");
//});