'use strict';

describe('Controller: ExpectedWindDaysCtrl', function () {

  // load the controller's module
  beforeEach(module('windopsApp'));

  var ExpectedWindDaysCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    ExpectedWindDaysCtrl = $controller('ExpectedWindDaysCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
