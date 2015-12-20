'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('DashboardCtrl',  function($scope, $cookieStore, $auth, $alert, $location, currentProject) {

    /**
     * Sidebar Toggle & Cookie Control
     *
     */

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

    $scope.getWindRoute = function(){
        return currentProject.project.hasWindFile ? "/#/windday" : "/#/upload"
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
