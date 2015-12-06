'use strict';

describe('Service: currentProject', function () {

  // load the service's module
  beforeEach(module('windopsApp'));

  // instantiate service
  var currentProject;
  beforeEach(inject(function (_currentProject_) {
    currentProject = _currentProject_;
  }));

  it('should do something', function () {
    expect(!!currentProject).toBe(true);
  });

});
