'use strict';

/**
 * @ngdoc directive
 * @name windopsApp.directive:loading
 * @description
 * # loading
 */
angular.module('windopsApp')
  .directive('loading', function () {
    return {
        restrict: 'AE',
        replace: 'false',
        template: '<div class="loading absolute-center"><div class="double-bounce1"></div><div class="double-bounce2"></div></div>'
    };
  });
