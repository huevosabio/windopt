'use strict';

describe('Controller: LayerlistCtrl', function () {

  // load the controller's module
  beforeEach(module('windopsApp'));

  var LayerlistCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    LayerlistCtrl = $controller('LayerlistCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
