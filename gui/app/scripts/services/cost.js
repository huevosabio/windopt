'use strict';

/**
 * @ngdoc service
 * @name windopsApp.costs
 * @description
 * # costs
 * Factory in the windopsApp.
 */
angular.module('windopsApp')
  .factory('cost', function ($http, $alert, currentProject) {
    // Service logic
    // ...

    // Public API here
    return {
      createCost: createCost,
      listCosts: listCosts,
      updateCost: updateCost,
      deleteCost: deleteCost
    };

    // Gets creates cost using a cost name
    function createCost( data ) {
      var request = $http({
        method: "post",
        url: "api/costs",
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

    function listCosts() {
      var request = $http({
        method: "get",
        url: "api/costs"
      });
      return (request.then (handleSuccess, handleError));
    }

    function deleteCost ( data ) {
      var request = $http({
        method: "delete",
        url: "api/costs/" + data.id,
        data: data
      });
      return (request.then( handleSuccess, handleError ));
    }

    function updateCost ( data ) {
      var request = $http({
        method: "put",
        url: "api/costs/" + data.id,
        data: data
      });
      return (request.then( handleSuccess, handleError ));
    }

    // WindDay Functions
    
  });