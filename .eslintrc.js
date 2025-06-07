module.exports = {
  root: true,
  extends: [
    "@react-native",
    "eslint:recommended",
    "plugin:prettier/recommended",
    "plugin:import/errors",
    "plugin:import/warnings",
    "plugin:import/typescript",
    "prettier" // 确保prettier规则在最后
  ],
  plugins: [
    "@typescript-eslint",
    "react",
    "react-hooks",
    "react-native",
    "prettier",
    "import"
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: "module",
    ecmaFeatures: {
      jsx: true
    }
  },
  rules: {
    // Prettier集成 - 重新启用但设为警告
    "prettier/prettier": ["warn", {
      semi: true,
      singleQuote: true,
      trailingComma: "es5",
      printWidth: 100,
      tabWidth: 2,
      useTabs: false,
      endOfLine: "lf"
    }],
    
    // 基本语法规则
    "quotes": ["error", "single", { "avoidEscape": true }],
    "semi": ["error", "always"],
    "no-trailing-spaces": "warn",
    "eol-last": "warn",
    "comma-dangle": ["error", "always-multiline"],
    
    // TypeScript规则
    "@typescript-eslint/no-unused-vars": ["error", { 
      "argsIgnorePattern": "^_",
      "varsIgnorePattern": "^_"
    }],
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-empty-function": "warn",
    "@typescript-eslint/no-non-null-assertion": "warn",
    
    // React规则
    "react/react-in-jsx-scope": "off", // React 17+不需要导入React
    "react/prop-types": "off", // 使用TypeScript类型检查
    "react/display-name": "warn",
    "react/jsx-key": "error",
    "react/jsx-no-duplicate-props": "error",
    "react/jsx-no-undef": "error",
    "react/jsx-uses-react": "off", // React 17+
    "react/jsx-uses-vars": "error",
    "react/no-array-index-key": "warn",
    "react/no-children-prop": "error",
    "react/no-danger-with-children": "error",
    "react/no-deprecated": "warn",
    "react/no-direct-mutation-state": "error",
    "react/no-find-dom-node": "error",
    "react/no-is-mounted": "error",
    "react/no-render-return-value": "error",
    "react/no-string-refs": "error",
    "react/no-unescaped-entities": "warn",
    "react/no-unknown-property": "error",
    "react/no-unsafe": "warn",
    "react/require-render-return": "error",
    
    // React Hooks规则
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    
    // React Native规则
    "react-native/no-unused-styles": "warn",
    "react-native/split-platform-components": "warn",
    "react-native/no-inline-styles": "warn",
    "react-native/no-color-literals": "warn",
    "react-native/no-raw-text": "off", // 允许原始文本
    
    // 通用规则
    "no-console": ["warn", {
      "allow": ["warn", "error", "info"]
    }],
    "no-debugger": "error",
    "no-alert": "warn",
    "no-var": "error",
    "prefer-const": "error",
    "no-unused-vars": "off", // 使用TypeScript版本
    "no-undef": "error",
    "no-duplicate-imports": "error",
    "no-multiple-empty-lines": ["warn", { "max": 2 }],
    "no-trailing-spaces": "warn",
    "object-curly-spacing": ["warn", "always"],
    "array-bracket-spacing": ["warn", "never"],
    "computed-property-spacing": ["warn", "never"],
    "space-in-parens": ["warn", "never"],
    "space-before-blocks": "warn",
    "keyword-spacing": "warn",
    "comma-spacing": "warn",
    "key-spacing": "warn",
    "arrow-spacing": "warn",
    
    // 安全规则
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "no-script-url": "error",
    
    // 性能规则
    "no-loop-func": "warn",
    "no-inner-declarations": "warn",
    
    // 可访问性规则
    "jsx-a11y/accessible-emoji": "off", // React Native不适用
    "jsx-a11y/alt-text": "off", // React Native不适用
    
    // 导入规则
    "import/no-unresolved": "off", // 由TypeScript处理
    "import/named": "off", // 由TypeScript处理
    "import/default": "off", // 由TypeScript处理
    "import/namespace": "off", // 由TypeScript处理
    "import/order": ["warn", {
      "groups": [
        "builtin",
        "external",
        "internal",
        "parent",
        "sibling",
        "index"
      ],
      "newlines-between": "always",
      "alphabetize": {
        "order": "asc",
        "caseInsensitive": true
      }
    }]
  },
  env: {
    jest: true,
    node: true,
    es6: true,
    "react-native/react-native": true
  },
  settings: {
    react: {
      version: "detect"
    },
    "react-native/style-sheet-object-names": [
      "StyleSheet",
      "PlatformStyleSheet",
      "styles"
    ]
  },
  overrides: [
    {
      files: ["*.test.{js,jsx,ts,tsx}", "**/__tests__/**/*"],
      env: {
        jest: true
      },
      rules: {
        "@typescript-eslint/no-explicit-any": "off",
        "react-native/no-inline-styles": "off"
      }
    },
    {
      files: ["scripts/**/*.js"],
      env: {
        node: true
      },
      rules: {
        "no-console": "off",
        "@typescript-eslint/no-var-requires": "off"
      }
    }
  ]
};
