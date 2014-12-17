'use strict';

describe('Controller: ZipuploadCtrl', function () {

  // load the controller's module
  beforeEach(module('windopsApp'));

  var ZipuploadCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    ZipuploadCtrl = $controller('ZipuploadCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
