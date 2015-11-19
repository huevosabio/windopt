'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:SignupCtrl
 * @description
 * # SignupCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('SignupCtrl', function($scope, $location, $auth, $alert) {
    $scope.signMeUp = function() {
      $auth.signup($scope.user)
        .then(function(response) {
          $auth.setToken(response);
          $alert({
                content: 'You have successfully created a new account and have been signed-in',
                animation: 'fadeZoomFadeDown',
                type: 'info',
                duration: 3,
                placement:'top-right'
            });
          $location.path('/');
        })
        .catch(function(response) {
          $alert({
            content: 'Error signing up:' + response.data.message,
            animation: 'fadeZoomFadeDown',
            type: 'danger',
            duration: 3,
            placement:'top-right'
          });
          toastr.error(response.data.message);
        });
    };
  });