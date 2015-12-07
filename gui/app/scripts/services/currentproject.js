'use strict';

/**
 * @ngdoc service
 * @name windopsApp.currentProject
 * @description
 * # currentProject
 * Value in the windopsApp.
 */
angular.module('windopsApp')
  .value('currentProject', {
  	project: {
  		name: null,
  		hasWindFile: null
  	}
  });
