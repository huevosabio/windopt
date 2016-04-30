'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('DashboardCtrl',  function($scope, $cookieStore, $auth, $alert, $location, currentProject, support) {

    /**
     * Sidebar Toggle & Cookie Control
     *
     */
     $scope.currentProject = currentProject;

     function getWindRoute(){
       return currentProject.project.hasWindFile ? "/#/windday" : "/#/upload"
     }

     $scope.email = '';
     $scope.link = '';

     $scope.supportLoaded = false;
     $scope.supportInfo = support.getSupportInfo();

     function getCraneRoute (){
       var cranepathStatuses = [
         "Optimization problem queued",
         "Setting layer interpretations.",
         "Layer Interpretations set",
         "Creating the cost raster.",
         "Building the complete graph.",
         "Solving the Traveling Salesman Problem",
         "Getting detailed path costs.",
         "Solved."
       ];
       var layerlistStatuses = [
         "Shapefiles stored. User needs to enter Interpretations",
         "Reading shapefiles.",
         "Project zip file stored, queueing for unpacking layers",
         "Error computing TSP"
       ];
       var zipuploadStatuses = [
         "Error storing zip file."
       ]
       var route =
       cranepathStatuses.indexOf(currentProject.project['crane status']) > -1 ? '/#/cranepath' :
       layerlistStatuses.indexOf(currentProject.project['crane status']) > -1 ? '/#/layerlist' :
       '/#/zipupload';
       return route;
     }
     $scope.windRoute = getWindRoute();
     $scope.craneRoute = getCraneRoute();

     $scope.$watch('currentProject.project',  function(){
       $scope.windRoute = getWindRoute();
       $scope.craneRoute = getCraneRoute();
     }, true);

     //hides menu items if there's no user authenticated
     $scope.isAuthenticated = function() {
        return $auth.isAuthenticated();
    };

    $scope.isOpenProject = function(){
        if (currentProject.project.name === null) {
            return false;
        } else {
            return true;
        }
    }

    $scope.getProjectName = function(){
        return currentProject.project['name'];
    }

    var mobileView = 992;

    $scope.getWidth = function() { return window.innerWidth; };

    $scope.$watch($scope.getWidth, function(newValue)//, oldValue)
    {
        if(newValue >= mobileView)
        {
            if(angular.isDefined($cookieStore.get('toggle')))
            {
                if($cookieStore.get('toggle') === false)
                {
                    $scope.toggle = false;
                }
                else
                {
                    $scope.toggle = true;
                }
            }
            else
            {
                $scope.toggle = true;
            }
        }
        else
        {
            $scope.toggle = false;
        }

    });

    $scope.toggleSidebar = function()
    {
        $scope.toggle = ! $scope.toggle;

        $cookieStore.put('toggle', $scope.toggle);
    };

    window.onresize = function() { $scope.$apply(); };

    $scope.logout = function(){
        $auth.logout()
        .then(function() {
            $location.path('/login');
            $alert({
                content: 'You have been logged out',
                animation: 'fadeZoomFadeDown',
                type: 'info',
                duration: 3,
                placement:'top-right'
            });
        });
    }
});
