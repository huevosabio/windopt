'use strict';

describe('Service: costs', function () {

  // load the service's module
  beforeEach(module('windopsApp'));

  // instantiate service
  var costs;
  beforeEach(inject(function (_costs_) {
    costs = _costs_;
  }));

  it('should do something', function () {
    expect(!!costs).toBe(true);
  });

});
