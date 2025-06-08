/**
* 索克生活端到端测试设置文件
* Suoke Life End-to-End Test Setup
*/
import 'react-native-gesture-handler/jestSetup';
// 扩展Jest匹配器
import '@testing-library/jest-native/extend-expect';
// 全局测试配置
global.__DEV__ = true;
global.__TEST__ = true;
// 设置测试超时
jest.setTimeout(300000); // 5分钟
// 模拟React Native模块
jest.mock('react-native', () => {
  const RN = jest.requireActual('react-native');
    return {
    ...RN,
    Platform: {
      ...RN.Platform,
      OS: 'ios',
      select: jest.fn((obj) => obj.ios || obj.default),
    },
    Dimensions: {
      get: jest.fn(() => ({
        width: 375,
        height: 812,
        scale: 3,
        fontScale: 1,
      })),
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
    AppState: {
      currentState: "active",
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    },
  };
});
// 模拟导航
jest.mock('@react-navigation/native', () => {
  const actualNav = jest.requireActual('@react-navigation/native');
  return {
    ...actualNav,
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
      name: 'TestScreen',
      key: 'test-key',
    }),
    useFocusEffect: jest.fn(),
    useIsFocused: () => true,
  };
});
// 模拟权限
jest.mock('react-native-permissions', () => ({
  PERMISSIONS: {
    IOS: {
      CAMERA: "ios.permission.CAMERA",
      MICROPHONE: 'ios.permission.MICROPHONE',
      LOCATION_WHEN_IN_USE: 'ios.permission.LOCATION_WHEN_IN_USE',
    },
    ANDROID: {
      CAMERA: "android.permission.CAMERA",
      RECORD_AUDIO: 'android.permission.RECORD_AUDIO',
      ACCESS_FINE_LOCATION: 'android.permission.ACCESS_FINE_LOCATION',
    },
  },
  RESULTS: {
      GRANTED: "granted",
      DENIED: 'denied',
    BLOCKED: 'blocked',
    UNAVAILABLE: 'unavailable',
  },
  check: jest.fn(() => Promise.resolve('granted')),
  request: jest.fn(() => Promise.resolve('granted')),
  requestMultiple: jest.fn(() => Promise.resolve({})),
}));
// 模拟语音识别
jest.mock('react-native-voice', () => ({
  SpeechRecognition: {
    isAvailable: jest.fn(() => Promise.resolve(true)),
    start: jest.fn(() => Promise.resolve()),
    stop: jest.fn(() => Promise.resolve()),
    destroy: jest.fn(() => Promise.resolve()),
    removeAllListeners: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  },
}));
// 模拟相机
jest.mock('react-native-image-picker', () => ({
  launchCamera: jest.fn((options, callback) => {
    callback({
      assets: [{
      uri: "file://test-image.jpg",
      type: 'image/jpeg',
        fileName: 'test-image.jpg',
        fileSize: 1024,
      }],
    });
  }),
  launchImageLibrary: jest.fn((options, callback) => {
    callback({
      assets: [{
      uri: "file://test-image.jpg",
      type: 'image/jpeg',
        fileName: 'test-image.jpg',
        fileSize: 1024,
      }],
    });
  }),
}));
// 模拟存储
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(() => Promise.resolve(null)),
  setItem: jest.fn(() => Promise.resolve()),
  removeItem: jest.fn(() => Promise.resolve()),
  clear: jest.fn(() => Promise.resolve()),
  getAllKeys: jest.fn(() => Promise.resolve([])),
  multiGet: jest.fn(() => Promise.resolve([])),
  multiSet: jest.fn(() => Promise.resolve()),
  multiRemove: jest.fn(() => Promise.resolve()),
}));
// 模拟网络状态
jest.mock('@react-native-community/netinfo', () => ({
  fetch: jest.fn(() => Promise.resolve({
      type: "wifi",
      isConnected: true,
    isInternetReachable: true,
  })),
  addEventListener: jest.fn(() => jest.fn()),
  useNetInfo: () => ({
      type: "wifi",
      isConnected: true,
    isInternetReachable: true,
  }),
}));
// 模拟手势处理
jest.mock('react-native-gesture-handler', () => {
  const View = require('react-native/Libraries/Components/View/View');
  return {
    Swipeable: View,
    DrawerLayout: View,
    State: {},
    ScrollView: View,
    Slider: View,
    Switch: View,
    TextInput: View,
    ToolbarAndroid: View,
    ViewPagerAndroid: View,
    DrawerLayoutAndroid: View,
    WebView: View,
    NativeViewGestureHandler: View,
    TapGestureHandler: View,
    FlingGestureHandler: View,
    ForceTouchGestureHandler: View,
    LongPressGestureHandler: View,
    PanGestureHandler: View,
    PinchGestureHandler: View,
    RotationGestureHandler: View,
    RawButton: View,
    BaseButton: View,
    RectButton: View,
    BorderlessButton: View,
    FlatList: View,
    gestureHandlerRootHOC: jest.fn((component) => component),
    Directions: {},
  };
});
// 模拟Redux
jest.mock('react-redux', () => ({
  useSelector: jest.fn((selector) => selector({
    auth: {
      isAuthenticated: false,
      user: null,
      token: null,
    },
    agents: {
      xiaoai: { status: 'idle' },
      xiaoke: { status: 'idle' },
      laoke: { status: 'idle' },
      soer: { status: 'idle' },
    },
    health: {
      data: [],
      diagnosis: null,
    },
  })),
  useDispatch: () => jest.fn(),
  Provider: ({ children }: { children: React.ReactNode }) => children,
}));
// 模拟WebSocket
global.WebSocket = jest.fn(() => ({
  send: jest.fn(),
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  readyState: 1,
})) as any;
// 模拟fetch
global.fetch = jest.fn(() =>)
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
  })
) as jest.Mock;
// 模拟定时器
jest.useFakeTimers();
// 全局错误处理
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if ()
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});
afterAll(() => {
  console.error = originalError;
});
// 清理函数
afterEach(() => {
  jest.clearAllMocks();
  jest.clearAllTimers();
});
// 测试环境信息
console.log('🚀 索克生活端到端测试环境已初始化');
console.log('📱 平台: React Native');
console.log('🧪 测试框架: Jest + React Native Testing Library');
console.log('⏱️  超时时间: 5分钟');
console.log('🔧 模拟: 权限、相机、语音、存储、网络等');
export {};