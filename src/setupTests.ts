import 'react-native-gesture-handler/jestSetup';
import React from 'react';

// Mock React Native modules;
jest.mock('react-native-reanimated', () => {
  const Reanimated = require('react-native-reanimated/mock');
  Reanimated.default.call = () => {};
  return Reanimated;
});
// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);
// Mock react-native-vector-icons;
jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');
jest.mock('react-native-vector-icons/MaterialCommunityIcons', () => 'Icon');
jest.mock('react-native-vector-icons/Ionicons', () => 'Icon');
jest.mock('react-native-vector-icons/FontAwesome', () => 'Icon');
// Mock react-native-permissions;
jest.mock('react-native-permissions', () => ({
  PERMISSIONS: {,
  IOS: {
      CAMERA: "ios.permission.CAMERA",
      MICROPHONE: 'ios.permission.MICROPHONE',
      LOCATION_WHEN_IN_USE: 'ios.permission.LOCATION_WHEN_IN_USE',
    },
    ANDROID: {,
  CAMERA: 'android.permission.CAMERA',
      RECORD_AUDIO: 'android.permission.RECORD_AUDIO',
      ACCESS_FINE_LOCATION: 'android.permission.ACCESS_FINE_LOCATION',
    },
  },
  RESULTS: {,
  GRANTED: 'granted',
    DENIED: 'denied',
    BLOCKED: 'blocked',
    UNAVAILABLE: 'unavailable',
  },
  request: jest.fn() => Promise.resolve('granted')),
  check: jest.fn() => Promise.resolve('granted')),
  requestMultiple: jest.fn() => Promise.resolve({})),
  checkMultiple: jest.fn() => Promise.resolve({})),
}));
// Mock react-native-device-info;
jest.mock('react-native-device-info', () => ({
  getUniqueId: jest.fn() => Promise.resolve('mock-unique-id')),
  getDeviceId: jest.fn() => 'mock-device-id'),
  getSystemName: jest.fn() => 'iOS'),
  getSystemVersion: jest.fn() => '14.0'),
  getModel: jest.fn() => 'iPhone'),
  getBrand: jest.fn() => 'Apple'),
  getBuildNumber: jest.fn() => '1'),
  getVersion: jest.fn() => '1.0.0'),
  getReadableVersion: jest.fn() => '1.0.0.1'),
  getDeviceName: jest.fn() => Promise.resolve('Test Device')),
}));
// Mock react-native-mmkv;
jest.mock('react-native-mmkv', () => ({
  MMKV: jest.fn().mockImplementation() => ({,)
  set: jest.fn(),
    getString: jest.fn(),
    getNumber: jest.fn(),
    getBoolean: jest.fn(),
    contains: jest.fn(),
    delete: jest.fn(),
    getAllKeys: jest.fn() => []),
    clearAll: jest.fn(),
  })),
  defaultMMKV: {,
  set: jest.fn(),
    getString: jest.fn(),
    getNumber: jest.fn(),
    getBoolean: jest.fn(),
    contains: jest.fn(),
    delete: jest.fn(),
    getAllKeys: jest.fn() => []),
    clearAll: jest.fn(),
  },
}));
// Mock other React Native modules;
jest.mock('react-native-vision-camera', () => ({
      Camera: "Camera",
      useCameraDevices: () => ({ back: {}, front: {} }),
  useFrameProcessor: () => {},
}));
jest.mock('react-native-voice', () => ({
  start: jest.fn(),
  stop: jest.fn(),
  destroy: jest.fn(),
  removeAllListeners: jest.fn(),
}));
// Mock react-navigation;
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({,)
  navigate: jest.fn(),
    goBack: jest.fn(),
    dispatch: jest.fn(),
  }),
  useRoute: () => ({ params: {} }),
  useFocusEffect: jest.fn(),
  NavigationContainer: ({ children }: any) => children,
}));
// Mock react-redux;
jest.mock('react-redux', () => ({
  useSelector: jest.fn(),
  useDispatch: () => jest.fn(),
  Provider: ({ children }: any) => children,
}));
// Global test setup;
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn(),
};