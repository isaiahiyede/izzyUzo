$(".item .circle").click(function () {
    $('.panel.item').toggleClass('active');
    $(this).toggleClass('active');
    $('.bottom_sticky').toggleClass('active');

})

$("#nav-toggle").click(function () {
    $(this).toggleClass('active');
    $('body').toggleClass('overflow');
})

$(".steps.t .circle").click(function () {
    $('.ft').toggleClass('active');
    $(this).parent().addClass('active');
    var target = $(this).attr('rel');
    $(".inner#" + target).addClass('active');
})

$(".ft .overlay, .ft .inner .close").click(function () {
    $('.ft').toggleClass('active');
    $('.ft .inner').removeClass('active');
    $('.steps.t .item').removeClass('active');
})

$(".nav .dropdown-menu a[href^='#']").on("click", function (e) {
    $("html, body").animate({
        scrollTop: $($(this).attr("href")).offset().top
    }, 1000);
});