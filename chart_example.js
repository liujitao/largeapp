$(function () {

  /* https://gist.github.com/devomacdee/1fe304d933858fefc67a65a881645069
https://gist.github.com/PedroGutierrezStratio/98a2c6d5298ec92e64ef */

  var chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(231,233,237)'
  };

  var startDate = "{{ date_start }}";
  var endDate = "{{ date_end }}";
  var selectedAccount = "{{ selected_account }}";

  $('#date-start').val("");
  $('#date-end').val("");

  firstCall();
  $('#account').selecter();

  $('#help-auto-reach').qtip({
    style: { classes: 'qtip-bootstrap' },
    content: {
      title: 'Automatically reach goal',
      text: 'A new weekly ongoing transfer will be setup to reach this goal automatically by the end date.<br><br>If no end date is set, automatic reach won\'t be turned on.'
    }
  });

  var dateChanged = false;
  $('#date-start').datepicker({
    dateFormat: 'mm.dd.yy',
    showOn: "both",
    buttonImage: "/static/images/calendar.png",
    buttonImageOnly: true,
    maxDate: 'd',
    onSelect: function (dateText, inst) {
      minDate();
      accountChanged = false;
      dateChanged = true;
    }
  });

  $('#date-end').datepicker({
    dateFormat: 'dd.mm.yy',
    maxDate: 'd',
    showOn: "both",
    buttonImage: "/static/images/calendar.png",
    buttonImageOnly: true,
    onSelect: function (dateText, inst) {
      accountChanged = false;
      dateChanged = true;
    }
  });
  var dataDictionary = [];
  var minRange = 5000;
  var maxRange = 10;

  Chart.defaults.global.defaultFontColor = '#666';
  Chart.defaults.global.defaultFontFamily = 'montserratregular';
  Chart.defaults.global.defaultFontSize = 15;

  function callChart() {
    var dateLabels = [];
    for (item in dataDictionary) {
      if (typeof dataDictionary[item].date !== 'undefined') {
        dateLabels.push(new Date(dataDictionary[item].date));
      }
    }
    var tooltipLabels = [];
    for (item in dataDictionary) {
      if (typeof dataDictionary[item].date !== 'undefined') {
        tooltipLabels.push(dataDictionary[item].date);
      }
    }
    var valueLabels = [];
    for (item in dataDictionary) {
      if (typeof dataDictionary[item].total_value !== 'undefined') {
        valueLabels.push(dataDictionary[item].total_value);
      }
    }
    var data = {
      labels: dateLabels,
      datasets: [
        {
          label: 'Total',
          fill: false,
          fillColor: "#74BAFC",
          lineTension: 0,
          borderColor: "#74BAFC",
          borderCapStyle: 'butt',
          borderDash: [],
          borderDashOffset: 0.0,
          borderJoinStyle: 'miter',
          pointBorderColor: "rgba(75,192,192,1)",
          pointBackgroundColor: "#fff",
          pointBorderWidth: 1,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#74BAFC",
          pointHoverBorderWidth: 2,
          pointRadius: 0,
          pointHitRadius: 2,
          data: valueLabels,
          spanGaps: true,
        },
      ]
    };


    var myChart = new Chart(document.getElementById("lineChart"), {
      type: 'line',
      data: data,
      options: {
        scales: {
          xAxes: [{
            gridLines: {
              display: false,
            },
            ticks: {
              display: true,
              padding: 15,
              maxRotation: 0,
            },
            type: 'time',
            time: {
              unit: 'month',
              round: 'day',
              parser: false,
              format: 'mmm',
              displayFormats: {
                'millisecond': 'MMM',
                'second': 'MMM',
                'minute': 'MMM',
                'hour': 'MMM',
                'day': 'MMM',
                'week': 'MMM',
                'month': 'MMM',
                'quarter': 'MMM',
                'year': 'MMM',
              }
            },
          }],
          yAxes: [{
            ticks: {
              beginAtZero: false,
              suggestedMin: (~~((minRange - 1) * 1) / 1),
              suggestedMax: (~~((maxRange + 3) / 3) * 3),
              maxTicksLimit: 4,
              //minMaxMultiplier : 1.2,
              padding: 25,
              callback: function (label, index, labels) {
                return '$ ' + label;
              },
            },
          }]
        },
        tooltips: {
          backgroundColor: 'rgb(253,253,253,0.8)',
          titleFontColor: '#666',
          titleFontFamily: 'montserratregular',
          titleFontSize: 14,
          bodyFontColor: '#666',
          bodyFontFamily: 'montserratregular',
          bodyFontSize: 14,
          xPadding: 15,
          yPadding: 15,
          enable: true,
          mode: 'label',
          bodySpacing: 8,
          callbacks: {
            title: function () {
              // Title doesn't make sense for scatter since we format the data as a point
              return '';
            },
            label: function (tooltipItem) {
              var returnString = [];
              returnString.push(dateFormat(tooltipItem.xLabel, 'mmm dd'));
              returnString.push('Value: $' + tooltipItem.yLabel.toFixed(2))
              return returnString;
            },
          },

        },
        legend: {
          display: false
        }

      }
    });
    legend(document.getElementById("lineLegend"), data);
    var ctx = document.getElementById("lineChart").getContext("2d");
  }


  $('#search').click(function () {
    var dateStart = $('#date-start').val();
    var dateEnd = $('#date-end').val();
    var re = /^([0-9]{2}\.[0-9]{2}\.[0-9]{4})$/;
    var dateStart = $('#date-start').val().split('.');
    var dateStartYear = dateStart[2];
    var dateStartMonth = dateStart[0];
    var dateStartDay = dateStart[1];
    var newDateStart = dateStartYear + '-' + dateStartMonth + '-' + dateStartDay;
    var dateEnd = $('#date-end').val().split('.');
    var dateEndYear = dateEnd[2];
    var dateEndMonth = dateEnd[1];
    var dateEndDay = dateEnd[0];
    var newDateEnd = dateEndYear + '-' + dateEndMonth + '-' + dateEndDay;
    location.href = '/main/performance/' + selectedAccount + '/?date_start=' + newDateStart + '&date_end=' + newDateEnd;
  });
  
  function firstCall() {
    $.ajax({
      type: 'GET',
      url: '/api/performance/' + selectedAccount + '?date_start=' + startDate + '&date_end=' + endDate,
      dataType: 'json',
      success: function (data, textStatus, jqXHR) {
        var parsedAjax = JSON && JSON.parse(jqXHR.responseText) || $.parseJSON(jqXHR.responseText);
        for (item in parsedAjax.performance_list) {
          dataDictionary.push({ 'date': parsedAjax.performance_list[item].date, 'total_value': parsedAjax.performance_list[item].total_value });

          $('#table-titles').after('<tr><td>' + parsedAjax.performance_list[item].date + '</td><td class="sum-column"><strong>' + '$' + parseFloat(parsedAjax.performance_list[item].total_value).toFixed(2) + '</strong></td></tr>');

          if (parsedAjax.performance_list[item].total_value > maxRange) {
            maxRange = parsedAjax.performance_list[item].total_value;
          }
          if (parsedAjax.performance_list[item].total_value < minRange) {
            minRange = parsedAjax.performance_list[item].total_value;
          }
        }
      }
    }).done(function () {
      callChart();
      $('#date-start').val(dataDictionary[0].date);
      $('#date-end').val(dataDictionary[dataDictionary.length - 1].date);
    });
  }
});


function validateDate(date, re) {
  if (!re.test(date))
    return false;

  var parts = date.split(".");
  var day = parseInt(parts[1], 10);
  var month = parseInt(parts[0], 10);
  var year = parseInt(parts[2], 10);

  // Check the ranges of month and year
  if (year < 1000 || year > 3000 || month == 0 || month > 12)
    return false;

  var monthLength = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

  // Adjust for leap years
  if (year % 400 == 0 || (year % 100 != 0 && year % 4 == 0))
    monthLength[1] = 29;

  // Check the range of the day
  return day > 0 && day <= monthLength[month - 1];
}