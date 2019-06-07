

        $('.mtoggle').click(function () {
            $(this).toggleClass('open');
            $('.navigation').toggleClass('open');
        });
        
         $('.bt-out').click(function () {
            $(this).parent().toggleClass('active');
            $('.top_info li.last').toggleClass('active');
        });
        
           $('#features ul.nav-tabs li').click(function () {
            $(this).parent().find('.active').removeClass('active');
            $(this).toggleClass('active');
            $('#features .tab-holder .tab-panel').removeClass('active');
            $('#features .tab-holder .tab-panel#' + $(this).attr('rel')).toggleClass('active');
        });

        $('#pack.select').click(function () {
            $('#pack.select').removeClass('sticky');
            $('.check').removeAttr('Checked');
            $(this).toggleClass('sticky');
            $('#pack.select.sticky .check').attr('Checked', 'Checked');
        });
        $('.your_cart .expand .down').click(function () {
            $(this).parent().find('.info').toggleClass('selected');
        });
                $('.cart .dropdown').click(function () {
            $(this).toggleClass('selected');
            $('.cart .your_cart').toggleClass('selected');
        });
                $('.method input').click(function () {
            $('.method').removeClass('selected');
            $(this).parent().toggleClass('selected');
        });
