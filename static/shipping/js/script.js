        (function ($) {

            //check if the browser width is less than or equal to the large dimension of an iPad
            if ($(window).width() >= 768) {

                $(document).ready(function () {
                    $('.top').addClass('hidden');
                    $.waypoints.settings.scrollThrottle = 60;
                    $('.wrapper-content').waypoint(function (event, direction) {
                        $('.top').toggleClass('hidden', direction === "up");
                    }, {
                        offset: '-50%'
                    }).find('#main-nav-holder').waypoint(function (event, direction) {
                        $(this).parent().toggleClass('sticky', direction === "down");
                        $('#account.promo').toggleClass('two', direction === "down");
                        event.stopPropagation();
                    });
                });
                $('.navigation').scrollspy()

            }
        })(jQuery);
