const PERMISSIONS = {
  ANDROID: {
    CAMERA: 'android.permission.CAMERA',
    RECORD_AUDIO: 'android.permission.RECORD_AUDIO',
    READ_EXTERNAL_STORAGE: 'android.permission.READ_EXTERNAL_STORAGE',
    WRITE_EXTERNAL_STORAGE: 'android.permission.WRITE_EXTERNAL_STORAGE',
  },
  IOS: {
    CAMERA: 'ios.permission.CAMERA',
    MICROPHONE: 'ios.permission.MICROPHONE',
    PHOTO_LIBRARY: 'ios.permission.PHOTO_LIBRARY',
  },
};

const RESULTS = {
  UNAVAILABLE: 'unavailable',
  DENIED: 'denied',
  LIMITED: 'limited',
  GRANTED: 'granted',
  BLOCKED: 'blocked',
};

const check = jest.fn(() => Promise.resolve(RESULTS.GRANTED));
const request = jest.fn(() => Promise.resolve(RESULTS.GRANTED));
const checkMultiple = jest.fn(() => Promise.resolve({}));
const requestMultiple = jest.fn(() => Promise.resolve({}));
const openSettings = jest.fn(() => Promise.resolve());
const checkNotifications = jest.fn(() =>
  Promise.resolve({
    status: RESULTS.GRANTED,
    settings: {},
  })
);
const requestNotifications = jest.fn(() =>
  Promise.resolve({
    status: RESULTS.GRANTED,
    settings: {},
  })
);

module.exports = {
  PERMISSIONS,
  RESULTS,
  check,
  request,
  checkMultiple,
  requestMultiple,
  openSettings,
  checkNotifications,
  requestNotifications,
};
