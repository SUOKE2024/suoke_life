module.exports = {
  preset: "react-native",
  testEnvironment: "node",
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
  transform: {
    "^.+\\.(js|jsx|ts|tsx)$": ["babel-jest", {
      presets: [
        ["@babel/preset-env", { targets: { node: "current" } }],
        "@babel/preset-typescript",
        "@babel/preset-react"
      ],
      plugins: [
        "@babel/plugin-transform-runtime",
        "@babel/plugin-proposal-class-properties",
        "@babel/plugin-transform-private-methods",
        "@babel/plugin-transform-private-property-in-object"
      ]
    }]
  },
  transformIgnorePatterns: [
    "node_modules/(?!(react-native|@react-native|react-native-vector-icons|@react-navigation|react-redux|@reduxjs|react-native-reanimated|react-native-gesture-handler|react-native-screens|react-native-safe-area-context|@react-native-async-storage|react-native-mmkv|react-native-device-info|react-native-permissions|react-native-vision-camera|react-native-voice|react-native-chart-kit|victory-native|react-native-svg|react-native-paper)/)"
  ],
  testPathIgnorePatterns: [
    "<rootDir>/node_modules/",
    "<rootDir>/.backup/",
    "<rootDir>/services/.*/\\.venv/",
    "<rootDir>/services/.*/.mypy_cache/",
    "<rootDir>/services/.*/.ruff_cache/",
    "<rootDir>/services/.*/.pytest_cache/",
    "<rootDir>/android/",
    "<rootDir>/ios/",
    "<rootDir>/deploy/"
  ],
  setupFiles: ["<rootDir>/src/setupTests.ts"],
  setupFilesAfterEnv: [],
  testMatch: [
    "**/__tests__/**/*.(ts|tsx|js)",
    "**/*.(test|spec).(ts|tsx|js)"
  ],
  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/index.tsx",
    "!src/**/__tests__/**",
    "!src/**/*.test.{ts,tsx}",
    "!src/**/*.spec.{ts,tsx}",
    "!src/assets/**",
    "!src/constants/**"
  ],
  coverageReporters: ["text", "lcov", "html", "json-summary"],
  coverageDirectory: "coverage",
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "^@assets/(.*)$": "<rootDir>/src/assets/$1",
    "^@components/(.*)$": "<rootDir>/src/components/$1",
    "^@constants/(.*)$": "<rootDir>/src/constants/$1",
    "^@contexts/(.*)$": "<rootDir>/src/contexts/$1",
    "^@hooks/(.*)$": "<rootDir>/src/hooks/$1",
    "^@navigation/(.*)$": "<rootDir>/src/navigation/$1",
    "^@screens/(.*)$": "<rootDir>/src/screens/$1",
    "^@services/(.*)$": "<rootDir>/src/services/$1",
    "^@store/(.*)$": "<rootDir>/src/store/$1",
    "^@types/(.*)$": "<rootDir>/src/types/$1",
    "^@utils/(.*)$": "<rootDir>/src/utils/$1",
    // React Native模块映射
    "^react-native$": "react-native",
    "^react-native-permissions$": "<rootDir>/src/__mocks__/react-native-permissions.js",
    "^react-native-vector-icons/(.*)$": "<rootDir>/src/__mocks__/react-native-vector-icons.js",
    "^react-native-device-info$": "<rootDir>/src/__mocks__/react-native-device-info.js",
    "^react-native-mmkv$": "<rootDir>/src/__mocks__/react-native-mmkv.js"
  },
  testTimeout: 10000,
  maxWorkers: "50%",
  cacheDirectory: "<rootDir>/.jest-cache",
  clearMocks: true,
  restoreMocks: true,
  verbose: false,
  collectCoverage: false, // 暂时关闭覆盖率收集，先修复测试
  // 全局设置
  globals: {
    __DEV__: true
  }
}