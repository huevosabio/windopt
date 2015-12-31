'use strict';

describe('Controller: CostsCtrl', function () {

  // load the controller's module
  beforeEach(module('windopsApp'));

  var CostsCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    CostsCtrl = $controller('CostsCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(CostsCtrl.awesomeThings.length).toBe(3);
  });
});
