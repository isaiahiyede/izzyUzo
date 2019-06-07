
function updateTime(hrs_diff){
    var currentTime = new Date();
    
    var currentHours = currentTime.getHours() + hrs_diff;
    var currentMinutes = currentTime.getMinutes();
    var currentSeconds = currentTime.getSeconds();
    
    // Pad the hours, minutes and seconds with leading zeros, if required
    currentHours = ( currentHours < 10 ? "0" : "") + currentHours;
    currentMinutes = ( currentMinutes < 10 ? "0" : "") + currentMinutes;
    currentSeconds = ( currentSeconds < 10 ? "0" : "") + currentSeconds;
    
    // Choose either "AM" or "PM" as appropriate
    var timeOfDay = ( currentHours < 12 ) ? "AM" : "PM";
    
    // Convert the hours component to 12-hour format if needed
    currentHours = ( currentHours > 12 ) ? currentHours - 12 : currentHours;
        
    // Convert an hours component of "0" to "12"
    currentHours = ( currentHours == 0 ) ? 12: currentHours;
    
    // Compose the string for display
    var currentTimeString = currentHours + ":" + currentMinutes + ":" + currentSeconds + " " + timeOfDay;
    // Update the time display
    //document.getElementById("time").firstChild.nodeValue = currentTimeString;
    document.getElementById("time").childNodes[1].nodeValue = currentTimeString;

}