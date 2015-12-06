'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('MainCtrl', function ($scope, project) {
  	project.listProjects().then( function(data){
  		$scope.projects = data.projects;
  	}).then(function(){
  		console.log($scope.projects);
  	})
  });
