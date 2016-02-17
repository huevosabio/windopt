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
  	$scope.selectedProject = null;
    $scope.fields = ['name', 'wind status', 'crane status']
    $scope.projects = [];

  	$scope.listProjects = function () {
  		project.listProjects().then( function(data){
  			$scope.projects = data.projects;
  		}).then(function(){
  			//console.log($scope.projects);
  		});
  	}

  	$scope.listProjects();

  	$scope.saveProject = function (data) {
  		if (data.name === null) {
  			$alert({
              content: 'Please name the new project.',
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
            return;
  		}
  		project.createProject( data.name ).then( function(data) {
  			$scope.listProjects();
  			currentProject.project = data.project;
  		});
  	}

    $scope.deleteProject = function(data){
      project.deleteProject(data.name);
      $scope.listProjects();
    };

    $scope.addProject = function() {
  		$scope.inserted = {
  			name: null,
  			interpretation: null,
  			cost: null,
  			id: null
  		};
  		$scope.projects.push($scope.inserted);
  	}


  	$scope.openProject = function ( data ) {
  		if (data === null ||
  			data.name === null ||
  			data.name === undefined) {
  			$alert({
              content: 'Please select or create a proejct.',
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
            return;
  		}
  		currentProject.project = data;
  	}
  });
