        $('#addbox').click(function () {
            $('#addbox1').show();
            $("#addbox1").delay(4000).fadeOut(200);
        });
        $('#addbox11 #close-modal').click(function () {
            $('#addbox1').hide();
            $("#shadow").fadeTo(200, 0);
            $('#shadow').hide();
        });
        $('.showmodal').click(function () {
            $('.modal-box').hide();
            $('.modal-box#' + $(this).attr('rel')).show();
        });
         $('.modal-box .button').click(function () {
            $('.modal-box').hide();
            $("#shadow").fadeTo(200, 0);
            $('#shadow').hide();
        });
        
                $('#selectsize').click(function () {
            $('#selectsize1').show();
        });
        $('#saveselect').click(function () {
            $('#selectsize1').hide();
            $("#shadow").fadeTo(200, 0);
            $('#shadow').hide();
        });

        $('.fieldset .tabholder input').click(function () {
            $('.fieldset .tabholder .tooltip_info').removeClass('selected');
            $(this).parent().find('.tooltip_info').addClass('selected');
        });
        $("body").click(function () {
            $('.fieldset .tabholder .tooltip_info').removeClass('selected');
        });
        $(".fieldset .tabholder input").click(function (e) {
            e.stopPropagation();
        });
                $('ul.tabs li a').click(function () {
            $('.tabholder#1').hide();
            $('.tabholder#2').hide();
            $('.tabholder#' + $(this).attr('rel')).show();
            $('ul.tabs li').removeClass('active');
            $(this).parent().addClass('active')
            return false;
        });
        
                $('.row-fluid .button.gostep').click(function () {
            $('.container-left #' + $(this).attr('rel')).fadeTo(300, 1);
            $(this).parent().parent().parent().hide();
            return false;
        });
        
                $('ul.nav.nav-tabs li span').click(function () {
            $('ul.nav.nav-tabs li').removeClass('active');
            $(this).parent().toggleClass('active');
            $('.tab-content .tab-pane').removeClass('active');
            $('.tab-content .tab-pane#' + $(this).attr('rel')).toggleClass('active');
        });
