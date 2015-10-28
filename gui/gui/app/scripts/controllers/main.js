'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('MainCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
