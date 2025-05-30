#!/usr/bin/env node

/**
 * 索克生活项目组件性能优化实施脚本
 * 自动优化React组件的性能问题
 */

const fs = require('fs');
const path = require('path');

console.log('⚡ 索克生活组件性能优化');
console.log('=====================================');

// 性能优化统计
const optimizationStats = {
  totalComponents: 0,
  optimizedComponents: 0,
  addedMemo: 0,
  addedCallback: 0,
  addedUseMemo: 0,
  errors: []
};

/**
 * 分析组件文件并应用优化
 */
function optimizeComponent(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    let optimizedContent = content;
    let hasChanges = false;

    // 检查是否已经使用了React.memo
    if (!content.includes('React.memo') && !content.includes('memo(')) {
      // 检查是否是函数组件
      const isFunctionComponent = content.includes('const ') && 
                                 content.includes('= (') && 
                                 content.includes('return');
      
      if (isFunctionComponent) {
        // 添加React.memo包装
        optimizedContent = optimizedContent.replace(
          /export default (\w+);/,
          'export default React.memo($1);'
        );
        
        // 确保导入了React
        if (!content.includes('import React')) {
          optimizedContent = `import React from 'react';\n${optimizedContent}`;
        }
        
        hasChanges = true;
        optimizationStats.addedMemo++;
      }
    }

    // 检查并优化useCallback使用
    const callbackPattern = /const\s+(\w+)\s+=\s+\([^)]*\)\s+=>\s+{/g;
    let match;
    while ((match = callbackPattern.exec(content)) !== null) {
      const functionName = match[1];
      
      // 检查是否已经使用useCallback
      if (!content.includes(`useCallback(`) || 
          !content.includes(functionName)) {
        
        // 建议使用useCallback的函数名模式
        if (functionName.startsWith('handle') || 
            functionName.startsWith('on') ||
            functionName.includes('Handler')) {
          
          console.log(`  💡 建议为 ${functionName} 使用 useCallback`);
          optimizationStats.addedCallback++;
        }
      }
    }

    // 检查并优化useMemo使用
    const expensiveOperations = [
      'filter(',
      'map(',
      'reduce(',
      'sort(',
      'find(',
      'JSON.parse',
      'JSON.stringify'
    ];

    expensiveOperations.forEach(operation => {
      if (content.includes(operation) && !content.includes('useMemo')) {
        console.log(`  💡 建议为包含 ${operation} 的计算使用 useMemo`);
        optimizationStats.addedUseMemo++;
      }
    });

    // 如果有修改，写回文件
    if (hasChanges) {
      fs.writeFileSync(filePath, optimizedContent);
      optimizationStats.optimizedComponents++;
      console.log(`  ✅ 优化完成: ${path.basename(filePath)}`);
    }

    optimizationStats.totalComponents++;

  } catch (error) {
    optimizationStats.errors.push({
      file: filePath,
      error: error.message
    });
    console.log(`  ❌ 优化失败: ${path.basename(filePath)} - ${error.message}`);
  }
}

/**
 * 递归扫描目录中的组件文件
 */
function scanDirectory(dirPath) {
  try {
    const items = fs.readdirSync(dirPath);
    
    for (const item of items) {
      const fullPath = path.join(dirPath, item);
      const stats = fs.statSync(fullPath);
      
      if (stats.isDirectory()) {
        // 跳过node_modules等目录
        if (!item.startsWith('.') && 
            item !== 'node_modules' && 
            item !== 'coverage') {
          scanDirectory(fullPath);
        }
      } else if (stats.isFile()) {
        // 处理React组件文件
        if ((item.endsWith('.tsx') || item.endsWith('.jsx')) &&
            (item.includes('Component') || 
             item.includes('Screen') ||
             fullPath.includes('/components/') ||
             fullPath.includes('/screens/'))) {
          
          console.log(`🔧 分析组件: ${path.relative(process.cwd(), fullPath)}`);
          optimizeComponent(fullPath);
        }
      }
    }
  } catch (error) {
    console.warn(`⚠️  无法访问目录: ${dirPath}`);
  }
}

// 开始优化
console.log('\n🔍 扫描组件文件...');
scanDirectory('./src');

// 创建性能优化配置文件
const performanceConfig = {
  optimization: {
    memo: {
      enabled: true,
      autoApply: true,
      excludePatterns: ['*Test*', '*Mock*']
    },
    callback: {
      enabled: true,
      suggestOnly: true,
      patterns: ['handle*', 'on*', '*Handler']
    },
    useMemo: {
      enabled: true,
      suggestOnly: true,
      expensiveOperations: [
        'filter', 'map', 'reduce', 'sort', 'find',
        'JSON.parse', 'JSON.stringify'
      ]
    }
  },
  monitoring: {
    enabled: true,
    threshold: {
      renderTime: 16, // 16ms (60fps)
      rerenderCount: 5
    }
  }
};

try {
  fs.writeFileSync('performance-config.json', JSON.stringify(performanceConfig, null, 2));
  console.log('\n📄 性能配置文件已创建: performance-config.json');
} catch (error) {
  console.warn('⚠️  无法创建配置文件');
}

// 创建性能监控Hook
const performanceHookContent = `import { useEffect, useRef } from 'react';

/**
 * 组件性能监控Hook
 * 自动生成的性能优化工具
 */
export const usePerformanceMonitor = (componentName: string) => {
  const renderCountRef = useRef(0);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    startTimeRef.current = performance.now();
    renderCountRef.current += 1;
  });

  useEffect(() => {
    const endTime = performance.now();
    const renderTime = endTime - startTimeRef.current;
    
    if (renderTime > 16) { // 超过16ms
      console.warn(\`⚠️  \${componentName} 渲染时间过长: \${renderTime.toFixed(2)}ms\`);
    }
    
    if (renderCountRef.current > 5) {
      console.warn(\`⚠️  \${componentName} 重渲染次数过多: \${renderCountRef.current}\`);
    }
  });

  return {
    renderCount: renderCountRef.current,
    componentName
  };
};

export default usePerformanceMonitor;
`;

try {
  const hooksDir = './src/hooks';
  if (!fs.existsSync(hooksDir)) {
    fs.mkdirSync(hooksDir, { recursive: true });
  }
  
  fs.writeFileSync(path.join(hooksDir, 'usePerformanceMonitor.ts'), performanceHookContent);
  console.log('📄 性能监控Hook已创建: src/hooks/usePerformanceMonitor.ts');
} catch (error) {
  console.warn('⚠️  无法创建性能监控Hook');
}

// 输出优化报告
console.log('\n📊 组件性能优化报告');
console.log('=====================================');
console.log(`总组件数: ${optimizationStats.totalComponents}`);
console.log(`已优化组件: ${optimizationStats.optimizedComponents}`);
console.log(`添加React.memo: ${optimizationStats.addedMemo}`);
console.log(`建议useCallback: ${optimizationStats.addedCallback}`);
console.log(`建议useMemo: ${optimizationStats.addedUseMemo}`);

if (optimizationStats.errors.length > 0) {
  console.log(`\n❌ 错误数量: ${optimizationStats.errors.length}`);
  optimizationStats.errors.slice(0, 5).forEach(error => {
    console.log(`  ${path.basename(error.file)}: ${error.error}`);
  });
}

// 生成优化建议
console.log('\n💡 性能优化建议:');

if (optimizationStats.addedCallback > 0) {
  console.log('  🔄 考虑为事件处理函数使用useCallback');
}

if (optimizationStats.addedUseMemo > 0) {
  console.log('  🧠 考虑为复杂计算使用useMemo');
}

if (optimizationStats.totalComponents > 50) {
  console.log('  📦 考虑使用代码分割和懒加载');
}

console.log('  📊 使用生成的usePerformanceMonitor监控组件性能');

console.log('\n✅ 组件性能优化完成！'); 