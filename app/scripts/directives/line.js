'use strict';

/**
 * @ngdoc directive
 * @name windopsApp.directive:line
 * @description
 * # line
 */
angular.module('windopsApp')
  .directive('line', function () {
  return {
    restrict: 'C',
    replace: true,
    scope: {
      items: '='
    },
    controller: function ($scope, $element, $attrs) {
      console.log(2);

    },
    template: '<div id="container2" style="margin: 0 auto">not working</div>',
    link: function (scope, element, attrs) {
      console.log(scope);
      var data = scope.items;
      var chart = new Highcharts.Chart({
        chart: {
            renderTo: 'container2',
            marginTop: 60,
            marginBottom: 40
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        },
        yAxis: {
            title: {
                text: 'Expected Wind Days'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: ' wind days'
        },
        
        credits: {
            enabled: false
        },
        
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [{
            name: 'By Month',
            data: data.byMonth
        }, {
            name: 'Cumulative',
            data: data.cumulative
        }]
    });
      scope.$watch("items", function (newValue) {
        chart.series[0].setData(newValue.byMonth, true);
        chart.series[1].setData(newValue.cumulative,true);
      }, true);
      
    }
  };
});
