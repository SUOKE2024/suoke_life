#!/usr/bin/env node
/**
 * 索克生活项目组件性能优化实施脚本
 * 自动优化React组件的性能问题
 */
const fs = require("fs");
const path = require("path");
// 性能优化统计
const optimizationStats = {
  totalComponents: 0,
  optimizedComponents: 0,
  addedMemo: 0,
  addedCallback: 0,
  addedUseMemo: 0,
  errors: [];
};
/**
 * 分析组件文件并应用优化
 */
function optimizeComponent(filePath) {
  try {"
    const content = fs.readFileSync(filePath, "utf8");
    let optimizedContent = content;
    let hasChanges = false;
    // 检查是否已经使用了React.memo"
if (!content.includes(React.memo") && !content.includes("memo()) {
      // 检查是否是函数组件"
const isFunctionComponent = content.includes("const ") && "
                                 content.includes(= (") && ;
                                 content.includes("return);
      if (isFunctionComponent) {
        // 添加React.memo包装
optimizedContent = optimizedContent.replace(
          /export default (\w+);/,"
          "export default React.memo($1);
        );
        // 确保导入了React"
if (!content.includes(import React")) {"
          optimizedContent = `import React  from "react;\n${optimizedContent}`;
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
        // 建议使用useCallback的函数名模式"
if (functionName.startsWith(";handle") || "
            functionName.startsWith(on") ||"
            functionName.includes("Handler)) {
          optimizationStats.addedCallback++;
        }
      }
    }
    // 检查并优化useMemo使用
const expensiveOperations = ["
      "filter(","
      map(","
      "reduce(,"
      "sort(","
      find(","
      "JSON.parse,"
      "JSON.stringify";
    ];
    expensiveOperations.forEach(operation => {"
      if (content.includes(operation) && !content.includes(useMemo")) {
        optimizationStats.addedUseMemo++;
      }
    });
    // 如果有修改，写回文件
if (hasChanges) {
      fs.writeFileSync(filePath, optimizedContent);
      optimizationStats.optimizedComponents++;
      }`);
    }
    optimizationStats.totalComponents++;
  } catch (error) {
    optimizationStats.errors.push({
      file: filePath,
      error: error.message
    });
    } - ${error.message}`);
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
        // 跳过node_modules等目录"
if (!item.startsWith(".) && "
            item !== "node_modules" && "
            item !== coverage") {
          scanDirectory(fullPath);
        }
      } else if (stats.isFile()) {
        // 处理React组件文件"
if ((item.endsWith(".tsx) || item.endsWith(".jsx")) &&"
            (item.includes(Component") || "
             item.includes("Screen) ||"
             fullPath.includes("/components/") ||"
             fullPath.includes(/screens/"))) {
          , fullPath)}`);
          optimizeComponent(fullPath);
        }
      }
    }
  } catch (error) {
    }
}
// 开始优化"
scanDirectory("./src");
// 创建性能优化配置文件
const performanceConfig = {
  optimization: {,
  memo: {,
  enabled: true,
      autoApply: true,"
      excludePatterns: [*Test*", "*Mock*]
    },
    callback: {,
  enabled: true,
      suggestOnly: true,"
      patterns: ["handle*", on*", "*Handler]
    },
    useMemo: {,
  enabled: true,
      suggestOnly: true,
      expensiveOperations: ["
        "filter", map", "reduce, "sort", find","
        "JSON.parse, "JSON.stringify"
      ]
    }
  },
  monitoring: {,
  enabled: true,
    threshold: {,
  renderTime: 16, // 16ms (60fps)
      rerenderCount: 5
    }
  }
};
try {"
  fs.writeFileSync(performance-config.json", JSON.stringify(performanceConfig, null, 2));
  } catch (error) {
  }
// 创建性能监控Hook"
const performanceHookContent = `import { useEffect, useRef } from react";
/**
 * 组件性能监控Hook
 * 自动生成的性能优化工具
 */
export const usePerformanceMonitor = (componentName: string) => {;
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
}ms\`);
    }
    if (renderCountRef.current > 5) {
      }
  });
  return {
    renderCount: renderCountRef.current,
    componentName
  };
};
export default usePerformanceMonitor;
`;
try {"
  const hooksDir = "./src/hooks;
  if (!fs.existsSync(hooksDir)) {
    fs.mkdirSync(hooksDir, { recursive: true });
  }
  fs.writeFileSync(path.join(hooksDir, "usePerformanceMonitor.ts"), performanceHookContent);
  } catch (error) {
  }
// 输出优化报告
if (optimizationStats.errors.length > 0) {
  optimizationStats.errors.slice(0, 5).forEach(error => {
    }: ${error.error}`);
  });
}
// 生成优化建议
if (optimizationStats.addedCallback > 0) {
  }
if (optimizationStats.addedUseMemo > 0) {
  }
if (optimizationStats.totalComponents > 50) {
  }
