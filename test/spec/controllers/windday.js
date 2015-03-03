'use strict';

describe('Controller: WinddayCtrl', function () {

  // load the controller's module
  beforeEach(module('windopsApp'));

  var WinddayCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    WinddayCtrl = $controller('WinddayCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
