(function ($) {

    //check if the browser width is less than or equal to the large dimension of an iPad
    if ($(window).width() >= 7068) {

        $(function () {
            var list = $('.slide');
            var current = 0;

            var main = $('#main');

            var nav = $('#nav');
            for (var i = 0; i < list.size(); i++) {
                if (i == 0) {
                    nav.append('<li id="' + i + '" class="active"><span class="button"></span></li>');
                } else {
                    nav.append('<li id="' + i + '" class=""><span class="button"></span></li>');
                }
            }

            $('#nav li').click(function () {
                current = $('#nav li').index(this);
                scroll(0);

            });
            $(window).bind('mousewheel', function (event) {
                if (event.originalEvent.wheelDelta >= 0) {
                    scroll(-1);
                } else {
                    scroll(1);
                }
            });

            $('.navbar .btn.green.full').click(function () {
                current = $('.btn.green.full').index(this);
                scroll(0);
            });
            $(window).bind('mousewheel', function (event) {
                if (event.originalEvent.wheelDelta >= 0) {
                    scrollTo('#estimate');
                } else {
                    scroll(1);
                }
            });

            $('.menulinks li a').click(function () {
                $('body').removeClass('active');
                $('body').toggleClass('topfix');
                $('.menu').toggleClass('bounceInDown');
                $('.navouter').addClass('fix');
                var tt = $(this).attr('rel');
                scrollTo("#main .slide#" + target).offset().top
            });


            /* Functions */
            var isScrolling = false;

            function scroll(dir) {
                if (isScrolling) {
                    return;
                }
                isScrolling = true;

                if (dir == -1) {
                    if (current > 0) {
                        current--;
                    }
                } else {
                    if (current < list.size() - 1) {
                        current++;
                    }
                }
                var number = 100 * current;
                var value = "translateY(-" + number + "vh)";
                main.css("transform", value);
                for (var i = 0; i < list.size(); i++) {
                    $('#nav li:nth-child(' + (i + 1) + ')').removeClass('active');
                }
                $('#nav li:nth-child(' + (current + 1) + ')').addClass('active');

                setTimeout(function () {
                    isScrolling = false;
                }, 500); // -> Here you can modify the time between functions call
            }
        });

    }
})(jQuery);



$(".social a").click(function () {
    $('.menu').toggleClass('bounceInDown');
    $('body').toggleClass('active');
    $('.navouter').removeClass('fix');
});

$(".menu .close").click(function () {
    $('body').toggleClass('active');
    $('.menu').toggleClass('bounceInDown');
});

$('.menulinks li a').click(function () {
    $('body').removeClass('active');
});


/* Order process steps - For TEST */

$(".order .bselect .btn_outer .btn").click(function () {
    $(this).parent().parent().parent().toggleClass('active');
    $(this).parent().parent().parent().parent().parent().toggleClass('active');
});


/* Go to */
$('.nav li a').click(function () {
    $('body').animate({
        scrollTop: $($(this).attr('href')).offset().top - 100
    }, 1200);
});

/* Custom Select */

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
    $('html').one('click', function () {
        $(".custom-select").removeClass("opened");
    });
    $(this).parents(".custom-select").toggleClass("opened");
    event.stopPropagation();
});
$(".custom-option").on("click", function () {
    $(this).parents(".custom-select-wrapper").find("select").val($(this).data("value"));
    $(this).parents(".custom-options").find(".custom-option").removeClass("selection");
    $(this).addClass("selection");
    $(this).parents(".custom-select").removeClass("opened");
    $(this).parents(".custom-select").find(".custom-select-trigger").text($(this).text());
});
