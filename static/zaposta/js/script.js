$('nav .triggerouter').click(function () {
    $('.st-container').toggleClass('active');
});

$('.overlay').click(function () {
    $('.st-container').removeClass('active');
});

$('.st-menu .close').click(function () {
    $('.st-container').removeClass('active');
});

$('.btn.toggle').click(function () {
    $(this).parent().toggleClass('open');
});


$('#mobile .over').click(function () {
    $(this).parent().toggleClass('open');
});

$('#deals .item .right #back').click(function () {
    $(this).parent().parent().toggleClass('full');
    $('#deals .item').removeClass('full');
});

$('#deals .item .image .btn').click(function () {
    $('#deals .item').removeClass('full');
    $(this).parent().parent().parent().parent().toggleClass('full');
});

$('#list .right span').click(function () {
    $('#list .right span').removeClass('active');
    $(this).toggleClass('active');
});

$('.widget .promo').click(function () {
    $(this).parent().parent().toggleClass('show');
});


/* Register Form Script Hide/Show */
$('.form .promo .btn').click(function () {
    $(this).parent().parent().parent().parent().toggleClass('show');
    $('.form #login').removeClass('show');
    $('#register .left').show();
    $('#register .business_registration').hide();
    $('.form #register').removeClass('active');
});

$('.form #login .left .rst').click(function () {
    $(this).parent().parent().parent().toggleClass('show');
});

$('.form .left .buttons .next').click(function () {
    $('.left_inner').removeClass('active');
    $('.left_inner#' + $(this).attr('rel')).toggleClass('active');
});

$('.form .promo .business_account').click(function () {
    $(this).parent().parent().toggleClass('active');
    $('.left_inner').removeClass('active');
    $('.left_inner#l1').addClass('active');
});
$('#main .widget .form .more').click(function () {
    $(this).parent().parent().toggleClass('show');
});


/* Register Form Script Hide/Show */

(function ($) {

    //check if the browser width is less than or equal to the large dimension of an iPad
    if ($(window).width() >= 768) {

        $(window).scroll(function () {
            var y_scroll_pos = window.pageYOffset;
            var scroll_pos_test = 450;
            // set to whatever you want it to be

            if (y_scroll_pos > scroll_pos_test) {
                $("header").addClass('show');
            } else {
                $("header").removeClass('show');
            }
        });

    }
})(jQuery);

/* Custom Select Start */

$(".custom-select").each(function () {
    var classes = $(this).attr("class"),
        id = $(this).attr("id"),
        name = $(this).attr("name");
    var template = '<div class="' + classes + '">';
    template += '<span class="custom-select-trigger">' + $(this).attr("placeholder") + '</span>';
    template += '<div class="custom-options">';
    $(this).find("option").each(function () {
        template += '<span class="custom-option ' + $(this).attr("class") + '" data-value="' + $(this).attr("value") + '">' + $(this).html() + '</span>';
    });
    template += '</div></div>';

    $(this).wrap('<div class="custom-select-wrapper"></div>');
    $(this).hide();
    $(this).after(template);
});
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

/* Custom Select End */

$(function () {
    $('[data-toggle="tooltip"]').tooltip();
})


var imgArray = ['img/mobile/1.png',
                 'img/mobile/2.png',
                 'img/mobile/3.png',
                 'img/mobile/4.png'
               ]
var nextBG = "url(" + imgArray[Math.floor(Math.random() * imgArray.length)] + ") no-repeat left 40px";
$('#').css("background", nextBG);

setInterval(function () {
    nextBG = "url(" + imgArray[Math.floor(Math.random() * imgArray.length)] + ") no-repeat left 40px";
    $('#').fadeOut('slow', function () {
        $(this).css("background", nextBG).fadeIn('slow');
    })
}, 5000); // 3 second interval

/* FAQ SCRIPT */
$('#faq_content .content .item').click(function () {
    $(this).toggleClass('full');
});

$(window).scroll(function () {
    var y_scroll_pos = window.pageYOffset;
    var scroll_pos_test = 700;
    // set to whatever you want it to be

    if (y_scroll_pos > scroll_pos_test) {
        $(".menu_outer").addClass('sticky');
        $(".content .searchbar").addClass('sticky');
        $(".content .searchbar").removeClass('sticky_bottom');
        $(".menu_outer").removeClass('sticky_bottom');
    } else {
        $(".menu_outer").removeClass('sticky');
        $(".content .searchbar").removeClass('sticky');
        $(".menu_outer").removeClass('sticky_bottom');
        $(".content .searchbar").removeClass('sticky_bottom');
    }
});

$(window).bind('scroll', function () {
    if ($(window).scrollTop() >= $('#support').offset().top - 432) {
        $(".menu_outer").removeClass('sticky');
        $(".menu_outer").addClass('sticky_bottom');
    }
});

$(window).bind('scroll', function () {
    if ($(window).scrollTop() >= $('#support').offset().top - 186) {
        $(".content .searchbar").removeClass('sticky');
        $(".content .searchbar").addClass('sticky_bottom');
    }
});

$('.menu_left li a').on('click', function (e) {
    e.preventDefault();
    var target = this.hash,
        $target = $(target);
    $('html, body').stop().animate({
        'scrollTop': $target.offset().top + (-178)
    }, 300, 'swing', function () {
        window.location.hash = target;
    });
});

$('.menu_left ul li a').click(function () {
    $('.menu_left ul li').removeClass('active');
    $(this).parent().toggleClass('active');
});

$('.shipment .btn.w').click(function () {
    $(this).parent().parent().parent().parent().toggleClass('active');
});

$('.shipment .back').click(function () {
    $(this).parent().parent().parent().parent().parent().toggleClass('active');
});

$('.shipment .item .out .history').on('click', function () {
    $(this).parent().parent().toggleClass('active');
    $(this).parent().toggleClass('selected');
});

$('.info .add').click(function () {
    $(this).parent().parent().toggleClass('active');
    $(this).toggleClass('selected');
});

$('#how .mc span').click(function () {
    $(this).parent().parent().parent().toggleClass('active');
});

$('#how .video .close').click(function () {
    $(this).parent().parent().parent().toggleClass('active');
});

$('.modal-body .right .edit').click(function () {
    $('.t_inner').removeClass('active');
    $('.t_inner#' + $(this).attr('rel')).toggleClass('active');
    $(this).parent().parent().find('.selected').removeClass('selected');
    $(this).parent().toggleClass('selected');
});

$('.modal-body .t .back').click(function () {
    $(this).parent().toggleClass('active');
    $(this).parent().parent().parent().find('.selected').removeClass('selected');
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

$('.checkb input[type="radio"]').click(function () {
    $('.tabh .col-md-12').removeClass('active');
    $(this).parent().parent().toggleClass('active');
});

// $('.credit.two .panel.addr').click(function () {
//     $(this).parent().parent().find('.panel.addr').removeClass('active');
//     $(this).toggleClass('active');
// });

$('.timmer table .delete').click(function () {
    $(this).parent().parent().addClass('hide');
});

$('.delivery_slc .custom-option').click(function () {
    $('.delivery_options .slc').removeClass('active');
    $('#' + $(this).attr('data-value')).toggleClass('active');
});

$('.clean .adds.item.select').click(function () {
    $('.clean .adds.item.select').removeClass('active');
    $(this).toggleClass('active');
});

$('.credit.two .payment_methods .panel').click(function () {
    $(this).parent().parent().find('.active').removeClass('active');
    $(this).toggleClass('active');
});

$('.table.two .line input').click(function () {
    $(this).parent().toggleClass('active');
});


/* Live Close Button Event */
$('.clean .modal-header .close').live('click', function () {
    $(this).parent().parent().parent().parent().hide();
    $(this).parent().parent().parent().parent().removeClass('in');
    $(this).parent().parent().parent().parent().parent().removeClass('modal-open');
    $(this).parent().parent().parent().parent().parent().find('.modal-backdrop').hide();
});
