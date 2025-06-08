/**
 * 简化的索克生活端到端测试设置文件
 * Simplified Suoke Life End-to-End Test Setup
 */
import 'react-native-gesture-handler/jestSetup';
// 扩展Jest匹配器
import '@testing-library/jest-native/extend-expect';
// 全局测试配置
(global as any).__DEV__ = true;
(global as any).__TEST__ = true;
// 设置测试超时
jest.setTimeout(300000); // 5分钟
// 模拟React Native核心模块
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
  };
});
// 模拟导航
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
    reset: jest.fn(),
    setParams: jest.fn(),
  }),
  useRoute: () => ({
    params: {},
  }),
  useFocusEffect: jest.fn(),
  NavigationContainer: ({ children }: { children: React.ReactNode }) => children,
}));
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
// 模拟fetch
global.fetch = jest.fn(() =>
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
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning:') || args[0].includes('ReactDOM.render'))
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
console.log('🚀 索克生活端到端测试环境已初始化（简化版）');
export {};