'use strict';

/**
 * @ngdoc overview
 * @name windopsApp
 * @description
 * # windopsApp
 *
 * Main module of the application.
 */
angular
  .module('windopsApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'ui.bootstrap',
    'angularFileUpload'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/upload', {
        templateUrl: 'views/upload.html',
        controller: 'UploadCtrl'
      })
      .when('/windday', {
        templateUrl: 'views/windday.html',
        controller: 'WinddayCtrl'
      })
      .otherwise({
        redirectTo: '/windday'
      });
  });
