console.log("testing")

function checkCookie(){
    alert("show")
    //console.log(document.cookie);
    var visit = getCookie("cookie");
    console.log(visit);
    if (visit == null) {
        //$("#"+div_id).show()
        //$('#dealsmailinglist').show();
        $('#ModalApp').modal('show');
        //$("#ModalApp").show();
        //$("#shadow").fadeTo(200,0.5);
        //alert("Your Message Goes here and you only get to see it once!");
        var expire = new Date();
        expires_in_seconds = 86400000;//86400; //24hrs
        expire = new Date(expire.getTime() + expires_in_seconds);
        document.cookie = "cookie=here; expires=" + expire;
        
    }
    //uncomment to delete cookie
    //del_cookie('cookie');
}


function del_cookie(name)
{
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function getCookie(c_name) {
    var c_value = document.cookie;
    var c_start = c_value.indexOf(" " + c_name + "=");
    if (c_start == -1) {
        c_start = c_value.indexOf(c_name + "=");
    }
    if (c_start == -1) {
        c_value = null;
    } else {
        c_start = c_value.indexOf("=", c_start) + 1;
        var c_end = c_value.indexOf(";", c_start);
        if (c_end == -1) {
            c_end = c_value.length;
        }
        c_value = unescape(c_value.substring(c_start, c_end));
    }
    return c_value;
}