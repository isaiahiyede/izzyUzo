 jQuery(document).ready(function($) {

		$('.new_user_check').shake({/*direction: "up", distance: 50*/ times: 6, speed: 60});
		$('.general-login-shake').shake({times: 3, speed: 80});
		$('.new_user_check').delay(5000).slideUp(2000);
		if ($('.new_user_check').is(':visible')){
			$('.dashboard-button-panel').hide().delay(7000).slideDown(2000);
		}
		else {
			$('.dashboard-button-panel').hide().slideDown(500);
			$('.dashboard-button-panel').shake({times: 3, speed: 100});
		}

		$('.shaker').shake({times: 5, speed: 80});

		$('.size-container').click(function() {
			$('.size-container').removeClass('size-new-color');
			$(this).addClass('size-new-color');
		});



		// $('.client-order-form-male, .client-order-form-female').hide();

		//make it not function if it is checked
		// $('#id_sex_0').click(function() {
		// 	if ($('.client-order-form-male').is(':visible')) {
		// 		$('.client-order-form-male').hide(500);
		// 	};
		// 	$('.client-order-form-female').slideToggle(500);
		// });

		// $('#id_sex_1').click(function() {
		// 		if ($('.client-order-form-female').is(':visible')) {
		// 		$('.client-order-form-female').hide(500);
		// 	};
		// 	$('.client-order-form-male').slideToggle(500);
		// });
//  setTimeout( "jQuery('body').hide();",3000 );


	//  setTimeout("paulund_modal_box();", 3000);



	setTimeout(function(){
		$('.wrapper_test').slideUp(500, function() {
			$('.wrapper_result').slideDown(500)
		});
		// $('.wrapper_result').slideDown(2000);
	},600000)
});