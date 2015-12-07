'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('MainCtrl', function ($scope, $alert, project, currentProject) {
  	$scope.newProjectName = null;
  	$scope.selectedProject = null;

  	
  	$scope.listProjects = function () {
  		project.listProjects().then( function(data){
  			$scope.projects = data.projects;
  		}).then(function(){
  			console.log($scope.projects);
  		});
  	}

  	$scope.listProjects();

  	$scope.createProject = function () {
  		if ($scope.newProjectName === null) {
  			$alert({
              content: 'Please name the new project.',
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
            return;
  		}
  		project.createProject( $scope.newProjectName ).then( function(data) {
  			$scope.listProjects();
  			currentProject.project = data.project;
  			$scope.newProjectName = null;
  		});
  	}

  	$scope.openProject = function ( selectedProject) {
  		if (selectedProject === null ||
  			selectedProject.name === null ||
  			selectedProject.name === undefined) {
  			$alert({
              content: 'Please select or create a proejct.',
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
            return;
  		}
  		currentProject.project = selectedProject;
  	}
  });
