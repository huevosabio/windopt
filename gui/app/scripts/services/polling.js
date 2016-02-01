'use strict';

/**
 * @ngdoc service
 * @name windopsApp.polling
 * @description
 * # polling
 * Factory in the windopsApp.
 */
angular.module('windopsApp')
  .factory('polling', function ($http, $alert, currentProject) {
    // Service logic
    // ...

    // Public API here
    return {
      isStatusReady: isStatusReady,
      loop: loop,
    };

    function isStatusReady($scope, statusCheck,callback){
      statusCheck()
        .then(function(data) {
        console.log(data);
        $scope.status = data.result.status;
        callback($scope, data);
      });

    };

  function loop($scope, statusCheck, $alert, requiredStatus, failureStatus, successEvent, failureEvent){
    isStatusReady($scope, statusCheck, function($scope, data){
      if (requiredStatus.indexOf($scope.status) >= 0){
        successEvent($scope, data);
        return;

      } else if (failureStatus.indexOf($scope.status) >= 0){
        $alert({
              content: $scope.status,
              animation: 'fadeZoomFadeDown',
              type: 'danger',
              duration: 3,
              placement:'top-right'
            });
        failureEvent($scope, data);
        return;

      } else {
        $alert({
              content: $scope.status,
              animation: 'fadeZoomFadeDown',
              type: 'info',
              duration: 3,
              placement:'top-right'
            });
        setTimeout(function(){
          loop($scope, statusCheck, $alert, requiredStatus, failureStatus, successEvent, failureEvent);
        },4000);
      };
    });
  }
});
