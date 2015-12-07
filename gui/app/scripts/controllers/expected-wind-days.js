'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:ExpectedWindDaysCtrl
 * @description
 * # ExpectedWindDaysCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('ExpectedWindDaysCtrl', function ($scope, $location, $http, currentProject) {
     $http.post('/api/windday/'  + currentProject.project.name)
    .success(function(data, status, headers, config) {
      console.log(data)
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
