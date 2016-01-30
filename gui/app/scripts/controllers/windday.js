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
    

    //Status
    windday.getSeasonality()
    .then(function(data){
      $scope.seasonality = result.seasonality;
      $scope.yearlyLoaded = true;
    })


    //Polling
    function successEvent($scope, data){
      $scope.conditions: data.result.conditions;
      $scope.conditionsEnabled = true
      $scope.expected = {byMonth: data.result.byMonth};
      $scope.expectedLoaded = true;
      $scope.risks = data.result.risks;
      $scope.risksLoaded = true;
    }

    function failureEvent($scope, $location) {
      $scope.conditionsEnabled = true
      if (["Wind model training failed.", "There was an error storing wind data."].indexOf(data.result.status)){
        $location.path('/upload')
      } 
    }
    polling.loop(
      $scope,
      windday.checkStatus,
      $alert,
      ["Wind Day calculations ready.", "Wind model trained."],
      ["Error Calculating Wind Days", "Empty project.", "Wind model training failed.", "There was an error storing wind data."],
      successEvent,
      failureEvent
      )

    $scope.estimate = function(){
      $scope.expectedLoaded = false;
      $scope.risksLoaded = false;
      windday.calculateWindDayRisks( data ).then(function(){
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
