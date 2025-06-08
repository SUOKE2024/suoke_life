import 'react-native-gesture-handler/jestSetup';
import mockAsyncStorage from '@react-native-async-storage/async-storage/jest/async-storage-mock';
jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage);
// Mock react-native-vector-icons
jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');
// Mock navigation
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn();
  }),
  useRoute: () => ({
    params: {}
  })
}));
// Global test utilities
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn();
};
// Performance mock
(global as any).performance = {
  now: jest.fn(() => Date.now())
};