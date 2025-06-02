#!/usr/bin/env node

/**
 * 索克生活项目内存使用分析脚本
 * 分析组件、服务和工具的内存占用情况
 */

const fs = require('fs');
const path = require('path');

console.log('🧠 索克生活项目内存使用分析');
console.log('=====================================');

// 获取初始内存使用情况
const initialMemory = process.memoryUsage();
console.log('\n📊 初始内存使用情况:');
console.log(`  RSS (常驻内存): ${(initialMemory.rss / 1024 / 1024).toFixed(2)} MB`);
console.log(`  堆内存总量: ${(initialMemory.heapTotal / 1024 / 1024).toFixed(2)} MB`);
console.log(`  堆内存使用: ${(initialMemory.heapUsed / 1024 / 1024).toFixed(2)} MB`);
console.log(`  外部内存: ${(initialMemory.external / 1024 / 1024).toFixed(2)} MB`);

// 分析文件大小和复杂度
function analyzeDirectory(dirPath, basePath = '') {
  const results = {
    totalFiles: 0,
    totalSize: 0,
    largeFiles: [],
    componentFiles: 0,
    serviceFiles: 0,
    utilFiles: 0
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
        } else if (stats.isFile() && (item.endsWith('.ts') || item.endsWith('.tsx') || item.endsWith('.js') || item.endsWith('.jsx'))) {
          results.totalFiles++;
          results.totalSize += stats.size;

          // 分类文件类型
          if (relativePath.includes('components') || item.includes('Component') || item.includes('Screen')) {
            results.componentFiles++;
          } else if (relativePath.includes('services') || item.includes('Service')) {
            results.serviceFiles++;
          } else if (relativePath.includes('utils') || relativePath.includes('hooks')) {
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
    console.warn(`⚠️  无法访问目录: ${dirPath}`);
  }

  return results;
}

// 分析src目录
console.log('\n📁 分析src目录结构...');
const srcAnalysis = analyzeDirectory('./src', 'src');

console.log('\n📊 文件分析结果:');
console.log(`  总文件数: ${srcAnalysis.totalFiles}`);
console.log(`  总大小: ${(srcAnalysis.totalSize / 1024 / 1024).toFixed(2)} MB`);
console.log(`  组件文件: ${srcAnalysis.componentFiles}`);
console.log(`  服务文件: ${srcAnalysis.serviceFiles}`);
console.log(`  工具文件: ${srcAnalysis.utilFiles}`);

// 显示大文件
if (srcAnalysis.largeFiles.length > 0) {
  console.log('\n🔍 大文件分析 (>50KB):');
  srcAnalysis.largeFiles
    .sort((a, b) => b.size - a.size)
    .slice(0, 10)
    .forEach((file, index) => {
      console.log(`  ${index + 1}. ${file.path} - ${file.sizeKB} KB`);
    });
}

// 分析智能体文件
console.log('\n🤖 智能体文件分析:');
const agentFiles = [
  'src/agents/xiaoai/XiaoaiAgentImpl.ts',
  'src/agents/xiaoke/XiaokeAgentImpl.ts',
  'src/agents/laoke/LaokeAgentImpl.ts',
  'src/agents/soer/SoerAgentImpl.ts',
  'src/agents/AgentCoordinator.ts',
  'src/agents/AgentManager.ts'
];

let totalAgentSize = 0;
agentFiles.forEach(filePath => {
  try {
    const stats = fs.statSync(filePath);
    const sizeKB = (stats.size / 1024).toFixed(2);
    totalAgentSize += stats.size;
    console.log(`  ${path.basename(filePath)}: ${sizeKB} KB`);
  } catch (error) {
    console.log(`  ${path.basename(filePath)}: 文件不存在`);
  }
});

console.log(`  智能体总大小: ${(totalAgentSize / 1024).toFixed(2)} KB`);

// 内存使用建议
console.log('\n💡 内存优化建议:');

const currentMemory = process.memoryUsage();
const memoryIncrease = currentMemory.heapUsed - initialMemory.heapUsed;

console.log(`  分析过程内存增长: ${(memoryIncrease / 1024).toFixed(2)} KB`);

if (srcAnalysis.largeFiles.length > 5) {
  console.log('  ⚠️  发现多个大文件，建议进行代码分割');
}

if (srcAnalysis.componentFiles > 100) {
  console.log('  ⚠️  组件数量较多，建议使用懒加载');
}

if (totalAgentSize > 200 * 1024) {
  console.log('  ⚠️  智能体文件较大，建议优化算法复杂度');
}

// 生成内存优化报告
const report = {
  timestamp: new Date().toISOString(),
  initialMemory: {
    rss: (initialMemory.rss / 1024 / 1024).toFixed(2) + ' MB',
    heapTotal: (initialMemory.heapTotal / 1024 / 1024).toFixed(2) + ' MB',
    heapUsed: (initialMemory.heapUsed / 1024 / 1024).toFixed(2) + ' MB'
  },
  fileAnalysis: {
    totalFiles: srcAnalysis.totalFiles,
    totalSizeMB: (srcAnalysis.totalSize / 1024 / 1024).toFixed(2),
    componentFiles: srcAnalysis.componentFiles,
    serviceFiles: srcAnalysis.serviceFiles,
    utilFiles: srcAnalysis.utilFiles
  },
  largeFiles: srcAnalysis.largeFiles.slice(0, 10),
  agentFiles: {
    totalSizeKB: (totalAgentSize / 1024).toFixed(2),
    files: agentFiles.length
  },
  recommendations: []
};

// 添加建议
if (srcAnalysis.largeFiles.length > 5) {
  report.recommendations.push('进行代码分割以减少大文件');
}
if (srcAnalysis.componentFiles > 100) {
  report.recommendations.push('使用懒加载优化组件加载');
}
if (totalAgentSize > 200 * 1024) {
  report.recommendations.push('优化智能体算法复杂度');
}

// 保存报告
try {
  fs.writeFileSync('memory-analysis-report.json', JSON.stringify(report, null, 2));
  console.log('\n📄 内存分析报告已保存到: memory-analysis-report.json');
} catch (error) {
  console.warn('⚠️  无法保存报告文件');
}

console.log('\n✅ 内存分析完成！');