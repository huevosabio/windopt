'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:WinddayCtrl
 * @description
 * # WinddayCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('WinddayCtrl',  function($scope, $location,$http) {
    $http.get('/api/windday')
    .success(function(data, status, headers, config) {
      if (!data.result.exists){
        $location.path('/upload');
      }
    })
    .error(function(data, status, headers, config) {
      console.log(data);
    });
  });
