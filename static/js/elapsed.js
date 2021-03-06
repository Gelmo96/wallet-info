function date_str(time){

    //i secondi sempre
    let str = "" + time.sec + "s ago."
    //se ho i minuti
    if (time.min != 0){
        str = time.min + "m " + str;
        //se ho ore e minuti
        if (time.hour != 0){
            str = time.hour + "h " + str;
        }
    } else {
        //se ho ore e secondi
        if (time.hour != 0) {
            str = time.hour + "h 0m " + str;
        }
    }
    str = "Data updated " + str;

    let refresh = document.getElementById("refresh");
    if (time.min >= 1 || time.hour > 0) {
        refresh.style.display = "block";
    } else {
        refresh.style.display = "none";
    }

    return str;
}

function calc_time(delta){

    // calculate (and subtract) whole hours
    let hours = Math.floor(delta / 3600) % 24;
    delta -= hours * 3600;

    // calculate (and subtract) whole minutes
    let minutes = Math.floor(delta / 60) % 60;
    delta -= minutes * 60;

    // what's left is seconds
    let seconds = delta % 60;  // in theory the modulus is not required

    return {
        hour: hours,
        min: minutes,
        sec: seconds
    }
}

function refresh (e){
    e.preventDefault();
    $('img#loading').show();
    $.getJSON('/collect_data',function(data) {

        $('img#loading').hide();

        if (!data["ok"]) {
            $('span#error').show();
            setTimeout(function () {
                $('span#error').hide();
            }, 5000);
        } else {
            location.reload();
        }
    });
    return;
}

$('a#refresh').click(function(e) { return refresh(e) } );

// on click bottone refresh data
/*
$('a#refresh').on('click', function(e) {
    e.preventDefault()
    $('span#loading').show()
    $.getJSON('/collect_data',function(data) {
        $('span#loading').hide()
        if (!data["ok"]){
            $('span#error').show();
            setTimeout(function() = { $('span#error').hide() }, 5000);
        }

    });
    return false;
});
*/

let new_date = new Date;
new_date.setHours(new_date.getHours()-1);

let this_script = document.currentScript;
let old_date_str = this_script.getAttribute("time");
let old_date = new Date(old_date_str);
console.log("Data old:",old_date);
console.log("Data new:", new_date);

// get total seconds between the times
let total_seconds = Math.floor(Math.abs(new_date - old_date) / 1000);

$('#time').text(date_str(calc_time(total_seconds)));

date_str(calc_time(total_seconds));
//chiamata ogni secondo

setInterval(function() {
    total_seconds += 1;
    $('#time').text(date_str(calc_time(total_seconds)));
}, 1000);
