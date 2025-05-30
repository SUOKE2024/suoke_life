export const PERMISSIONS = {
  ANDROID: {
    CAMERA: 'android.permission.CAMERA',
    RECORD_AUDIO: 'android.permission.RECORD_AUDIO',
    ACCESS_FINE_LOCATION: 'android.permission.ACCESS_FINE_LOCATION',
  },
  IOS: {
    CAMERA: 'ios.permission.CAMERA',
    MICROPHONE: 'ios.permission.MICROPHONE',
    LOCATION_WHEN_IN_USE: 'ios.permission.LOCATION_WHEN_IN_USE',
  },
};

export const RESULTS = {
  UNAVAILABLE: 'unavailable',
  DENIED: 'denied',
  LIMITED: 'limited',
  GRANTED: 'granted',
  BLOCKED: 'blocked',
};

export const check = jest.fn(() => Promise.resolve(RESULTS.GRANTED));
export const request = jest.fn(() => Promise.resolve(RESULTS.GRANTED));
export const requestMultiple = jest.fn(() => Promise.resolve({}));
export const checkMultiple = jest.fn(() => Promise.resolve({}));

export default {
  PERMISSIONS,
  RESULTS,
  check,
  request,
  requestMultiple,
  checkMultiple,
}; 