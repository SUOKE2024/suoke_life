module.exports = {
  root: true,
  extends: ['@react-native', 'plugin:security/recommended'],
  plugins: [
    'security',
    'privacy',
  ],
  rules: {
    // 关闭格式化相关规则
    'prettier/prettier': 'off',
    'quotes': 'off',
    'eol-last': 'off',
    'no-trailing-spaces': 'off',
    
    // 保留重要的语法检查
    'react-native/no-inline-styles': 'off',
    'react-hooks/exhaustive-deps': 'warn',
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-fallthrough': 'warn',
    'no-new': 'warn',
    // 禁止console输出敏感信息
    'no-console': [
      'error',
      {
        allow: ['warn', 'error', 'info']
      }
    ],
    // 自定义规则：禁止明文手机号、身份证号等敏感信息
    'privacy/no-plain-sensitive-data': 'warn',
  },
  env: {
    jest: true,
    node: true,
  },
};
