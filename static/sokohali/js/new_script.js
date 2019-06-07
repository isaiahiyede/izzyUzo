$('.menu').click(function () {
    $('.st-container').toggleClass('active');
    $('body').toggleClass('active');
});

$('.overlay').click(function () {
    $('.st-container').removeClass('active');
    $('body').removeClass('active');
});

$('.st-menu .close').click(function () {
    $('.st-container').removeClass('active');
    $('body').removeClass('active');
});


(function ($) {

    //check if the browser width is less than or equal to the large dimension of an iPad
    if ($(window).width() >= 768) {
        $('.zaposta .widget ul li a').hover(
            function () {
                $('#intro').removeAttr('class');
                $('#intro').addClass($(this).attr('rel'));
                $('.navlinks .navbar').addClass('active');
            },
            function () {
                $('#intro').removeAttr('class');
                $('.navlinks .navbar').removeClass('active');
            }
        );

    }
})(jQuery);

/*
 Reference: http://jsfiddle.net/BB3JK/47/
 */

// $('select').each(function () {
//     var $this = $(this),
//         numberOfOptions = $(this).children('option').length;
//
//     $this.addClass('select-hidden');
//     $this.wrap('<div class="select"></div>');
//     $this.after('<div class="select-styled"></div>');
//
//     var $styledSelect = $this.next('div.select-styled');
//     $styledSelect.text($this.children('option').eq(0).text());
//
//     var $list = $('<ul />', {
//         'class': 'select-options'
//     }).insertAfter($styledSelect);
//
//     for (var i = 0; i < numberOfOptions; i++) {
//         $('<li />', {
//             text: $this.children('option').eq(i).text(),
//             rel: $this.children('option').eq(i).val()
//         }).appendTo($list);
//     }
//
//     var $listItems = $list.children('li');
//
//     $styledSelect.click(function (e) {
//         e.stopPropagation();
//         $('div.select-styled.active').each(function () {
//             $(this).removeClass('active').next('ul.select-options').hide();
//         });
//         $(this).toggleClass('active').next('ul.select-options').toggle();
//     });
//
//     $listItems.click(function (e) {
//         e.stopPropagation();
//         $styledSelect.text($(this).text()).removeClass('active');
//         $this.val($(this).attr('rel'));
//         $list.hide();
//         //console.log($this.val());
//     });
//
//     $(document).click(function () {
//         $styledSelect.removeClass('active');
//         $list.hide();
//     });
//
// });

$('#shipwd .shipinfo .soption').click(function () {
    $('#shipwd .shipinfo .col-md-4').removeClass('active');
    $(this).parent().addClass('active');
    $('#shipwd .shipinfo .scontent').removeClass('active');
    var target = $(this).attr('rel');
    $(" #shipwd .shipinfo .scontent#" + target).addClass('active');
});




// $('#shipwd .twoselect .select-options li').click(function () {

//     var target = $(this).attr('rel');


//     if (target === "Nigeria") {
//         $('#shipwd .shipinfo').removeClass('active');
//         $("#domestic").toggleClass('active');
//     }
// });
