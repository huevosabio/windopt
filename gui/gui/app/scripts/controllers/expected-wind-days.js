'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:ExpectedWindDaysCtrl
 * @description
 * # ExpectedWindDaysCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('ExpectedWindDaysCtrl', function ($scope, $location,$http) {
     $http.post('/api/windday')
    .success(function(data, status, headers, config) {
      if (!data.result.exists){
        $location.path('/upload');
      }
      $scope.seasonality = data.result.seasonality;
      console.log($scope.seasonality);
    })
    .error(function(data, status, headers, config) {
      console.log(data);
    });
  });
