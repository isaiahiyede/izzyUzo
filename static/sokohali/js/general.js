
// 
// var field_ids = ['pk_address','pk_city','pk_state','pk_country','pk_address1','pk_address1','pk_zipcode']
// function require_input(option){
//     if(option == 'pick-up-package' || 'export-import') {
//         for (var id =0; id < field_ids.length; id++){
//             $('#' + field_ids[id]).attr('required', true);
//         }
//     } else {
//         for (var id =0; id < field_ids.length; id++){
//             $('#' + field_ids[id]).attr('required', false);
//         }
//     }
// }
//
// function select_shipping_option(id){                                                                                                                                                                                   // alert("its here");
//     //$this =  $('#id_shipping_option');
//     console.log(id)
//     $('#id_shipping_option').val(id);
//     if (id === "send-from-shop" || id === "drop-at-location"){
//       console.log("1")
//       //return true
//         // $("#" + id).css({"background-color":"gray","border":"2px solid red"});
//         // $("#send-from-shop").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
//         // $("#export-import").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
//
//         //$('#pick-up-location-form').removeClass('hidden');
//         //$this.attr("value","pick-up-package");
//         //$this.val("pick-up-package");
//         // $this.val("pick-up-package");
//         //$('#location_title').html('ENTER PICK UP LOCATION');
//         //$('#pick-up-phone').removeClass('hidden');
//
//     } else if(id === "pick-up-package" || id === "drop-at-postoffice"){
//       console.log("2")
//       //require_input(id);
//     }
//         // $("#" + id).css({"background-color":"gray","border":"2px solid red"});
//         // $("#export-import").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
//         // $("#pick-up-package").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
//
//         //$this.attr("value","send-from-shop");
//         //$this.val("send-from-shop");
//         //$('#pick-up-location-form').addClass('hidden');
//
//         // for (var id =0; id < field_ids.length; id++){
//         //     $('#' + field_ids[id]).attr("required", false);
//         // }
//     // } else if(id ==="export-import"){
//     //     $("#" + id).css({"background-color":"gray","border":"2px solid red"});
//     //     $("#send-from-shop").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
//     //     $("#pick-up-package").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
//     //
//     //     $('#pick-up-location-form').removeClass('hidden');
//     //     $this.attr("value", "export-import");
//     //     $this.val("export-import");
//     //     $('#location_title').html('ENTER POST OFFICE LOCATION');
//     //     require_input(id);
//     else {
//       console.log("3")
//         //require_input(id);
//     }
// }




function validate_import_selection(){
    $this =  $('#id_shipping_option');
    var origin = $("#id_country_from").find(":selected").val();
    var destination = $("#id_country_to").find(":selected").val();
    if (origin === destination){
        alert("Destination country cannot be the same as origin country");
        return false;
    }
    if (!($this).val()){
        alert("You have not selected any shipping option");
        return false;
        }
        else if (origin == "") {
            alert("You have not selected any origin country");
            return false;
        }
        else if
            ( destination == "") {
            alert("You have not selected any destination country");
            return false;
        }
    return true;
    }




function set_action(origin){
    if (origin === "Nigeria"){
        return '/export-landing-page'
    }
    return '/import/shipping/retrieve_modal_values'

}




function set_country_option(){
    var origin = $("#id_country_from").find(":selected").val();
    if (origin === "Nigeria"){
        $("#service-selection").addClass('hidden');
        $("#id_shipping_option").val("Export");
        $("#pick-up-location-form").addClass('hidden');
        $("#send-from-shop").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
        $("#export-import").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
        $("#pick-up-package").css({"background-color":"#3C983C","border":"2px solid #3C983C"});
    } else {
        $("#id_shipping_option").val("");
        $("#service-selection").removeClass('hidden');
    }
    $("#service-option-form").attr("action", set_action(origin));
}
