function date_str(time){
    //fix different timezone
    time.hour -= 1

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

    if(gen_link) {
        let a = document.createElement('a');
        a.innerText = "Refresh";
        a.href = "javascript:window.location.href=window.location.href";
        a.class = "text-white";
        document.getElementById("refresh").appendChild(a);
        gen_link = false;
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

let gen_link = true;
let new_date = new Date;

let this_script = document.currentScript;
let old_date_str = this_script.getAttribute("time");
let old_date = new Date(old_date_str);
console.log("Data old",old_date);
console.log("Data new", new_date);

// get total seconds between the times
let total_seconds = Math.floor(Math.abs(new_date - old_date) / 1000);

$('#time').text(date_str(calc_time(total_seconds)));

date_str(calc_time(total_seconds));
//chiamata ogni secondo

setInterval(function() {
    total_seconds += 1;
    $('#time').text(date_str(calc_time(total_seconds)));
}, 1000);
