#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const setupTestsPath = path.join(__dirname, '..', 'src', 'setupTests.ts');

console.log('🔧 修复 setupTests.ts 文件...');

try {
  let content = fs.readFileSync(setupTestsPath, 'utf8');
  
  // 修复第12行的分号错误
  content = content.replace(
    /jest\.mock\('@react-native-async-storage\/async-storage', \(\) =>\n  require\('@react-native-async-storage\/async-storage\/jest\/async-storage-mock'\);\n\);/g,
    `jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);`
  );
  
  // 修复对象字面量中的分号错误
  content = content.replace(/clearAll: jest\.fn\(\);\n  \}\)\),/g, 'clearAll: jest.fn()\n  })),');
  content = content.replace(/clearAll: jest\.fn\(\);\n  \}\n\}\)\);/g, 'clearAll: jest.fn()\n  }\n}));');
  content = content.replace(/removeAllListeners: jest\.fn\(\);\n\}\)\);/g, 'removeAllListeners: jest.fn()\n}));');
  content = content.replace(/dispatch: jest\.fn\(\);\n  \}\),/g, 'dispatch: jest.fn()\n  }),');
  content = content.replace(/error: jest\.fn\(\);\n\};/g, 'error: jest.fn()\n};');
  
  fs.writeFileSync(setupTestsPath, content);
  console.log('✅ setupTests.ts 修复完成');
  
} catch (error) {
  console.error('❌ 修复失败:', error.message);
  process.exit(1);
} 