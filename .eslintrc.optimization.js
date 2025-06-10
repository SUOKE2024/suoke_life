module.exports = {
  extends: [
    '@react-native-community',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:react-native/all'
  ],
  parser: '@typescript-eslint/parser',
  plugins: [
    '@typescript-eslint',
    'react-hooks',
    'react-native',
    'import',
    'jsx-a11y'
  ],
  rules: {
    // 性能相关规则
    'react-hooks/exhaustive-deps': 'warn',
    'react-native/no-inline-styles': 'warn',
    'react-native/no-color-literals': 'warn',
    'react-native/no-unused-styles': 'error',
    
    // 代码质量规则
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    
    // 导入规则
    'import/order': ['error', {
      'groups': ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
      'newlines-between': 'always'
    }],
    
    // 可访问性规则
    'jsx-a11y/accessible-emoji': 'warn',
    'jsx-a11y/alt-text': 'warn'
  },
  settings: {
    'import/resolver': {
      'typescript': {}
    }
  }
};
