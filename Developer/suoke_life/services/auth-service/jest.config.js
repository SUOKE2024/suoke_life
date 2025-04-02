/**
 * Jest配置文件
 */
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!**/node_modules/**',
    '!**/vendor/**'
  ],
  testMatch: [
    '**/tests/**/*.test.js',
    '**/src/tests/**/*.test.js'
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/config/',
    '/dist/'
  ],
  moduleNameMapper: {
    '@suoke/shared': '<rootDir>/src/mocks/shared.js'
  },
  setupFilesAfterEnv: ['<rootDir>/src/tests/setup.js'],
  verbose: true,
  forceExit: true,
  clearMocks: true,
  resetMocks: false,
  restoreMocks: true
}; 