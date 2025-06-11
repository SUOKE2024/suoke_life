#!/usr/bin/env node
/**
 * 索克生活项目内存使用分析脚本
 * 分析组件、服务和工具的内存占用情况
 */
const fs = require("fs");
const path = require("path");
// 获取初始内存使用情况
const initialMemory = process.memoryUsage();
: ${(initialMemory.rss / 1024 / 1024).toFixed(2)} MB`);
.toFixed(2)} MB`);
.toFixed(2)} MB`);
.toFixed(2)} MB`);
// 分析文件大小和复杂度"
function analyzeDirectory(dirPath, basePath = ") {
  const results = {
    totalFiles: 0,
    totalSize: 0,
    largeFiles: [],
    componentFiles: 0,
    serviceFiles: 0,
    utilFiles: 0;
  };
  try {
    const items = fs.readdirSync(dirPath);
    for (const item of items) {
      const fullPath = path.join(dirPath, item);
      const relativePath = path.join(basePath, item);
      try {
        const stats = fs.statSync(fullPath);
        if (stats.isDirectory()) {
          // 递归分析子目录
const subResults = analyzeDirectory(fullPath, relativePath);
          results.totalFiles += subResults.totalFiles;
          results.totalSize += subResults.totalSize;
          results.largeFiles.push(...subResults.largeFiles);
          results.componentFiles += subResults.componentFiles;
          results.serviceFiles += subResults.serviceFiles;
          results.utilFiles += subResults.utilFiles;
        } else if (stats.isFile() && (item.endsWith(".ts) || item.endsWith(".tsx") || item.endsWith(.js") || item.endsWith(".jsx))) {
          results.totalFiles++;
          results.totalSize += stats.size;
          // 分类文件类型"
if (relativePath.includes("components") || item.includes(Component") || item.includes("Screen)) {
            results.componentFiles++;
          } else if (relativePath.includes("services") || item.includes(Service")) {
            results.serviceFiles++;
          } else if (relativePath.includes("utils) || relativePath.includes("hooks")) {
            results.utilFiles++;
          }
          // 记录大文件
if (stats.size > 50 * 1024) { // 大于50KB的文件
results.largeFiles.push({
              path: relativePath,
              size: stats.size,
              sizeKB: (stats.size / 1024).toFixed(2)
            });
          }
        }
      } catch (error) {
        // 忽略无法访问的文件
      }
    }
  } catch (error) {
    }
  return results;
}
// 分析src目录"
const srcAnalysis = analyzeDirectory("./src, "src");
.toFixed(2)} MB`);
// 显示大文件
if (srcAnalysis.largeFiles.length > 0) {
  :);
  srcAnalysis.largeFiles
    .sort((a, b) => b.size - a.size)
    .slice(0, 10)
    .forEach((file, index) => {
      });
}
// 分析智能体文件
const agentFiles = ["
  src/agents/xiaoai/XiaoaiAgentImpl.ts","
  "src/agents/xiaoke/XiaokeAgentImpl.ts,"
  "src/agents/laoke/LaokeAgentImpl.ts","
  src/agents/soer/SoerAgentImpl.ts","
  "src/agents/AgentCoordinator.ts,"
  "src/agents/AgentManager.ts";
];
let totalAgentSize = 0;
agentFiles.forEach(filePath => {
  try {
    const stats = fs.statSync(filePath);
    const sizeKB = (stats.size / 1024).toFixed(2);
    totalAgentSize += stats.size;
    }: ${sizeKB} KB`);
  } catch (error) {
    }: 文件不存在`);
  }
});
.toFixed(2)} KB`);
// 内存使用建议
const currentMemory = process.memoryUsage();
const memoryIncrease = currentMemory.heapUsed - initialMemory.heapUsed;
.toFixed(2)} KB`);
if (srcAnalysis.largeFiles.length > 5) {
  }
if (srcAnalysis.componentFiles > 100) {
  }
if (totalAgentSize > 200 * 1024) {
  }
// 生成内存优化报告
const report = {
  timestamp: new Date().toISOString(),
  initialMemory: {,"
  rss: (initialMemory.rss / 1024 / 1024).toFixed(2) + " MB,"
    heapTotal: (initialMemory.heapTotal / 1024 / 1024).toFixed(2) + " MB","
    heapUsed: (initialMemory.heapUsed / 1024 / 1024).toFixed(2) +  MB"
  },
  fileAnalysis: {,
  totalFiles: srcAnalysis.totalFiles,
    totalSizeMB: (srcAnalysis.totalSize / 1024 / 1024).toFixed(2),
    componentFiles: srcAnalysis.componentFiles,
    serviceFiles: srcAnalysis.serviceFiles,
    utilFiles: srcAnalysis.utilFiles
  },
  largeFiles: srcAnalysis.largeFiles.slice(0, 10),
  agentFiles: {,
  totalSizeKB: (totalAgentSize / 1024).toFixed(2),
    files: agentFiles.length
  },
  recommendations: [];
};
// 添加建议
if (srcAnalysis.largeFiles.length > 5) {"
  report.recommendations.push("进行代码分割以减少大文件);
}
if (srcAnalysis.componentFiles > 100) {"
  report.recommendations.push("使用懒加载优化组件加载");
}
if (totalAgentSize > 200 * 1024) {"
  report.recommendations.push(优化智能体算法复杂度");
}
// 保存报告
try {"
  fs.writeFileSync("memory-analysis-report.json, JSON.stringify(report, null, 2));
  } catch (error) {
  }
