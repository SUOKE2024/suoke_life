import "react-native-gesture-handler/jestSetup";
import mockAsyncStorage from "@react-native-async-storage/async-storage/jest/async-storage-mock";


// Jest测试环境设置

// 声明全局类型
declare const global: any;

// Mock AsyncStorage
jest.mock("@react-native-async-storage/async-storage", () => mockAsyncStorage);

// Mock React Native modules
jest.mock("react-native", () => {
  const RN = jest.requireActual("react-native-web");

  return {
    ...RN,
    Platform: {
      OS: "ios",
      select: jest.fn((obj) => obj.ios || obj.default),
    },
    Dimensions: {
      get: jest.fn(() => ({ width: 375, height: 812 })),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    },
    Alert: {
      alert: jest.fn(),
    },
    Linking: {
      openURL: jest.fn(),
      canOpenURL: jest.fn(() => Promise.resolve(true)),
    },
    StatusBar: {
      setBarStyle: jest.fn(),
      setBackgroundColor: jest.fn(),
    },
    PermissionsAndroid: {
      request: jest.fn(() => Promise.resolve("granted")),
      check: jest.fn(() => Promise.resolve(true)),
      PERMISSIONS: {},
      RESULTS: {
        GRANTED: "granted",
        DENIED: "denied",
      },
    },
  };
});

// Mock React Navigation
jest.mock("@react-navigation/native", () => ({
  ...jest.requireActual("@react-navigation/native"),
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
    dispatch: jest.fn(),
    setOptions: jest.fn(),
    isFocused: jest.fn(() => true),
    addListener: jest.fn(),
    removeListener: jest.fn(),
  }),
  useRoute: () => ({
    params: {},
    name: "TestScreen",
    key: "test-key",
  }),
  useFocusEffect: jest.fn(),
  NavigationContainer: ({ children }: any) => children,
}));

// Mock Redux
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useSelector: jest.fn(),
  useDispatch: () => jest.fn(),
}));

// Mock MMKV
jest.mock("react-native-mmkv", () => ({
  MMKV: jest.fn().mockImplementation(() => ({
    set: jest.fn(),
    getString: jest.fn(),
    getNumber: jest.fn(),
    getBoolean: jest.fn(),
    delete: jest.fn(),
    clearAll: jest.fn(),
    getAllKeys: jest.fn(() => []),
  })),
}));

// Mock Vector Icons
jest.mock("react-native-vector-icons/MaterialIcons", () => "MaterialIcons");
jest.mock("react-native-vector-icons/Ionicons", () => "Ionicons");
jest.mock("react-native-vector-icons/FontAwesome", () => "FontAwesome");

// Mock Device Info
jest.mock("react-native-device-info", () => ({
  getVersion: jest.fn(() => "1.0.0"),
  getBuildNumber: jest.fn(() => "1"),
  getSystemVersion: jest.fn(() => "14.0"),
  getModel: jest.fn(() => "iPhone"),
  getBrand: jest.fn(() => "Apple"),
  getDeviceId: jest.fn(() => "test-device-id"),
  getUniqueId: jest.fn(() => Promise.resolve("test-unique-id")),
  isEmulator: jest.fn(() => Promise.resolve(false)),
}));

// Mock Permissions
jest.mock("react-native-permissions", () => ({
  check: jest.fn(() => Promise.resolve("granted")),
  request: jest.fn(() => Promise.resolve("granted")),
  openSettings: jest.fn(() => Promise.resolve()),
  PERMISSIONS: {
    IOS: {
      CAMERA: "ios.permission.CAMERA",
      MICROPHONE: "ios.permission.MICROPHONE",
      LOCATION_WHEN_IN_USE: "ios.permission.LOCATION_WHEN_IN_USE",
    },
    ANDROID: {
      CAMERA: "android.permission.CAMERA",
      RECORD_AUDIO: "android.permission.RECORD_AUDIO",
      ACCESS_FINE_LOCATION: "android.permission.ACCESS_FINE_LOCATION",
    },
  },
  RESULTS: {
    GRANTED: "granted",
    DENIED: "denied",
    BLOCKED: "blocked",
    UNAVAILABLE: "unavailable",
  },
}));

// Mock Vision Camera
jest.mock("react-native-vision-camera", () => ({
  Camera: "Camera",
  useCameraDevices: jest.fn(() => ({
    back: { id: "back" },
    front: { id: "front" },
  })),
  useCameraFormat: jest.fn(),
  useFrameProcessor: jest.fn(),
}));

// Mock Voice
jest.mock("react-native-voice", () => ({
  start: jest.fn(() => Promise.resolve()),
  stop: jest.fn(() => Promise.resolve()),
  destroy: jest.fn(() => Promise.resolve()),
  removeAllListeners: jest.fn(),
  isAvailable: jest.fn(() => Promise.resolve(true)),
  onSpeechStart: jest.fn(),
  onSpeechEnd: jest.fn(),
  onSpeechResults: jest.fn(),
  onSpeechError: jest.fn(),
}));

// Mock NetInfo
jest.mock("@react-native-community/netinfo", () => ({
  fetch: jest.fn(() =>
    Promise.resolve({
      isConnected: true,
      type: "wifi",
      isInternetReachable: true,
    })
  ),
  addEventListener: jest.fn(() => jest.fn()),
}));

// Mock Geolocation
jest.mock("@react-native-community/geolocation", () => ({
  getCurrentPosition: jest.fn((success) => {
    success({
      coords: {
        latitude: 37.7749,
        longitude: -122.4194,
        accuracy: 5,
      },
    });
  }),
  watchPosition: jest.fn(() => 1),
  clearWatch: jest.fn(),
}));

// Mock SQLite
jest.mock("react-native-sqlite-storage", () => ({
  openDatabase: jest.fn(() => ({
    transaction: jest.fn(),
    executeSql: jest.fn(),
    close: jest.fn(),
  })),
}));

// Mock Chart Kit
jest.mock("react-native-chart-kit", () => ({
  LineChart: "LineChart",
  BarChart: "BarChart",
  PieChart: "PieChart",
  ProgressChart: "ProgressChart",
}));

// Mock SVG
jest.mock("react-native-svg", () => ({
  Svg: "Svg",
  Circle: "Circle",
  Path: "Path",
  G: "G",
  Text: "Text",
  Rect: "Rect",
}));

// Mock Paper
jest.mock("react-native-paper", () => ({
  Provider: ({ children }: any) => children,
  DefaultTheme: {},
  configureFonts: jest.fn(),
}));

// Mock Reanimated
jest.mock("react-native-reanimated", () => {
  const Reanimated = require("react-native-reanimated/mock");
  Reanimated.default.call = () => {};
  return Reanimated;
});

// Mock Async Storage
jest.mock("@react-native-async-storage/async-storage", () => ({
  setItem: jest.fn(() => Promise.resolve()),
  getItem: jest.fn(() => Promise.resolve(null)),
  removeItem: jest.fn(() => Promise.resolve()),
  clear: jest.fn(() => Promise.resolve()),
  getAllKeys: jest.fn(() => Promise.resolve([])),
  multiGet: jest.fn(() => Promise.resolve([])),
  multiSet: jest.fn(() => Promise.resolve()),
  multiRemove: jest.fn(() => Promise.resolve()),
}));

// Global test utilities
global.fetch = jest.fn();
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn(),
};

// Set test timeout
jest.setTimeout(10000);

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
});

// 全局错误处理
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === "string" &&
      (args[0].includes("Warning: ReactDOM.render is deprecated") ||
        args[0].includes("Warning: componentWillReceiveProps"))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
