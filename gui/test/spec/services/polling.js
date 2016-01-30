'use strict';

describe('Service: polling', function () {

  // load the service's module
  beforeEach(module('windopsApp'));

  // instantiate service
  var polling;
  beforeEach(inject(function (_polling_) {
    polling = _polling_;
  }));

  it('should do something', function () {
    expect(!!polling).toBe(true);
  });

});
