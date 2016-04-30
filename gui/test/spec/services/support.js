'use strict';

describe('Service: support', function () {

  // load the service's module
  beforeEach(module('windopsApp'));

  // instantiate service
  var support;
  beforeEach(inject(function (_support_) {
    support = _support_;
  }));

  it('should do something', function () {
    expect(!!support).toBe(true);
  });

});
