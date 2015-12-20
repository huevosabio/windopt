'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:LayerlistCtrl
 * @description
 * # LayerlistCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('LayerlistCtrl',  function($scope, $location,$http, currentProject) {
    $scope.layersLoaded = false;
    $http.get('/api/cranepath/layerlist')
    .success(function(data, status, headers, config) {
      console.log(data);
      $scope.layerdict= {};
      $scope.layers = data.layers;
      for (var i = 0; i < data.layers.length; i++){
        $scope.layerdict[data.layers[i]] = {};
        $scope.layerdict[data.layers[i]].interpretation = 'turbines';
        $scope.layerdict[data.layers[i]].cost = 0.0;
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
