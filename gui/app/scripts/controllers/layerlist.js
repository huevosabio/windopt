'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:LayerlistCtrl
 * @description
 * # LayerlistCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('LayerlistCtrl',  
    function(
      $scope, 
      $location, 
      $alert, 
      $http, 
      currentProject, 
      cost, 
      craneProject,
      polling
      ) {
    $scope.layersLoaded = false;
    $scope.layerdict= {};

    //load costs
    cost.listCosts().then( function(data){
        $scope.costs = data.costs;
      }).then(function(){
        //if the costs is empty, then redirect.
        if ($scope.costs.length < 1) {
          $alert({
              content: 'You need to create costs first; redirecting.',
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
          $location.path('/costs');
        }
        //console.log($scope.costs);
      });

    //Polling
    function successEvent($scope, data){
      $scope.layers = data.result.layers;
      for (var i = 0; i < data.result.layers.length; i++){
        $scope.layerdict[data.result.layers[i]] = {};
      }
      $scope.layersLoaded = true;
    }

    function failureEvent($scope, data) {
      return;
    }

    polling.loop(
      $scope,
      craneProject.checkStatus,
      $alert,
      ["Shapefiles stored. User needs to enter Interpretations"],
      [],
      successEvent,
      failureEvent
      )
    


    $scope.tsp = function(){
      $scope.layersLoaded = false;
      craneProject.calculateTSP({"layerdict": $scope.layerdict, "project": currentProject.project.name})
      .success(function(data,status,headers,config){
        $location.path('/cranepath');
      })
      .error(function(data,status,headers,config){
        console.log(data);
      });
    };
  });
