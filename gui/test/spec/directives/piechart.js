'use strict';

describe('Directive: piechart', function () {

  // load the directive's module
  beforeEach(module('windopsApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<piechart></piechart>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the piechart directive');
  }));
});
