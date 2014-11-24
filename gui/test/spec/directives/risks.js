'use strict';

describe('Directive: risks', function () {

  // load the directive's module
  beforeEach(module('windopsApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<risks></risks>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the risks directive');
  }));
});
