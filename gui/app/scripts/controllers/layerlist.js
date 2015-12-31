'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:LayerlistCtrl
 * @description
 * # LayerlistCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('LayerlistCtrl',  function($scope, $location,$http, currentProject, cost) {
    $scope.layersLoaded = false;

    //load costs
    cost.listCosts().then( function(data){
        $scope.costs = data.costs;
      }).then(function(){
        //console.log($scope.costs);
      });

    $http.get('/api/cranepath/layerlist')
    .success(function(data, status, headers, config) {
      console.log(data);
      $scope.layerdict= {};
      $scope.layers = data.layers;
      for (var i = 0; i < data.layers.length; i++){
        $scope.layerdict[data.layers[i]] = {};
      }
      $scope.layersLoaded = true;
    })
    .error(function(data, status, headers, config) {
      console.log(data);
    });
    
    $scope.tsp = function(){
      $scope.layersLoaded = false;
      $http.post('/api/cranepath/tsp',{"layerdict": $scope.layerdict, "project": currentProject.project.name})
      .success(function(data,status,headers,config){
        $location.path('/cranepath');
      })
      .error(function(data,status,headers,config){
        console.log(data);
      });
    };
  });
