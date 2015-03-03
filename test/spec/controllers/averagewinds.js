'use strict';

describe('Controller: AveragewindsCtrl', function () {

  // load the controller's module
  beforeEach(module('windopsApp'));

  var AveragewindsCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    AveragewindsCtrl = $controller('AveragewindsCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
