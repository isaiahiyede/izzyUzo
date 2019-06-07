
	$('#buy_now_update').live('click', function(){
	    $('#alert1').html("Updating...");
	    var form_values = $('#buy_now_form').serialize();
	    $.post('/shopping/review-shopping-cart/', form_values, function(data){
		if (data.result != 'fail'){
		    $('#shop-content').replaceWith(data);
		    $('#alert1').html("Updated");
		}
		else{
		    $('#alert1').html(data);
		}
	    });
	    return false;
	});
	$('#buy_later_update').live('click', function(){
	    $('#alert1').html("Updating...");
	    var form_values = $('#buy_later_form').serialize();
	    $.post('/shopping/review-shopping-cart/', form_values, function(data){
		if (data.result != 'fail'){
		    $('#shop-content').replaceWith(data);
		    $('#alert1').html("Updated");
		}
	    });
	    return false;
	});
	$('.save.buy_now').live('click', function(){
	    $('#alert1').html("Saving...");
	    var id = $(this).attr('id');
	    var save_buy_now = 'True';
	    $.post('/shopping/review-shopping-cart/', {'id': id, 'save_buy_now': save_buy_now}, function(data){
		if (data.result != 'fail'){
		    $('#shop-content').replaceWith(data);
		    $('#alert1').html("Saved");
		}
	    });
	    return false;
	});
	

	$('.add.buy_later').live('click', function(){
	    $('#alert1').html("Saving...");
	    var id = $(this).attr('id');
	    var save_buy_later = 'True';
	    $.post('/shopping/review-shopping-cart/', {'id': id, 'save_buy_later': save_buy_later}, function(data){
		if (data.result != 'fail'){
		    $('#shop-content').replaceWith(data);
		    $('#alert1').html("Saved");
		}
	    });
	    return false;
	});
	$('.delete.product').live('click', function(){
	    $('#alert1').html("Saving...");
	    var id = $(this).attr('id');
	    $('#item'+id).hide();
	    var product_delete = 'True';
	    $.post('/shopping/review-shopping-cart/', {'id': id, 'product_delete': product_delete}, function(data){
		if (data.result != 'fail'){
		    $('#shop-content').replaceWith(data);
		    $('#alert1').html("Deleted");
		}
	    });
	    return false
	});
	
	
//new pages' implementation script
	//$('.save').live('click', function(){
	$('body').on('click', '.save', function(){
		$('.divLoading').addClass('show');
		$('#error_alert').html("Saving...");
		var id = $(this).attr('id');
		var data_dict = {};
		var btn_type = $(this).attr('btn-type');
		data_dict[btn_type] = 'True';
		data_dict['id'] = id;
	    
		$.post('', data_dict, function(data){
			if (data.result != 'fail'){
				$('.col-md-8.content_outer').replaceWith(data);
				$('#error_alert').html("Saved");
				$('.divLoading').removeClass('show');
			}
	    });
	    return false;
	});
	
	//$('.delete.a_product').live('click', function(){
	$('body').on('click', '.delete.a_product', function(){
		var product_desc = $(this).attr('data-desc');
		if (confirm("Are you sure you want to delete "+ product_desc +"?")) {
			$('.divLoading').addClass('show');
			$('#error_alert').html("Deleting " + product_desc + "...");
			var id = $(this).attr('id');
			//var item_tr = $(this).parent().parent();
			var product_delete = 'True';
			$.post('', {'id': id, 'product_delete': product_delete}, function(data){
			if (data.result != 'fail'){
				//item_tr.hide();
				$('.col-md-8.content_outer').replaceWith(data);
				$('#error_alert').html("Deleted " + product_desc);;
				$('.divLoading').removeClass('show');
				}
			});
		}
	    
	    return false
	});
	