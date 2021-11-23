function updateDate(newDateText) {
    $("#lastMeasurementTime").empty().append(newDateText);
}

function updatePressureData(data) {
    var currentStage = $('#selectedStageName').text();
    try {
        var stageData = data[currentStage]['data'];
        var date = new Date(data[currentStage]['time']);
        updateDate(date.toString());
        updateGauge('pressureGauge', stageData);
    }
    catch(err) {
        updateDate("No Measurement Available");
        updateGauge('pressureGauge', "No Data");
    }
}

var nullDataCount = 0;

function getPressureData(showLoading) {
    var currentIMEI = $('#imei').val();
    if (showLoading) {
        $('#loading').show();
        $('.gauge-example').addClass('divOpac');
        $.ajax({
            type: "GET",
            url: "/get_hvac_data?imei=" + currentIMEI,
            success: function(data) {
                updatePressureData(data);
            },
            complete: function(){
            $('#loading').hide();
            $('.gauge-example').removeClass('divOpac');
            }
        });
    }else {
        $.ajax({
            type: "GET",
            url: "/get_hvac_data?imei=" + currentIMEI,
            success: function(data) {
                updatePressureData(data);
            }
        });
    }
}

function updateGauge(id, newVal) {
    if ( newVal != "No Data" ) {
        var newGaugeValue;
        if (newVal > 3){
            newGaugeValue = 100;
        }else{
            newGaugeValue = Math.floor(((newVal) / (3)) * 100);
        }
        $("#pressureGauge").css({"--gauge-value": newGaugeValue});
        $("#pressureDeltaValue").empty().append(newVal);
    }else {
        $("#pressureGauge").css({"--gauge-value": 0});
        $("#pressureDeltaValue").empty().append(newVal);
    }
}

function onReady(callback) {
    var intervalID = window.setInterval(checkReady, 1000);

    function checkReady() {
        if (document.getElementsByTagName('body')[0] !== undefined) {
            window.clearInterval(intervalID);
            callback.call(this);
        }
    }
}

function show(id, value) {
    document.getElementById(id).style.display = value ? 'block' : 'none';
}

function removeLoader(){
    $( "#loading" ).fadeOut(100, function() {
      show('page', true);
  });
}

document.addEventListener("DOMContentLoaded", function(){
    getPressureData(false);
    setTimeout(removeLoader, 1000);
    if ($("button.button-tag")) {
        $(".button-tag").click(function (e) {
            var newStage = e.target.innerHTML;
            $('#selectedStageName').empty().append(newStage);
            getPressureData(true);
        });
    }
    $( "#ahuSelect" ).change(function() {
        var newImei = $( "#ahuSelect" ).val();
        var dashboardId = $( "#dashboardID" ).val();
        window.location.replace("/dashboard/?id=" + dashboardId + "&imei=" + newImei);
    });
});

setInterval(function() {
    getPressureData(false);
}, 5000);
