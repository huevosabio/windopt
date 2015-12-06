'use strict';

/**
 * @ngdoc service
 * @name windopsApp.project
 * @description
 * # project
 * Factory in the windopsApp.
 * inspired from http://www.bennadel.com/blog/2612-using-the-http-service-in-angularjs-to-make-ajax-requests.htm
 */
angular.module('windopsApp')
  .factory('project', function ($http, $alert) {
    // Service logic
    // ...

    // Public API here
    return {
      createProject: createProject,
      listProjects: listProjects
    };

    // Gets creates project using a project name
    function createProject(name) {
      var request = $http({
        method: "post",
        url: "api/project",
        data: {
          name: name
        }
      });
      return (request.then( handleSuccess, handleError ));
    }

    function handleError( response ){
        if (
          ! angular.isObject( response.data ) ||
          ! response.data.message
          ) {
            $alert({
              content: 'There was an error logging in',
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
          return;
        } else{
          $alert({
              content: response.data.message,
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
          return;
        }
    }

    function handleSuccess( response ) {
      return ( response.data );
    }

    function listProjects() {
      var request = $http({
        method: "get",
        url: "api/project"
      });
      return (request.then (handleSuccess, handleError));
    }
    
  });
