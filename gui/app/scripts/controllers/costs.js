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
  	$scope.interpretations = ['turbines', 'boundary', 'crossing'];
  	$scope.fields = ['name', 'interpretation', 'cost'];
  	
  	$scope.listCosts = function () {
  		cost.listCosts().then( function(data){
  			$scope.costs = data.costs;
  		}).then(function(){
  			//console.log($scope.costs);
  		});
  	}

  	$scope.listCosts();

  	$scope.saveCost = function (data) {
  		if (data.name === null) {
  			$alert({
              content: 'Costs must be uniquely named.',
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
            return;
  		}
  		if (data.id === null){
  			cost.createCost(data).then( function() {
  				$scope.listCosts();
  			});
  		} else {
  			cost.updateCost(data).then( function() {
  				$scope.listCosts();
  			})
  		}
  	}

  	$scope.addCost = function() {
  		$scope.inserted = {
  			name: null,
  			interpretation: null,
  			cost: null,
  			id: null
  		};
  		$scope.costs.push($scope.inserted);
  	}

  	$scope.deleteCost = function( data ) {
  		cost.deleteCost(data).then(function(){
  			$scope.listCosts();
  		});
  	}

  });
