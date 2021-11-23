function updateSunStyle(indoorText, outdoorText) {
    $('#indoorSunStyle').empty().append(indoorText);
    $('#outdoorSunStyle').empty().append(outdoorText);
}

function fillData(data) {
    if (data['indoorClass'] == 'Good') {{
        $('#indoorClass').empty().append('Healthy');
    }} else {
        $('#indoorClass').empty().append(data['indoorClass']);
    }
    if (data['outdoorClass'] == 'Good') {{
        $('#outdoorClass').empty().append('Healthy');
    }} else {
        $('#outdoorClass').empty().append(data['outdoorClass']);
    }
    if (isNaN(data['indoorValue'])) {
        addBlur();
    } else {
        removeBlur();
    }
    $('#indoorValue').empty().append(data['indoorValue']);
    $('#outdoorValue').empty().append(data['outdoorValue']);
    $('#indoorTemp').empty().append(data['indoorTemp']);
    $('#outdoorTemp').empty().append(data['outdoorTemp']);
    $('#indoorHum').empty().append(data['indoorHum']);
    $('#outdoorHum').empty().append(data['outdoorHum']);
    $('#indoorPollUnits').empty().append(data['poll_units']);
    $('#outdoorPollUnits').empty().append(data['poll_units']);
}

function addBlur(){
    $('.centerScreen').removeClass('hide');
    $('.facilityInfo').addClass('blur');
    $('.includeOutdoor').addClass('blur');
    $('.selectStyle').addClass('blur');
    $('.topSpace').addClass('blur');
}

function removeBlur(){
    $('.centerScreen').addClass('hide');
    $('.facilityInfo').removeClass('blur');
    $('.includeOutdoor').removeClass('blur');
    $('.selectStyle').removeClass('blur');
    $('.topSpace').removeClass('blur');
}

function getClassColor(classText){
    colorDict = {
        'Good': '#04F000',
        'Moderate': '#E5F300',
        'Unhealthy for sensitive groups': '#F38C00',
        'Unhealthy': '#F33B00',
        'Very Unhealthy': '#F30000',
        'Hazardous': '#A600F3',
        'N/A': '#b3b3b3',
        'Low Risk': '#04F000',
        'Moderate Risk': '#F38C00',
        'High Risk': '#F30000'
    };
    return colorDict[classText];
}

function updateCircleColor(data) {
    var indoorColor = getClassColor(data['indoorClass'])
    var outdoorColor = getClassColor(data['outdoorClass'])
    var baseWidth = 16;
    var raySize1 = baseWidth * 0.5;
    var raySize2 = baseWidth * 0.4;
    var raySize3 = baseWidth * 0.3;
    var raySize4 = baseWidth * 0.25;
    var raySize5 = baseWidth * 0.2;
    var indoorSunText = `
    .indoorSun {
        width: ${baseWidth}vw;
        height: ${baseWidth}vw;
        background-color:${indoorColor};
        border-radius: 50%;
        box-shadow: 0 0 0 ${raySize4}vw ${indoorColor}80,
            0 0 0 ${raySize5}vw ${indoorColor}40,
            0 0 0 ${raySize3}vw ${indoorColor}20,
            0 0 0 ${raySize2}vw ${indoorColor}10,
            0 0 0 ${raySize1}vw ${indoorColor}00,
            0 0 ${raySize5}vw ${raySize1}vw ${indoorColor}10;
        animation: indoorRays 7s infinite ease;
        }
        @keyframes in {0% {box-shadow: none;}}
        @keyframes indoorRays {0% {
            box-shadow: 0 0 0 0 ${indoorColor}80,
            0 0 0 ${raySize4}vw ${indoorColor}80,
            0 0 0 ${raySize5}vw ${indoorColor}40,
            0 0 0 ${raySize3}vw ${indoorColor}20,
            0 0 0 ${raySize2}vw ${indoorColor}10,
            0 0 ${raySize5}vw ${raySize1}vw ${indoorColor}10;
            }
        100% {
            box-shadow:0 0 0 ${raySize4}vw ${indoorColor}80,
            0 0 0 ${raySize5}vw ${indoorColor}40,
            0 0 0 ${raySize3}vw ${indoorColor}20,
            0 0 0 ${raySize2}vw ${indoorColor}10,
            0 0 0 ${raySize1}vw ${indoorColor}00,
            0 0 ${raySize5}vw ${raySize1}vw ${indoorColor}10;
         }
     }
     `;
    var outdoorSunText = `
    .outdoorSun {
        width: ${baseWidth}vw;
        height: ${baseWidth}vw;
        background-color:${outdoorColor};
        border-radius: 50%;
        box-shadow: 0 0 0 ${raySize4}vw ${outdoorColor}80,
            0 0 0 ${raySize5}vw ${outdoorColor}40,
            0 0 0 ${raySize3}vw ${outdoorColor}20,
            0 0 0 ${raySize2}vw ${outdoorColor}10,
            0 0 0 ${raySize1}vw ${outdoorColor}00,
            0 0 ${raySize5}vw ${raySize1}vw ${outdoorColor}10;
        animation: outdoorRays 7s infinite ease;
        }
        @keyframes in {0% {box-shadow: none;}}
        @keyframes outdoorRays {0% {
            box-shadow: 0 0 0 0 ${outdoorColor}80,
            0 0 0 ${raySize4}vw ${outdoorColor}80,
            0 0 0 ${raySize5}vw ${outdoorColor}40,
            0 0 0 ${raySize3}vw ${outdoorColor}20,
            0 0 0 ${raySize2}vw ${outdoorColor}10,
            0 0 ${raySize5}vw ${raySize1}vw ${outdoorColor}10;
            }
        100% {
            box-shadow:0 0 0 ${raySize4}vw ${outdoorColor}80,
            0 0 0 ${raySize5}vw ${outdoorColor}40,
            0 0 0 ${raySize3}vw ${outdoorColor}20,
            0 0 0 ${raySize2}vw ${outdoorColor}10,
            0 0 0 ${raySize1}vw ${outdoorColor}00,
            0 0 ${raySize5}vw ${raySize1}vw ${outdoorColor}10;
         }
     }
     `;
     updateSunStyle(indoorSunText, outdoorSunText);
}

function convertStringPollutantToStandardName(stringName) {
    var outputDict = {
        "Air Quality Index": "Total_AQI",
        "Carbon Dioxide": "cotwo",
        "Organic Compounds": "voc",
        "Fine Dust Matter": "pmtwo",
        "Coarse Dust Matter": "pmten",
        "CAIRS Score": "covid_risk"
    };
    return outputDict[stringName];
}

function updatePollutantValues() {
    var currentPoll = convertStringPollutantToStandardName($('#pollSelect').val());
    var currentMac = $('#macAddress').val();
    var currentFacility = $('#facilityName').val();
    var isFacility = $('#isFacility').val();

    if (isFacility) {
        $.ajax({
            type: "GET",
            url: "/get_aq_data?fac=" + currentFacility + "&mac=" + currentMac + "&poll=" + currentPoll,
            success: function(data) {
                fillData(data);
                $('#indoorNum').empty().append(data);
                updateCircleColor(data);
            }
        });
    }else {
        $.ajax({
            type: "GET",
            url: "/get_aq_data?fac=" + currentFacility + "&poll=" + currentPoll,
            success: function(data) {
                fillData(data);
                $('#indoorNum').empty().append(data);
                updateCircleColor(data);
            }
        });
    }
}

function updateSelectedPollutant() {
    var selectedPoll = $('#pollSelect').val()
    $('#indoorSelectedPoll').empty().append(selectedPoll);
    $('#outdoorSelectedPoll').empty().append(selectedPoll);

    if (selectedPoll == 'Carbon Dioxide') {
        $('#outdoorDiv').addClass('hide');
        $('#indoorDiv').removeClass('row');
        $('#toggleOutdoor').addClass('hide');
    }
    if (selectedPoll == 'Organic Compounds') {
        $('#outdoorDiv').addClass('hide');
        $('#indoorDiv').removeClass('row');
        $('#toggleOutdoor').addClass('hide');
    }
    if (selectedPoll == 'Fine Dust Matter') {
        $('#outdoorDiv').removeClass('hide');
        $('#indoorDiv').addClass('row');
        $('#toggleOutdoor').removeClass('hide');
    }
    if (selectedPoll == 'Coarse Dust Matter') {
        $('#outdoorDiv').removeClass('hide');
        $('#indoorDiv').addClass('row');
        $('#toggleOutdoor').removeClass('hide');
    }
    if (selectedPoll == 'Air Quality Index') {
        $('#outdoorDiv').removeClass('hide');
        $('#indoorDiv').addClass('row');
        $('#toggleOutdoor').removeClass('hide');
    }
    if (selectedPoll == 'CAIRS Score') {
        $('#outdoorDiv').addClass('hide');
        $('#indoorDiv').removeClass('row');
        $('#toggleOutdoor').addClass('hide');
    }
}

function updateHideOutdoorButtonText() {
    if ($("#outdoorDiv").hasClass('hide')) {
        $("#toggleOutdoor").empty().append('Show Outdoor')
    }
    else {
        $("#toggleOutdoor").empty().append('Hide Outdoor')
    };
}

function updateDate() {
    var options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' };
    $("#curDate").empty().append(new Date().toLocaleDateString("en-US", options));
}

document.addEventListener("DOMContentLoaded", function(){
    updateDate()
    updatePollutantValues();

    $("#toggleOutdoor").click(function() {
        $('#outdoorDiv').toggleClass('hide');
        $('#indoorDiv').toggleClass('row');
        updateHideOutdoorButtonText()
    });

    $( "#pollSelect" ).change(function() {
        updateSelectedPollutant();
        updatePollutantValues();
        updateHideOutdoorButtonText()
    });
});


const valList = ['Air Quality Index', 'Carbon Dioxide',
                 'Organic Compounds', 'Fine Dust Matter',
                 'Coarse Dust Matter', 'CAIRES Score'];
var valIdx = 0;
setInterval(function() {
    updatePollutantValues();
    updateDate();

}, 5000);

setInterval(function() {
    /*
    valIdx = valIdx + 1;
    if (valIdx > valList.length - 1) {
        valIdx = 0;
    }
    $("#pollSelect").val(valList[valIdx]);
    */
    updateSelectedPollutant();
    updatePollutantValues();
    updateHideOutdoorButtonText();

}, 15000);
