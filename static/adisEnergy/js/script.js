$('.nav li a, .btn.goto').click(function () {
    $('body').animate({
        scrollTop: $($(this).attr('href')).offset().top - 0
    }, 1200);
});

$('#nav-icon1,#nav-icon2,#nav-icon3,#nav-icon4').click(function () {
    $(this).toggleClass('open');
});

$('.booking .header span').click(function () {
    $('.booking .header span').parent().removeClass('active');
    $('.booking .content').removeClass('active');
    $(this).parent().toggleClass('active');
    var target = $(this).attr('rel');
    $(".booking .content#" + target).addClass('active');
});

$('select').each(function () {
    var $this = $(this),
        numberOfOptions = $(this).children('option').length;

    $this.addClass('select-hidden');
    $this.wrap('<div class="select"></div>');
    $this.after('<div class="select-styled"></div>');

    var $img = $(this).children('option').find('img').addClass('.img');

    var $styledSelect = $this.next('div.select-styled');
    $styledSelect.text($this.children('option').eq(0).text());

    var $list = $('<ul />', {
        'class': 'select-options'
    }).insertAfter($styledSelect);

    for (var i = 0; i < numberOfOptions; i++) {
        $('<li />', {
            text: $this.children('option').eq(i).text(),
            rel: $this.children('option').eq(i).val(),
        }).appendTo($list);
    }

    var $listItems = $list.children('li');

    $styledSelect.click(function (e) {
        e.stopPropagation();
        $('div.select-styled.active').not(this).each(function () {
            $(this).removeClass('active').next('ul.select-options').hide();
        });
        $(this).toggleClass('active').next('ul.select-options').toggle();
    });

    $listItems.click(function (e) {
        e.stopPropagation();
        $styledSelect.text($(this).text()).removeClass('active');
        $this.val($(this).attr('rel'));
        $list.hide();
        //console.log($this.val());
    });

    $(document).click(function () {
        $styledSelect.removeClass('active');
        $list.hide();
    });

});

$('.widget .link.one').click(function () {
    $(this).parent().parent().parent().parent().toggleClass('active');
});
$('.widget .link.two').click(function () {
    $(this).parent().parent().parent().toggleClass('active');
});

$(".steps .btn_outer .btn.next").click(function () {

    var dt = $(this).parent().parent().parent().find('.steps_content.active');


    $(this).parent().parent().parent().find('.steps_content.active').next().addClass('active');
    dt.removeClass('active');


    $('.booking.new .breadcrumbs .progress-bar').css("width", '+=' + (0.20 * $('.progress').width()));

});

$(".steps .btn_outer .btn.back").click(function () {

    var dtt = $(this).parent().parent().parent().find('.steps_content.active');

    $('.booking.new .breadcrumbs .progress-bar').css("width", '-=' + (0.20 * $('.progress').width()));

    $(this).parent().parent().parent().find('.steps_content.active').prev().addClass('active');
    dtt.removeClass('active');


});

$(".booking.new .boxes .box").click(function () {
    $('.booking.new .boxes .box').removeClass('active');
    $(this).addClass('active');
});

$(".steps .btn_outer .finish").click(function () {
    $(this).parent().parent().parent().find('.overlay').addClass('active');
    $(this).parent().parent().removeClass('active');
});
