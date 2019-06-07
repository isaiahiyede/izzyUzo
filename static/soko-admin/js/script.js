$(".toggle").click(function () {
    $('.panel.item').toggleClass('active');
    $(this).toggleClass('active');
    $('.bottom_sticky').toggleClass('active');

})

$(".bottom_sticky .cancel").click(function () {
    $('.panel.item').toggleClass('active');
    $('.toggle').toggleClass('active');
    $('.bottom_sticky').toggleClass('active');

})


$(".searchbar input").click(function () {
    $(this).parent().parent().parent().toggleClass('active');

})

$(".search_filter p span").click(function () {
    $(this).parent().toggleClass('active');

})

$(".md-button").click(function () {
    $(this).parent().parent().parent().parent().toggleClass('active');

})

$(".sticky_msg .alert .close").click(function () {
    $('.content .inner').toggleClass('active');

})

$(".overlay .linkt").click(function () {
    $(this).parent().parent().toggleClass('open');

})

$(".panel.item").click(function () {
    if ($(this).hasClass("active")) {
        //do something it does have the protected class!
        $(this).toggleClass('selected');
    }
});


$(".batches .panel.item .link").click(function () {
    $(this).parent().parent().toggleClass('open');
});



$(".itt span").click(function () {
    $('.itt span').removeClass('active');
    $(this).toggleClass('active');
    var target = $(this).attr('rel');
    $('.box').removeClass('active');
    $(".box#" + target).addClass('active');

});

/* Input script good/notgood */

$(".notgood input").click(function () {
    $(this).parent().removeClass('notgood');

});

$(".good input").click(function () {
    $(this).parent().removeClass('good');

});

$('.modal-footer .trigger').on('click', function () {
    $('.modal-c').removeClass('open');
    var target = $(this).attr('rel');
    $(".modal-c#" + target).addClass('open');
});


/* Upload Img Script */
$('.file-upload').hide();
$('#file-upload1').show();

$('.reveal-file').click(function (event) {
    $('#file-upload2').show();
    $(this).click(function (event) {
        $('#file-upload3').show();
        $(this).click(function (event) {
            $('#file-upload4').show();
            $(this).hide();
        })
    })
})


$('.image-box').click(function (event) {
    var imgg = $(this).children('img');
    $(this).siblings().children("input").trigger('click');

    $(this).siblings().children("input").change(function () {
        var reader = new FileReader();

        reader.onload = function (e) {
            var urll = e.target.result;
            $(imgg).attr('src', urll);
            imgg.parent().css('background', 'transparent');
            imgg.show();
            imgg.siblings('p').hide();

        }
        reader.readAsDataURL(this.files[0]);
    });
});

/* Route Edit Toggle */

$('.route').on('click', function () {
    $(this).parent().parent().parent().parent().parent().find('.form').removeClass('active');
    var target = $(this).attr('rel');
    $(".form#" + target).addClass('active');
    $('ul.routes li').removeClass('selected');
    $('.rwidget').removeClass('active');
});

$('.rwidget ul.routes li').on('click', function () {
    $('.rwidget ul.routes li').addClass('trig');
    $(this).parent().parent().toggleClass('active');
    $(this).toggleClass('selected');
    $(this).parent().parent().parent().find('.form').removeClass('active');
    var target = $(this).attr('rel');
    $(".form#" + target).addClass('active');
    $(this).parent().parent().parent().parent().find('.right .bt.nxt').removeClass('hide');
});
/* Steps Animations */

$(".page .service").click(function () {
    $(this).parent().parent().toggleClass('hid');
    $(this).parent().parent().parent().find('.page_outer').addClass('active');
    $(this).parent().parent().parent().find('.topsv').addClass('hid');
});

/* Steps Services Bullets */
$(".steps .item .circle").click(function () {
    $(this).parent().parent().parent().find('.widget').addClass('open');
    $(this).parent().parent().parent().find('.overlay').addClass('open');
    var target = $(this).attr('rel');
    $(this).parent().parent().parent().find('.widget_content').removeClass('active');
    $('.widget_content#' + target).addClass('active');
});

$(".widget .close , .widget .footer .btn ").click(function () {
    $('.widget').toggleClass('open');
    $('.pagect .overlay').removeClass('open');
});


/* Script toggle steps */
$(".bt.nxt").click(function () {
    var dt = $(this).parent().parent().parent().find('.page-content.active');


    $('.widget_content').removeClass('active');
    $('.widget').removeClass('open');
    $('.overlay').removeClass('open');

    $(this).parent().parent().parent().find('.page-content.active').next().addClass('active');
    dt.removeClass('active');
    $('.content .inner .breadcrumbs .progress-bar').css("width", '+=' + (0.25 * $('.progress').width()));


    $(".bt.prv").removeClass('hide');
    if ($('#pglast').hasClass('active')) {
        $(this).addClass('hide');
    } else {
        $(".bt.nxt").removeClass('hide');
    }

});
/* Script toggle steps */
$(".bt.prv").click(function () {
    var dtt = $(this).parent().parent().parent().find('.page-content.active');


    $(this).parent().parent().parent().find('.page-content.active').prev().addClass('active');
    dtt.removeClass('active');
    $('.content .inner .breadcrumbs .progress-bar').css("width", '-=' + (0.25 * $('.progress').width()));


    $(".bt.nxt").removeClass('hide');
    if ($('#pgfirst').hasClass('active')) {
        $(this).addClass('hide');
    } else {
        $(".bt.prv").removeClass('hide');
    }

});

/* Add Route Toggle Next BTN */

$('.form .btn.green').click(function () {
    $(this).parent().parent().parent().parent().parent().find('.right .bt.nxt').removeClass('hide');
});


/* Admin Scripts */

$(".houter .hitem .trigger").click(function () {
    $(this).parent().parent().toggleClass('active');

});

$(".admin .subcontent .it .trigger").click(function () {
    $(this).parent().parent().toggleClass('active');

});

$(".admin .subcontent .subcontent .it .trigger").click(function () {
    $(this).parent().parent().find('.it_outer').toggleClass('active');
});

$(".admin .subcontent .it_outer .subcontent.two .title .trigger").click(function () {
    $(this).parent().parent().toggleClass('active');
});
