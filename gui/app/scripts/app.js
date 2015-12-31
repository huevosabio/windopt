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
    'leaflet-directive',
    'satellizer',
    'mgcrea.ngStrap',
    'xeditable'
  ])
  .config(function ($routeProvider, $locationProvider, $authProvider) {
    

    function authenticated($q, $location, $auth) {
      var deferred = $q.defer();
      if (!$auth.isAuthenticated()) {
        $location.path('/login');
      } else {
        deferred.resolve();
      }
      return deferred.promise;
    }

    $routeProvider
      .when('/main', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl',
        resolve: {
          authenticated: authenticated
        }
      })
      .when('/upload', {
        templateUrl: 'views/upload.html',
        controller: 'UploadCtrl',
        resolve: {
          authenticated: authenticated
        }
      })
      .when('/windday', {
        templateUrl: 'views/windday.html',
        controller: 'WinddayCtrl',
        resolve: {
          authenticated: authenticated
        }
      })
      .when('/cranepath', {
        templateUrl: 'views/cranepath.html',
        controller: 'CranepathCtrl',
        resolve: {
          authenticated: authenticated
        }
      })
      .when('/zipupload', {
        templateUrl: 'views/zipupload.html',
        controller: 'ZipuploadCtrl',
        resolve: {
          authenticated: authenticated
        }
      })
      .when('/layerlist', {
        templateUrl: 'views/layerlist.html',
        controller: 'LayerlistCtrl',
        resolve: {
          authenticated: authenticated
        }
      })
      .when('/login', {
        templateUrl: 'views/login.html',
        controller: 'LoginCtrl',
        controllerAs: 'login'
      })
      .when('/signup', {
        templateUrl: 'views/signup.html',
        controller: 'SignupCtrl',
        controllerAs: 'signup'
      })
      .when('/projects', {
        templateUrl: 'views/projects.html',
        controller: 'ProjectsCtrl',
        controllerAs: 'projects'
      })
      .when('/costs', {
        templateUrl: 'views/costs.html',
        controller: 'CostsCtrl',
        controllerAs: 'costs',
        resolve: {
          authenticated: authenticated
        }
      })
      .otherwise({
        redirectTo: '/main'
      });


    $authProvider.httpInterceptor = true; // Add Authorization header to HTTP request
    $authProvider.loginOnSignup = true;
    $authProvider.baseUrl = '/'; // API Base URL for the paths below.
    $authProvider.loginRedirect = '/main';
    $authProvider.logoutRedirect = '/login';
    $authProvider.signupRedirect = '/main';
    $authProvider.loginUrl = '/api/auth/login';
    $authProvider.signupUrl = '/api/users';
    $authProvider.loginRoute = '/login';
    $authProvider.signupRoute = '/create';
    $authProvider.tokenRoot = false; // set the token parent element if the token is not the JSON root
    $authProvider.tokenName = 'token';
    $authProvider.tokenPrefix = 'windops'; // Local Storage name prefix
    $authProvider.unlinkUrl = '/auth/unlink/';
    $authProvider.unlinkMethod = 'get';
    $authProvider.authHeader = 'Authorization';
    $authProvider.authToken = 'Bearer';
    $authProvider.withCredentials = true;
    $authProvider.platform = 'browser'; // or 'mobile'
    $authProvider.storage = 'localStorage'; // or 'sessionStorage' 
  });