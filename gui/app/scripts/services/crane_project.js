'use strict';

/**
 * @ngdoc service
 * @name windopsApp.craneProject
 * @description
 * # craneProject
 * Factory in the windopsApp.
 */
angular.module('windopsApp')
  .factory('craneProject', function ($http, $alert, currentProject) {
    // Service logic
    // ...

    // Public API here
    return {
      checkStatus: checkStatus,
      calculateTSP: calculateTSP
    };

    // Checks status of wind day calculations, and if ready returns risks and winddays
    function checkStatus() {
      var request = $http({
        method: "get",
        url: "/api/cranepath/" + currentProject.project.name + "/status"
      });
      return (request.then( handleSuccess, handleError ));
    }

    // Gets creates cost using a cost name
    function calculateTSP( data ) {
      var request = $http({
        method: "post",
        url: "/api/cranepath/" + currentProject.project.name + "/tsp",
        data: data
      });
      return (request.then( handleSuccess, handleError ));
    }


    function handleError( response ){
        if (
          ! angular.isObject( response.data ) ||
          ! response.data.message
          ) {
            $alert({
              content: 'There was an error on the server side.',
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
    
  });