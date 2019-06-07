$(window).bind('scroll', function() {
    if($(window).scrollTop() >= $('#support').offset().top - 432) {
              $(".menu_outer").removeClass('sticky');
              $(".menu_outer").addClass('sticky_bottom');
            }
    });
    
    $(window).bind('scroll', function() {
    if($(window).scrollTop() >= $('#support').offset().top - 186) {
              $(".content .searchbar").removeClass('sticky');
              $(".content .searchbar").addClass('sticky_bottom');
            }
    });
    
        $('.menu_left li a').on('click',function (e) {
            e.preventDefault();
            var target = this.hash,
            $target = $(target);
    $('html, body').stop().animate({
        'scrollTop': $target.offset().top + (-178)
    }, 300, 'swing', function () {
        window.location.hash = target;
    });
        });
        
       $('.menu_left ul li a').click(function() {
         $('.menu_left ul li').removeClass('active');
         $(this).parent().toggleClass('active');
  });
       



function activate_custom_select(select_name){
   $(".custom-select").each(function () {
    //name = $(this).attr("name");
    //if (select_name === name) {
       var classes = $(this).attr("class"),
        id = $(this).attr("id"),
        name = $(this).attr("name");        
        
            //console.log("select_name: "+select_name);
            //console.log(classes);
            //console.log("name: "+name);
            var template = '<div class="' + classes + '">';
            placeholder = $(this).attr("placeholder");
            //console.log("placejoldeR: "+placeholder);
            
            if (placeholder != undefined) {
                //console.log("select_name: "+select_name);
                //console.log("name: "+name);
                template += '<span class="custom-select-trigger">' + $(this).attr("placeholder") + '</span>';
                template += '<div class="custom-options">';
                
                
                $(this).find("option").each(function () {
                template += '<span class="custom-option ' + $(this).attr("class") + '" data-value="' + $(this).attr("value") + '">' + $(this).html() + '</span>';
                });
                template += '</div></div>';
                
                
                if (name != 'sources'){
                    $(this).wrap('<div class="custom-select-wrapper"></div>');
                }
            }
            
            $(this).hide();
            $(this).after(template);
            
        //}
        
       
   });
   
   //if (select_name != 'sources') {
        $(".custom-option:first-of-type").hover(function () {
            $(this).parents(".custom-options").addClass("option-hover");
        }, function () {
            $(this).parents(".custom-options").removeClass("option-hover");
        });
        $(".custom-select-trigger").on("click", function () {
            $(this).parents(".custom-select").toggleClass("opened");
        });
        
        $(".custom-option").on("click", function () {
             $(this).parents(".custom-select-wrapper").find("select").val($(this).data("value"));
             $(this).parents(".custom-options").find(".custom-option").removeClass("selection");
             $(this).addClass("selection");
             $(this).parents(".custom-select").removeClass("opened");
             $(this).parents(".custom-select").find(".custom-select-trigger").text($(this).text());
       
        });
   //}
}

//activate_custom_select();
       
//$(".custom-option").on("click", function () {
$("body").on('click', ".custom-option", function(){
    
    $(".divLoading").addClass('show');

    var select_val = $(this).data("value");
    var select_type = $(this).parents(".custom-select-wrapper").find("select").attr('id');
    //console.log(select_val);
    //console.log(select_type);
    
    $(this).parents(".custom-select-wrapper").find("select").val($(this).data("value"));
    $(this).parents(".custom-options").find(".custom-option").removeClass("selection");
    $(this).addClass("selection");
    $(this).parents(".custom-select").removeClass("opened");
    $(this).parents(".custom-select").find(".custom-select-trigger").text($(this).text());
    
    if (select_val == 'all') {
        $('.inner').find('.col-md-12.shipment_div').show();
    }else{
        $('.inner').find('.col-md-12.shipment_div').hide();
        $('.inner').find('.col-md-12.shipment_div').each(function(){
            if(select_type == "status"){
                if ($(this).attr('data-status')  == select_val) {
                    $(this).show();
                }
            }else{
                if ($(this).attr('data-shipping-method')  == select_val) {
                    $(this).show();
                }
            }
            
        });
    }
    
    $(".divLoading").removeClass('show');
    
});

$('.edit.add_comment').click(function () {
    $(".divLoading").addClass('show');
    var message_id = $(this).attr('message_id');
    //var parent_div = $(this).parent().parent().parent().parent();
    $.post('', {'message_id': message_id, 'view_comment_msgs': 'view_comment_msgs'}, function(data){			
        
        $(data).replaceAll("#compose");
        $('#compose').show();
        $(".divLoading").removeClass('show');
    });		
});

//recently added
//$('.checkb input[type="checkbox"]').click(function () {
$('body').on('click', '.checkb input[type="checkbox"]', function () {
    $('.tabh .col-md-12').removeClass('active');
    $(this).parent().parent().toggleClass('active');
});


//$('#add_comment_btn').live('click', function(){
$('body').on('click', '#add_comment_btn', function(){
    $(".divLoading").addClass('show');
    var form_id = $(this).attr('rel');
    var message_id = $(this).attr('message_id');
    var form_values = $('#'+form_id).serialize()+'&'+$.param({ action: form_id, 'message_id': message_id });
    console.log(form_values);
    $.post('', form_values, function(data){
        if (data.result != 'fail') {
            $(data).replaceAll("#compose");
            $('#compose').show();
            
        }else{
            alert(data.alert_msg);
        }
        $(".divLoading").removeClass('show');
        
    });
    
});

// $('.shipment .btn.w').click(function () {

//     $(".divLoading").addClass('show');
//     var obj_id = $(this).attr('obj_id');
//     var is_export = $(this).attr('is_export');
//     alert(is_export);
//     var parent_div = $(this).parent().parent().parent().parent().parent();
//     $.post('', {'obj_id': obj_id, 'collapse_shipment': 'collapse_shipment', 'is_export': is_export}, function(data){			
//         parent_div.find('.second').replaceWith(data);
//         parent_div.toggleClass('active');
//         //$('#S1').show();
//         $(".divLoading").removeClass('show');
//     });		
// });


$('.shipment .btn.w').click(function () {

    $(".divLoading").addClass('show');
    var obj_id = $(this).attr('obj_id');
    var is_export = $(this).attr('is_export');
    var shipment_type = $(this).attr('shipment_type');
    // alert(shipment_type);
    var parent_div = $(this).parent().parent().parent().parent().parent();
    $.post('', {'obj_id': obj_id, 'collapse_shipment': 'collapse_shipment', 'shipment_type':shipment_type, 'is_export': is_export}, function(data){            
        parent_div.find('.second').replaceWith(data);
        parent_div.toggleClass('active');
        //$('#S1').show();
        $(".divLoading").removeClass('show');
    });     
});



//$('.shipment .back').live('click', function () {
$('body').on('click', '.shipment .back', function () {
    $(this).parent().parent().parent().parent().parent().toggleClass('active');
});

//$('.shipment .item .out .history').live('click', function () {
$('body').on('click', '.shipment .item .out .history', function () {
    $(this).parent().parent().toggleClass('active');
    $(this).parent().toggleClass('selected');
});
    
       
$('body').on('click', '.btn.black', function () {
//$('.btn.black').live('click', function(){
    $(".divLoading").addClass('show');
    var shipment_id = $(this).attr('shipment_id');
    $.post('', {'id': shipment_id, 'edit_shipment': 'edit_shipment'}, function(data){			
        $(data).replaceAll("#S1");
        
        activate_custom_select("state");
        
        $('#S1').show();
        $(".divLoading").removeClass('show');
    });			    
});

//$('#edit_handling_options').live('click', function(){
$('body').on('click', '#edit_handling_options', function () {
    var form_id = $(this).attr('rel');
    var shipment_id = $(this).attr('shipment_id');
    
    if ($('#id_dm_location').val() == '' && $('#id_address_book').val() == '') {
        alert("Please select a Pick Up Location");
    }else{
        $(".divLoading").addClass('show');
        var form_values = $('#'+form_id).serialize()+'&'+$.param({ action: form_id, 'shipment': shipment_id });
        //console.log(form_values);
        $.post('', form_values, function(data){
            $(data).replaceAll("#S1");
            activate_custom_select("state");
            $('#S1').show();
            $(".divLoading").removeClass('show');
        });
    }
    
    
    
});

/* Live Close Button Event */
//$('.clean .modal-header .close').live('click', function () {
$('body').on('click', '.clean .modal-header .close', function () {    
    $(this).parent().parent().parent().parent().hide();
    $(this).parent().parent().parent().parent().removeClass('in');
    $(this).parent().parent().parent().parent().parent().parent().parent().removeClass('modal-open');
    $(this).parent().parent().parent().parent().parent().parent().parent().find('.modal-backdrop').hide();
});


$('body').on('click', '#add_item_btn', function () {    
//$('#add_item_btn').live('click', function(){
    $(".divLoading").addClass('show');
    var form_id = $(this).attr('rel');
    var shipment_id = $(this).attr('shipment_id');
    //console.log(item_rel);
    //console.log(id);
    var form_values = $('#'+form_id).serialize()+'&'+$.param({ action: form_id, 'shipment': shipment_id });
    //console.log(form_values);
    $.post('', form_values, function(data){
        if (data.result != 'fail') {
            $(data).replaceAll("#S1");
            activate_custom_select("state");
            $('#S1').show();
        }else{
            alert(data.alert);
        }
        
        $(".divLoading").removeClass('show');
    });
    
});

//$('.btn.update').live('click', function(e){
$('body').on('click', '.btn.update', function (e) { 
    //$('#wl.slc').append('<div>Testing</div>');
    var item_rel = $(this).attr('rel');
    //console.log(item_rel);
    var item_rel_split = item_rel.split('m'); //itemxx
    //var item_rel_split = item_rel.split('m')[1]; //itemxx
    var action = item_rel_split[0];
    var item_id = item_rel_split[1];
    if (action == "edit_ite") {
        action = "edit_item"; //split removed 'm'
    }
    if (action == "edit_address" || action == "add_address") {
        var state = $(this).parent().find('#select_state').val();
        if (state == "") {
            //e.preventDefault();
            alert("Please choose a state.");
            return false;
        }
        //console.log(state)
    }
    $(".divLoading").addClass('show');
    //console.log(id);
    //var form_values = $('#edit_'+item_rel).serialize()+'&'+$.param({ 'edit_item': 'edit_item', 'item_id': item_id });
    var form_values = $('#'+item_rel).serialize()+'&'+$.param({ action: action, 'item_id': item_id });
    //console.log(form_values);
    $.post('', form_values, function(data){
        if (data.result != 'fail') {
            if (action == "edit_item") {
            //if (action == "edit_address") {
                
                $(data).replaceAll("#S1");
                activate_custom_select("state");
                $('#S1').show();
                
            }else{
                $('.t_inner#add_address .back').trigger('click');
                $('#wl.slc').append(data.new_address_div);
                $('#al.slc').append(data.new_address_div);
            }
            
            
        }else{
            alert(data.alert);
        }
        $(".divLoading").removeClass('show');
        
        
    });
   
});

//$('.remove').live('click', function(e){
$('body').on('click', '.remove', function (e) { 
    //if (confirm("Are you sure you want to delete this item?")) {
    if (confirm("Are you sure you want to delete "+ $(this).attr('data-desc') +"?")) {
        $(".divLoading").addClass('show');
        var item_id = $(this).attr('data-item-id');
        var shipment_id = $(this).attr('data-shipment-id');
    
        $.post('', {'item_id': item_id, 'shipment': shipment_id, 'delete_item': 'delete_item'}, function(data){
            $(data).replaceAll("#S1");
            activate_custom_select("state");
            $('#S1').show();
            //if (data.result == 'ok') {
            //    console.log("This result is ok");
            //    $(this).parent().hide();
            //};
            $(".divLoading").removeClass('show');
        });
    }
    else{
        return false;
        //e.preventDefault();
    }
    
});



//$('.modal-body .right .edit').live('click', function () {
$('body').on('click', '.modal-body .right .edit', function () { 
    $('.t_inner').removeClass('active');
    $('.t_inner#' + $(this).attr('rel')).toggleClass('active');
    $(this).parent().parent().find('.selected').removeClass('selected');
    $(this).parent().toggleClass('selected');
    
    //activate_custom_select("state");
    var item_id = $(this).attr('rel');
    $('.btn.update').hide();
    $('.btn.update.'+item_id).show();
    //$('.btn_add_item').hide();
      
});

$('body').on('click', '#sdfsshow_add_new_address', function () { 
//$('#sdfsshow_add_new_address').live('click', function(){
   //$("#edit_address").show();
   //console.log("show_add_new_address");
   //$("#add_addresstesting")[0].reset()
   $('.t_inner#add_address').show();//toggleClass('active');
   $('.t_inner#add_address .back').show()
   //document.getElementById("add_address").reset();
});


$('body').on('click', '.modal-body .right .btn.yellow', function () { 
//$('.modal-body .right .btn.yellow').live('click', function () {
   $('.t_inner').removeClass('active');
   $('.t_inner#' + $(this).attr('rel')).toggleClass('active');
   $(this).parent().parent().find('.selected').removeClass('selected');
   $('#add_item_btn').show();
    //$(this).parent().toggleClass('selected');
    //var item_id = $(this).attr('rel');
    //$('.btn.update.'+item_id).show();
});

$('body').on('click', '.modal-body .t .back', function () { 
//$('.modal-body .t .back').live('click', function () {
    $(this).parent().toggleClass('active');
    $(this).parent().parent().parent().parent().find('.selected').removeClass('selected');
    $(this).parent().parent().parent().find('.btn.update').hide();
    $('.btn_add_item').hide();
});

$('.credit .tab-content table input[type="radio"]').click(function () {
    $(this).parent().parent().parent().parent().parent().parent().addClass('selected');
    $(this).parent().parent().addClass('active');
});

$('.credit .btns .btn.cl').click(function () {
    $(this).parent().parent().removeClass('selected');
    $(this).parent().parent().find('td.selected.active').removeClass('active');
    $(this).parent().parent().find('td.selected input').attr('checked', false);
});

$(function () {
    $("body").tooltip({ selector: '[data-toggle="tooltip"]'});
    //$('[data-toggle="tooltip"]').tooltip();
});

$('body').on('click', '.delivery_slc .custom-option', function () { 
//$('.delivery_slc .custom-option').live('click', function () {
    
    var select_name = $(this).parents(".custom-select-wrapper").find("select").attr('name');
    if (select_name == "dm_freight") {
        $('.delivery_options .slc').removeClass('active');
    }
    
    $('#' + $(this).attr('data-value')).toggleClass('active');
    var select_val = $(this).text();
    
    $("#id_"+select_name).val(select_val);
    //console.log(select_name);
    //console.log(select_val);
    
    if (select_val == 'Home Delivery Within Lagos' || select_val == 'Home Delivery Outside Lagos') {
        $("#show_add_new_address").show();
    }else{
         $("#show_add_new_address").hide();
    }
});


$('body').on('click', '.clean .adds.item.select', function () { 
//$('.clean .adds.item.select').live('click', function () {
    //console.log($(this).attr('address-id'));
    $("#id_address_book").val($(this).attr('address-id'));
    $('.clean .adds.item.select').removeClass('active');
    $(this).toggleClass('active');
});

