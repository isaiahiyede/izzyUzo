
        $('nav .triggerouter').click(function () {
            $('.st-container').toggleClass('active');
        });

        $('.overlay').click(function () {
            $('.st-container').removeClass('active');
        });

        $('.st-menu .close').click(function () {
            $('.st-container').removeClass('active');
        });
