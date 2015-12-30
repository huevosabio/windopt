'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:CostsCtrl
 * @description
 * # CostsCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('CostsCtrl', function ($scope, $alert, cost) {
  	$scope.newCostName = null;

  	
  	$scope.listCosts = function () {
  		cost.listCosts().then( function(data){
  			$scope.costs = data.costs;
  		}).then(function(){
  			//console.log($scope.costs);
  		});
  	}

  	$scope.listCosts();

  	$scope.createCost = function () {
  		if ($scope.newCostName === null) {
  			$alert({
              content: 'Please name the new cost.',
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
            return;
  		}
  		cost.createCost( $scope.newCostName ).then( function(data) {
  			$scope.listCosts();
  			$scope.newCostName = null;
  		});
  	}

  });
