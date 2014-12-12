'use strict';

/**
 * @ngdoc directive
 * @name windopsApp.directive:heatmap
 * @description
 * # heatmap
 */
angular.module('windopsApp')
  .directive('heatmap', function () {
  return {
    restrict: 'C',
    replace: true,
    scope: {
      items: '='
    },
    controller: function ($scope, $element, $attrs) {
      //console.log(2);

    },
    template: '<div id="container" style="margin: 0 auto">not working</div>',
    link: function (scope, element, attrs) {
      //console.log(3);
      var data = scope.items;
      var chart = new Highcharts.Chart({
        

        chart: {
            type: 'heatmap',
            renderTo: 'container',
            marginTop: 60,
            marginBottom: 40
        },


        title: {
            text: ''
        },

        xAxis: {
            categories: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
            title: {
              text: 'Month of the Year'
            }
        },

        yAxis: {
            categories: ['00:00','01:00','02:00','03:00','04:00','05:00','06:00'
            ,'07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00',
            '15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00',
            '23:00'],
            title: {
              text: 'Hour of the Day'
            }
        },

        colorAxis: {
            stops: [
                [0, '#3060cf'],
                [0.5, '#fffbbc'],
                [0.9, '#c4463a'],
                [1, '#c4463a']
            ],
            startOnTick: false,
            endOnTick: false,
            labels: {
                format: '{value} m/s'
            }
        
        },
        
        credits: {
            enabled: false
        },

        legend: {
            align: 'center',
            layout: 'horizontal',
            verticalAlign: 'top'
        },

        tooltip: {
            formatter: function () {
                return 'Average wind speed the month of '+'<b>' + 
                this.series.xAxis.categories[this.point.x] + '</b><br> at <b>' 
                + this.series.yAxis.categories[this.point.y]+ '</b>:<br><b>' +
                this.point.value +' m/s</b>';
            }
        },

        series: [{
            name: 'Median Wind Speed',
            borderWidth: 1,
            data: data,
            dataLabels: {
                enabled: false,
                color: 'black',
                style: {
                    textShadow: 'none',
                    HcTextStroke: null
                }
            }
        }]

    
      });
      scope.$watch("items", function (newValue) {
        chart.series[0].setData(newValue, true);
      }, true);
      
    }
  };
});

function maxWind(array) {
  array.sort(function(a,b){
    var x=a[2];
    var y = b[2];
    return y-x;
  });
  return array[0][2];
}

function minWind(array) {
  array.sort(function(a,b){
    var x=a[2];
    var y = b[2];
    return x-y;
  });
  return array[0][2];
}
