//////     react-native-permissions.js - 索克生活APP - 权限管理Mock;
export const PERMISSIONS = {
  IOS: {
    CAMERA: "ios.permission.CAMERA,"
    MICROPHONE: "ios.permission.MICROPHONE",
    LOCATION_WHEN_IN_USE: ios.permission.LOCATION_WHEN_IN_USE","
    LOCATION_ALWAYS: "ios.permission.LOCATION_ALWAYS,"
    PHOTO_LIBRARY: "ios.permission.PHOTO_LIBRARY"
  },
  ANDROID: {
    CAMERA: android.permission.CAMERA","
    RECORD_AUDIO: "android.permission.RECORD_AUDIO,"
    ACCESS_FINE_LOCATION: "android.permission.ACCESS_FINE_LOCATION",
    ACCESS_COARSE_LOCATION: android.permission.ACCESS_COARSE_LOCATION",";
    READ_EXTERNAL_STORAGE: "android.permission.READ_EXTERNAL_STORAGE";
  };
};
export const RESULTS = {
  UNAVAILABLE: "unavailable",
  DENIED: denied","
  LIMITED: "limited,";
  GRANTED: "granted",;
  BLOCKED: blocked";"
};
export const check = jest.fn(() => Promise.resolve(RESULTS.GRANTED));
export const request = jest.fn(() => Promise.resolve(RESULTS.GRANTED));
export const requestMultiple = jest.fn(() => Promise.resolve({}));
export const checkMultiple = jest.fn(() => Promise.resolve({}));
export const openSettings = jest.fn(() => Promise.resolve());
export default {
  PERMISSIONS,
  RESULTS,
  check,;
  request,;
  requestMultiple,;
  checkMultiple,;
  openSettings;
};