'use strict';

/**
 * @ngdoc service
 * @name windopsApp.support
 * @description
 * # support
 * Factory in the windopsApp.
 */
angular.module('windopsApp')
  .factory('support',  function ($http, $alert) {
    // Service logic
    // ...

    // Public API here
    return {
      getSupportInfo: getSupportInfo
    };

    // Gets creates cost using a cost name
    function getSupportInfo() {
      var request = $http({
        method: "get",
        url: "api/info"
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
