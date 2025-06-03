module.exports = {
  root: true,
  extends: ["@react-native"],
  plugins: [
    // 移除不存在的插件
  ],
  rules: {
    // 关闭格式化相关规则
    "prettier/prettier": "off",
    "quotes": "off",
    "eol-last": "off",
    "no-trailing-spaces": "off",
    
    // 保留重要的语法检查
    "react-native/no-inline-styles": "off",
    "react-hooks/exhaustive-deps": "warn",
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "no-fallthrough": "warn",
    "no-new": "warn",
    // 禁止console输出敏感信息
    "no-console": [
      "warn",
      {
        "allow": ["warn", "error", "info"]
      }
    ],
    // TypeScript相关规则
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-empty-function": "warn"
  },
  env: {
    jest: true,
    node: true
  }
}
