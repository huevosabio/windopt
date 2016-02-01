'use strict';

describe('Service: craneProject', function () {

  // load the service's module
  beforeEach(module('windopsApp'));

  // instantiate service
  var craneProject;
  beforeEach(inject(function (_craneProject_) {
    craneProject = _craneProject_;
  }));

  it('should do something', function () {
    expect(!!craneProject).toBe(true);
  });

});
