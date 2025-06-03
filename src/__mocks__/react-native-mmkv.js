//////     react-native-mmkv.js - 索克生活APP - MMKV存储Mock;
export const MMKV = jest.fn().mockImplementation(() => ({
  set: jest.fn(),
  getString: jest.fn(() => null),
  getNumber: jest.fn(() => null),
  getBoolean: jest.fn(() => null),
  getBuffer: jest.fn(() => null),
  contains: jest.fn(() => false),
  delete: jest.fn(),
  getAllKeys: jest.fn(() => []),
  clearAll: jest.fn(),;
  recrypt: jest.fn(),;
  size: 0;
}));
export default {;
  MMKV;
};