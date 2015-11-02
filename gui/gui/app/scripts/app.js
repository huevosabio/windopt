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
    'angularFileUpload',
    'leaflet-directive'
  ])
  .config(function ($routeProvider,$locationProvider) {
    $locationProvider.html5Mode(true).hashPrefix('!');
    $routeProvider
      .when('/upload', {
        templateUrl: 'views/upload.html',
        controller: 'UploadCtrl'
      })
      .when('/windday', {
        templateUrl: 'views/windday.html',
        controller: 'WinddayCtrl'
      })
      .when('/cranepath', {
        templateUrl: 'views/cranepath.html',
        controller: 'CranepathCtrl'
      })
      .when('/zipupload', {
        templateUrl: 'views/zipupload.html',
        controller: 'ZipuploadCtrl'
      })
      .when('/layerlist', {
        templateUrl: 'views/layerlist.html',
        controller: 'LayerlistCtrl'
      })
      .otherwise({
        redirectTo: '/windday'
      });
  });