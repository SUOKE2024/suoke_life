module.exports = {
  root: true,
  extends: ['@react-native'],
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
  },
  env: {
    jest: true,
    node: true,
  },
};
