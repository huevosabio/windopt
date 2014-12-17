'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:LayerlistCtrl
 * @description
 * # LayerlistCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('LayerlistCtrl',  function($scope, $location,$http) {
    $http.get('/api/cranepath/layerlist')
    .success(function(data, status, headers, config) {
      console.log(data);
      $scope.layerdict= {};
      $scope.layers = data.layers;
      for (var i = 0; i < data.layers.length; i++){
        $scope.layerdict[data.layers[i]] = {};
      }
      
    })
    .error(function(data, status, headers, config) {
      console.log(data);
    });
    
    $scope.tsp = function(){
      $http.post('/api/cranepath/tsp',$scope.layerdict)
      .success(function(data,status,headers,config){
        $location.path('/cranepath');
      })
      .error(function(data,status,headers,config){
        console.log(data);
      });
    };
  });
