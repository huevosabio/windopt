'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:LoginCtrl
 * @description
 * # LoginCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('LoginCtrl', function($scope, $location, $alert, $auth) {
    if ($auth.isAuthenticated()) {
        $auth.logout()
        .then(function() {
            $alert({
                content: 'You have been logged out',
                animation: 'fadeZoomFadeDown',
                type: 'info',
                duration: 3,
                placement:'top-right'
            });
        });
    }
    
    $scope.logMeIn = function() {
      $alert({
        content: 'Checking your credentials, please wait.',
        animation: 'fadeZoomFadeDown',
        type: 'info',
        duration: 3,
        placement:'top-right'
      })
      $auth.login({ username: $scope.username, password: $scope.password })
        .then(function() {
          $alert({
            content: 'You have successfully logged in',
            animation: 'fadeZoomFadeDown',
            type: 'success',
            duration: 3,
            placement:'top-right'
          });
          $location.path('/');
        })
        .catch(function(response) {
          $alert({
            content: 'There was an error logging in',
            animation: 'fadeZoomFadeDown',
            type: 'danger',
            duration: 3,
            placement:'top-right'
          });
        });
    };
    $scope.authenticate = function(provider) {
      $auth.authenticate(provider)
        .then(function() {
          $alert({
            content: 'You have successfully logged in',
            animation: 'fadeZoomFadeDown',
            type: 'success',
            duration: 3,
            placement:'top-right'
          });
          $location.path('/');
        })
        .catch(function(response) {
          $alert({
            content: 'There was an error logging in.',
            animation: 'fadeZoomFadeDown',
            type: 'danger',
            duration: 3,
            placement:'top-right'
          });
        });
    };
  });