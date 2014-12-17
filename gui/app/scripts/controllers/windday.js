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
    $scope.conditions = {}
    $scope.conditions.height = 50;
    $scope.conditions.maxws = 10.0;
    $scope.conditions.maxhours = 4;
    $scope.conditions.starthr = 7;
    $scope.conditions.consecutive = true;
    $scope.conditions.daylength = 10;
    $scope.conditions.certainty = 0.9;
    $scope.expectedLoaded = false;
    $scope.risksLoaded = false;
    $scope.yearlyLoaded = false;
    $http.get('/api/windday')
    .success(function(data, status, headers, config) {
      if (!data.result.exists){
        $location.path('/upload');
      }
      $scope.seasonality = data.result.seasonality;
      $scope.yearlyLoaded = true;
    })
    .error(function(data, status, headers, config) {
      //console.log(data);
    });
    
    $scope.estimate = function(){
      $scope.expectedLoaded = false;
      $scope.risksLoaded = false;
      $http.post('/api/windday/expected',$scope.conditions)
      .success(function(data,status,headers,config){
        $scope.expected = {byMonth: data.result.byMonth,cumulative:data.result.cumulative};
        $scope.expectedLoaded = true;
      })
      .error(function(data,status,headers,config){
        //console.log(data);
      });
      
      $http.post('/api/windday/risks',$scope.conditions)
      .success(function(data,status,headers,config){
        $scope.risks = data.result.risks;
        $scope.risksLoaded = true;
      })
      .error(function(data,status,headers,config){
        //console.log(data);
      });
    };
    
    $scope.newWindFile = function(){
      $location.path('/upload');
    };
    
    $scope.estimate();
  });
