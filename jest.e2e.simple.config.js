module.exports = {
  preset: 'react-native',
  testEnvironment: 'node',
  
  testMatch: [
    '<rootDir>/src/__tests__/e2e/**/*.test.{js,jsx,ts,tsx}',
  ],
  
  setupFilesAfterEnv: [
    '<rootDir>/src/__tests__/setup/e2e-setup-minimal.ts',
  ],
  
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/android/',
    '<rootDir>/ios/',
  ],
  
  collectCoverage: false,
  testTimeout: 300000,
  
  globals: {
    __DEV__: true,
    __TEST__: true,
  },
  
  clearMocks: true,
  resetMocks: true,
  restoreMocks: true,
  verbose: true,
  forceExit: true,
  maxWorkers: 1,
}; 