import 'react-native-gesture-handler/jestSetup';

// Mock react-native modules
jest.mock('react-native-reanimated', () => {
  const Reanimated = require('react-native-reanimated/mock');
  Reanimated.default.call = () => {};
  return Reanimated;
});

// Mock react-native-vector-icons
jest.mock('react-native-vector-icons/Ionicons', () => 'Icon');

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

// Mock react-navigation
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
    dispatch: jest.fn(),
  }),
  useRoute: () => ({
    params: {},
  }),
  useFocusEffect: jest.fn(),
}));

// Mock performance monitoring
jest.mock('./src/services/monitoring/PerformanceMonitor', () => ({
  performanceMonitor: {
    start: jest.fn(),
    stop: jest.fn(),
    getMetrics: jest.fn(() => []),
    getLatestMetrics: jest.fn(() => null),
    on: jest.fn(),
    emit: jest.fn(),
  },
}));

// Mock health check service
jest.mock('./src/services/monitoring/HealthCheckService', () => ({
  healthCheckService: {
    registerService: jest.fn(),
    checkHealth: jest.fn(() => Promise.resolve({
      status: 'healthy',
      timestamp: Date.now(),
      services: {},
      metrics: {
        uptime: 0,
        memoryUsage: 0,
        cpuUsage: 0,
      },
    })),
  },
}));

// Global test setup
global.__DEV__ = true;

// Silence console warnings in tests
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn(),
}; 