// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Seeded latency and failure schedule (DEC-004, proposed). Pure functions.
// Twin of src/scroll/schedule.py; the two must agree bit for bit
// (differential test tests/test_schedule_differential.py).
(function (root) {
  'use strict';

  var STREAMS = { read: 0, write: 1, decoy: 2 };
  var FIELD_DELAY = 0;
  var FIELD_OUTCOME = 1;
  var TWO_32 = 4294967296;

  function fmix32(h) {
    h = h >>> 0;
    h ^= h >>> 16;
    h = Math.imul(h, 0x85ebca6b);
    h ^= h >>> 13;
    h = Math.imul(h, 0xc2b2ae35);
    h ^= h >>> 16;
    return h >>> 0;
  }

  function isUint32(x) {
    return Number.isInteger(x) && x >= 0 && x < TWO_32;
  }

  function hash32(seed, stream, index, field) {
    if (!isUint32(seed)) throw new RangeError('seed must be an integer in [0, 2^32)');
    if (!isUint32(stream)) throw new RangeError('stream must be an integer in [0, 2^32)');
    if (!isUint32(index) || index >= TWO_32 - 1) throw new RangeError('index must be an integer in [0, 2^32 - 1)');
    if (!isUint32(field)) throw new RangeError('field must be an integer in [0, 2^32)');
    var h = fmix32(seed);
    h = fmix32((h ^ Math.imul(stream + 1, 0x9e3779b1)) >>> 0);
    h = fmix32((h ^ Math.imul(index + 1, 0x85ebca77)) >>> 0);
    h = fmix32((h ^ Math.imul(field + 1, 0xc2b2ae3d)) >>> 0);
    return h;
  }

  // Uniform in [0, 1).
  function uniform(seed, stream, index, field) {
    return hash32(seed, stream, index, field) / TWO_32;
  }

  function streamId(name) {
    if (!Object.prototype.hasOwnProperty.call(STREAMS, name)) throw new RangeError('unknown stream: ' + name);
    return STREAMS[name];
  }

  // Delay in integer milliseconds: floor(L * (1 + jitter * (2u - 1)) + 0.5).
  function delayMs(seed, stream, index, latencyMs, jitter) {
    if (typeof latencyMs !== 'number' || !isFinite(latencyMs) || latencyMs < 0) throw new RangeError('latencyMs must be a finite number >= 0');
    if (typeof jitter !== 'number' || !(jitter >= 0 && jitter < 1)) throw new RangeError('jitter must be in [0, 1)');
    var u = uniform(seed, streamId(stream), index, FIELD_DELAY);
    return Math.floor(latencyMs * (1 + jitter * (2 * u - 1)) + 0.5);
  }

  // true when the request succeeds. Failure iff u < p.
  function succeeds(seed, stream, index, failureProb) {
    if (typeof failureProb !== 'number' || !(failureProb >= 0 && failureProb <= 1)) throw new RangeError('failureProb must be in [0, 1]');
    var u = uniform(seed, streamId(stream), index, FIELD_OUTCOME);
    return !(u < failureProb);
  }

  function schedule(seed, stream, index, latencyMs, jitter, failureProb) {
    return {
      delayMs: delayMs(seed, stream, index, latencyMs, jitter),
      ok: succeeds(seed, stream, index, failureProb)
    };
  }

  var api = {
    STREAMS: STREAMS, fmix32: fmix32, hash32: hash32, uniform: uniform,
    delayMs: delayMs, succeeds: succeeds, schedule: schedule
  };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; } else { root.ScrollSchedule = api; }
})(typeof self !== 'undefined' ? self : this);
