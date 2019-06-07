    $('.countdowntimer').each(function(){
	var self = $(this);
	date_string = self.attr('data-date');
	id = self.attr('id');
	// set the date we're counting down to
	var target_date = new Date(date_string).getTime();
	 
	// variables for time units
	var days, hours, minutes, seconds;
	 
	// get tag element
	var countdown = document.getElementById(id);
	 
	// update the tag with id "countdown" every 1 second
	setInterval(function () {
	 
	    // find the amount of "seconds" between now and target
	    var current_date = new Date().getTime();
	    var seconds_left = (target_date - current_date) / 1000;
	 
	    // do some time calculations
	    days = parseInt(seconds_left / 86400);
            seconds_left = seconds_left % 86400;
            if (days > 0) {
                days = days;
            }
            else{
                days = 0;
            }
            
            hours = parseInt(seconds_left / 3600);
            seconds_left = seconds_left % 3600;
            if (hours > 0) {
                hours = hours ;
            }
            else{
                hours = 0;
            }
	    
	    minutes = parseInt(seconds_left / 60);
	    seconds = parseInt(seconds_left % 60);
	    if (minutes > 0) {
                minutes = minutes;
            }
            else{
                minutes = 0
            }
            
            if (seconds > 0) {
                seconds = seconds
            }
	    else{
                seconds = 0
	    }
	    // format countdown string + set tag value
	    countdown.innerHTML = days + "d " + hours + "h "
	    + minutes + "m " + seconds + "s";
	    
	}, 1000);
    });
    
    $('.jquery-countdown').each(function(){
	var self = $(this);
        if (self.attr('data-date')) {
           
            date_string = self.attr('data-date');
            id = self.attr('id');
            // set the date we're counting down to
            var target_date = new Date(date_string).getTime();
             
            // variables for time units
            var days, hours, minutes, seconds;
             
            // get tag element
            var countdown = document.getElementById(id);
             
            // update the tag with id "countdown" every 1 second
            setInterval(function () {
             
                // find the amount of "seconds" between now and target
                var current_date = new Date().getTime();
                var seconds_left = (target_date - current_date) / 1000;
             
                // do some time calculations
                days = parseInt(seconds_left / 86400);
                seconds_left = seconds_left % 86400;
                if (days > 0) {
                    days = days;
                }
                else{
                    days = 0;
                }
                
                hours = parseInt(seconds_left / 3600);
                seconds_left = seconds_left % 3600;
                if (hours > 0) {
                    hours = hours ;
                }
                else{
                    hours = 0;
                }
                
                minutes = parseInt(seconds_left / 60);
                seconds = parseInt(seconds_left % 60);
                if (minutes > 0) {
                    minutes = minutes;
                }
                else{
                    minutes = 0
                }
                
                if (seconds > 0) {
                    seconds = seconds
                }
                else{
                    seconds = 0
                }
                // format countdown string + set tag value
                
                countdown.innerHTML = "<span>" + days + "d " + hours + "h "
                + minutes + "m " + seconds + "s" + "<span>";  
             
            }, 1000);
        }
    });
	

	
	