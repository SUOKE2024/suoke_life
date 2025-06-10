const mockDeviceInfo = {
  getUniqueId: jest.fn(() => Promise.resolve('mock-unique-id')),
  getManufacturer: jest.fn(() => Promise.resolve('mock-manufacturer')),
  getModel: jest.fn(() => Promise.resolve('mock-model')),
  getDeviceId: jest.fn(() => Promise.resolve('mock-device-id')),
  getSystemName: jest.fn(() => Promise.resolve('mock-system')),
  getSystemVersion: jest.fn(() => Promise.resolve('mock-version')),
  getBundleId: jest.fn(() => Promise.resolve('mock-bundle-id')),
  getApplicationName: jest.fn(() => Promise.resolve('mock-app-name')),
  getBuildNumber: jest.fn(() => Promise.resolve('mock-build')),
  getVersion: jest.fn(() => Promise.resolve('mock-version')),
  getReadableVersion: jest.fn(() => Promise.resolve('mock-readable-version')),
  getDeviceName: jest.fn(() => Promise.resolve('mock-device-name')),
  getUserAgent: jest.fn(() => Promise.resolve('mock-user-agent')),
  getFontScale: jest.fn(() => Promise.resolve(1.0)),
  isEmulator: jest.fn(() => Promise.resolve(false)),
  isTablet: jest.fn(() => Promise.resolve(false)),
  hasNotch: jest.fn(() => Promise.resolve(false)),
  getDeviceType: jest.fn(() => Promise.resolve('Handset')),
  supported32BitAbis: jest.fn(() => Promise.resolve([])),
  supported64BitAbis: jest.fn(() => Promise.resolve([])),
  supportedAbis: jest.fn(() => Promise.resolve([]))
};

module.exports = mockDeviceInfo;
