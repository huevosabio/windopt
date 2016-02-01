'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:WinddayCtrl
 * @description
 * # WinddayCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('WinddayCtrl',  function(
    $scope,
    $location,
    $alert,
    $http,
    currentProject,
    windday,
    polling
    ){

    $scope.conditions = {}
    $scope.conditionsEnabled = false
    $scope.expectedLoaded = false;
    $scope.risksLoaded = false;
    $scope.yearlyLoaded = false;

    //Polling
    function successEvent($scope, data){
      $scope.conditions= data.result.conditions;
      $scope.conditionsEnabled = true
      $scope.expected = {byMonth: data.result.byMonth};
      $scope.expectedLoaded = true;
      $scope.risks = data.result.risks;
      $scope.risksLoaded = true;
    }

    function failureEvent($scope, data) {
      $scope.conditionsEnabled = true
      if (["Wind model training failed.", "There was an error storing wind data."].indexOf(data.result.status)){
        $location.path('/upload')
      } 
    }
    polling.loop(
      $scope,
      windday.checkStatus,
      $alert,
      ["Wind Day calculations ready."],
      ["Error Calculating Wind Days", "Empty project.", "Wind model training failed.", "There was an error storing wind data."],
      successEvent,
      failureEvent
      )

    //Seasonality
    windday.getSeasonality()
    .then(function(data){
      $scope.seasonality = data.result.seasonality;
      $scope.yearlyLoaded = true;
    })

    $scope.estimate = function(){
      $scope.expected = {};
      $scope.expectedLoaded = false;
      $scope.risks = [];
      $scope.risksLoaded = false;
      windday.calculateWindDayRisks( $scope.conditions ).then(function(){
        polling.loop(
          $scope,
          windday.checkStatus,
          $alert,
          ["Wind Day calculations ready.", "Wind model trained."],
          ["Error Calculating Wind Days", "Empty project.", "Wind model training failed.", "There was an error storing wind data."],
          successEvent,
          failureEvent
        );
      })
    };
    
    $scope.newWindFile = function(){
      $location.path('/upload');
    };
    
  });
