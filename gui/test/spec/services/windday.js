'use strict';

describe('Service: windday', function () {

  // load the service's module
  beforeEach(module('windopsApp'));

  // instantiate service
  var windday;
  beforeEach(inject(function (_windday_) {
    windday = _windday_;
  }));

  it('should do something', function () {
    expect(!!windday).toBe(true);
  });

});
