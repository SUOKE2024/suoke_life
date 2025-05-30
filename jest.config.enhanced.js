module.exports = {
  "preset": "react-native",
  "setupFilesAfterEnv": [
    "<rootDir>/src/setupTests.ts"
  ],
  "testMatch": [
    "<rootDir>/src/**/__tests__/**/*.{ts,tsx}",
    "<rootDir>/src/**/*.{test,spec}.{ts,tsx}"
  ],
  "collectCoverageFrom": [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/**/__tests__/**",
    "!src/**/node_modules/**"
  ],
  "coverageThreshold": {
    "global": {
      "branches": 70,
      "functions": 70,
      "lines": 70,
      "statements": 70
    },
    "./src/components/": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    },
    "./src/services/": {
      "branches": 75,
      "functions": 75,
      "lines": 75,
      "statements": 75
    },
    "./src/hooks/": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    }
  },
  "testEnvironment": "jsdom",
  "transform": {
    "^.+\\.(ts|tsx)$": "babel-jest"
  },
  "moduleNameMapping": {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy"
  }
};