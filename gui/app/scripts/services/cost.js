'use strict';

/**
 * @ngdoc service
 * @name windopsApp.costs
 * @description
 * # costs
 * Factory in the windopsApp.
 */
angular.module('windopsApp')
  .factory('costs', function ($http, $alert, currentProject) {
    // Service logic
    // ...

    // Public API here
    return {
      createCost: createCost,
      listCosts: listCosts
    };

    // Gets creates cost using a cost name
    function createCost(name) {
      var request = $http({
        method: "post",
        url: "api/costs",
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
              content: 'There was an error creating the cost.',
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

    // WindDay Functions
    
  });