'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('AboutCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
