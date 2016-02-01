'use strict';

/**
 * @ngdoc service
 * @name windopsApp.windday
 * @description
 * # windday
 * Factory in the windopsApp.
 */
angular.module('windopsApp')
  .factory('windday', function ($http, $alert, currentProject) {
    // Service logic
    // ...

    // Public API here
    return {
      checkStatus: checkStatus,
      getSeasonality: getSeasonality,
      calculateWindDayRisks: calculateWindDayRisks
    };

    // Checks status of wind day calculations, and if ready returns risks and winddays
    function checkStatus() {
      var request = $http({
        method: "get",
        url: "api/windyday/" + currentProject.project.name + "/status"
      });
      return (request.then( handleSuccess, handleError ));
    }

    // gets wind seasonality data
    function getSeasonality() {
      var request = $http({
        method: "get",
        url: "api/windday/" + currentProject.project.name + "/seasonality"
      });
      return (request.then( handleSuccess, handleError ));
    }

    // Gets creates cost using a cost name
    function calculateWindDayRisks( data ) {
      var request = $http({
        method: "post",
        url: "/api/windday/" + currentProject.project.name + "/calculate",
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
