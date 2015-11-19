'use strict';

describe('Directive: passwordStrength', function () {

  // load the directive's module
  beforeEach(module('windopsApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<password-strength></password-strength>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the passwordStrength directive');
  }));
});
