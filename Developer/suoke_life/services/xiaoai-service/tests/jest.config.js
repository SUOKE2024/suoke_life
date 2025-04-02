module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/unit'],
  testMatch: ['**/*.test.ts'],
  collectCoverage: true,
  collectCoverageFrom: [
    '../src/**/*.ts',
    '!../src/index.ts',
    '!../src/types/**',
    '!../src/**/*.d.ts',
  ],
  coverageDirectory: '../coverage',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/../src/$1',
  },
  testTimeout: 30000,
  verbose: true,
}; 