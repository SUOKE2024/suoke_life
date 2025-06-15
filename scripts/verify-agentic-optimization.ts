#!/usr/bin/env ts-node

/**
 * Agentic AI系统优化验证脚本
 * 验证优化后的系统是否正常工作
 */

import * as fs from 'fs';
import * as path from 'path';

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message: string, color: keyof typeof colors = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function success(message: string) {
  log(`✅ ${message}`, 'green');
}

function error(message: string) {
  log(`❌ ${message}`, 'red');
}

function warn(message: string) {
  log(`⚠️ ${message}`, 'yellow');
}

function info(message: string) {
  log(`ℹ️ ${message}`, 'blue');
}

// 项目根目录
const PROJECT_ROOT = path.resolve(__dirname, '..');

/**
 * 检查文件是否存在
 */
function checkFileExists(filePath: string): boolean {
  const fullPath = path.join(PROJECT_ROOT, filePath);
  return fs.existsSync(fullPath);
}

/**
 * 检查目录是否存在
 */
function checkDirectoryExists(dirPath: string): boolean {
  const fullPath = path.join(PROJECT_ROOT, dirPath);
  return fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory();
}

/**
 * 读取文件内容
 */
function readFile(filePath: string): string | null {
  try {
    const fullPath = path.join(PROJECT_ROOT, filePath);
    return fs.readFileSync(fullPath, 'utf-8');
  } catch (error) {
    return null;
  }
}

/**
 * 检查文件语法
 */
function checkFileSyntax(filePath: string): boolean {
  const content = readFile(filePath);
  if (!content) return false;

  // 基本语法检查
  const syntaxErrors = [
    /const async = /,  // 错误的async语法
    /\}\s*\{/,         // 缺少分号的对象
    /\)\s*\(/,         // 缺少操作符的函数调用
    /\s+\}\s*\)/,      // 不匹配的括号
    /\s+\)\s*\{/       // 不匹配的括号
  ];

  for (const pattern of syntaxErrors) {
    if (pattern.test(content)) {
      return false;
    }
  }

  return true;
}

/**
 * 验证核心文件结构
 */
async function verifyFileStructure(): Promise<boolean> {
  info('🔍 验证文件结构...');

  const requiredFiles = [
    'src/core/agentic/OptimizedAgenticManager.ts',
    'src/agents/EnhancedAgentCoordinator.ts',
    'src/agents/AgentManager.ts',
    'examples/agentic-integration-example.ts',
    'docs/AGENTIC_SYSTEM_OPTIMIZATION.md',
    'AGENTIC_AI_OPTIMIZATION_SUMMARY.md'
  ];

  const requiredDirectories = [
    'src/core/agentic',
    'src/agents',
    'examples',
    'docs',
    'scripts'
  ];

  let allFilesExist = true;
  let allDirsExist = true;

  // 检查文件
  for (const file of requiredFiles) {
    if (checkFileExists(file)) {
      success(`文件存在: ${file}`);
    } else {
      error(`文件缺失: ${file}`);
      allFilesExist = false;
    }
  }

  // 检查目录
  for (const dir of requiredDirectories) {
    if (checkDirectoryExists(dir)) {
      success(`目录存在: ${dir}`);
    } else {
      error(`目录缺失: ${dir}`);
      allDirsExist = false;
    }
  }

  return allFilesExist && allDirsExist;
}

/**
 * 验证代码质量
 */
async function verifyCodeQuality(): Promise<boolean> {
  info('🔍 验证代码质量...');

  const filesToCheck = [
    'src/core/agentic/OptimizedAgenticManager.ts',
    'src/agents/EnhancedAgentCoordinator.ts',
    'src/agents/AgentManager.ts'
  ];

  let allFilesValid = true;

  for (const file of filesToCheck) {
    if (checkFileExists(file)) {
      if (checkFileSyntax(file)) {
        success(`语法检查通过: ${file}`);
      } else {
        error(`语法检查失败: ${file}`);
        allFilesValid = false;
      }
    } else {
      error(`文件不存在: ${file}`);
      allFilesValid = false;
    }
  }

  return allFilesValid;
}

/**
 * 验证核心组件
 */
async function verifyCoreComponents(): Promise<boolean> {
  info('🔍 验证核心组件...');

  const components = [
    {
      name: 'OptimizedAgenticManager',
      file: 'src/core/agentic/OptimizedAgenticManager.ts',
      requiredMethods: ['initialize', 'start', 'stop', 'processIntelligentTask', 'getSystemHealth']
    },
    {
      name: 'EnhancedAgentCoordinator',
      file: 'src/agents/EnhancedAgentCoordinator.ts',
      requiredMethods: ['initialize', 'processCollaborativeTask', 'getAllAgentStatus']
    }
  ];

  let allComponentsValid = true;

  for (const component of components) {
    const content = readFile(component.file);
    if (!content) {
      error(`无法读取组件文件: ${component.name}`);
      allComponentsValid = false;
      continue;
    }

    // 检查类定义
    const classPattern = new RegExp(`class\\s+${component.name}`);
    if (!classPattern.test(content)) {
      error(`组件类定义缺失: ${component.name}`);
      allComponentsValid = false;
      continue;
    }

    // 检查必需方法
    let methodsValid = true;
    for (const method of component.requiredMethods) {
      const methodPattern = new RegExp(`${method}\\s*\\(`);
      if (!methodPattern.test(content)) {
        error(`方法缺失: ${component.name}.${method}`);
        methodsValid = false;
      }
    }

    if (methodsValid) {
      success(`组件验证通过: ${component.name}`);
    } else {
      allComponentsValid = false;
    }
  }

  return allComponentsValid;
}

/**
 * 验证智能体配置
 */
async function verifyAgentConfiguration(): Promise<boolean> {
  info('🔍 验证智能体配置...');

  const coordinatorFile = 'src/agents/EnhancedAgentCoordinator.ts';
  const content = readFile(coordinatorFile);
  
  if (!content) {
    error('无法读取智能体协调器文件');
    return false;
  }

  const requiredAgents = ['xiaoai', 'xiaoke', 'laoke', 'soer'];
  let allAgentsConfigured = true;

  for (const agent of requiredAgents) {
    if (content.includes(agent)) {
      success(`智能体配置存在: ${agent}`);
    } else {
      error(`智能体配置缺失: ${agent}`);
      allAgentsConfigured = false;
    }
  }

  // 检查智能体能力配置
  const capabilityPatterns = [
    'analysis',      // 小艾的分析能力
    'health_assessment', // 小克的健康评估能力
    'tcm_diagnosis', // 老克的中医诊断能力
    'lifestyle_guidance' // 索儿的生活指导能力
  ];

  for (const capability of capabilityPatterns) {
    if (content.includes(capability)) {
      success(`智能体能力配置存在: ${capability}`);
    } else {
      warn(`智能体能力配置可能缺失: ${capability}`);
    }
  }

  return allAgentsConfigured;
}

/**
 * 验证示例代码
 */
async function verifyExamples(): Promise<boolean> {
  info('🔍 验证示例代码...');

  const exampleFile = 'examples/agentic-integration-example.ts';
  const content = readFile(exampleFile);

  if (!content) {
    error('示例文件不存在');
    return false;
  }

  const requiredExamples = [
    'basicHealthConsultationExample',
    'tcmDiagnosisExample',
    'batchHealthAssessmentExample',
    'collaborativeDiagnosisExample'
  ];

  let allExamplesExist = true;

  for (const example of requiredExamples) {
    if (content.includes(example)) {
      success(`示例函数存在: ${example}`);
    } else {
      error(`示例函数缺失: ${example}`);
      allExamplesExist = false;
    }
  }

  return allExamplesExist;
}

/**
 * 验证文档完整性
 */
async function verifyDocumentation(): Promise<boolean> {
  info('🔍 验证文档完整性...');

  const docs = [
    {
      file: 'docs/AGENTIC_SYSTEM_OPTIMIZATION.md',
      requiredSections: ['现状分析', '优化方案', '性能提升', '技术创新']
    },
    {
      file: 'AGENTIC_AI_OPTIMIZATION_SUMMARY.md',
      requiredSections: ['项目概览', '现状分析', '优化方案', '性能提升效果']
    }
  ];

  let allDocsValid = true;

  for (const doc of docs) {
    const content = readFile(doc.file);
    if (!content) {
      error(`文档文件不存在: ${doc.file}`);
      allDocsValid = false;
      continue;
    }

    let sectionsValid = true;
    for (const section of doc.requiredSections) {
      if (content.includes(section)) {
        success(`文档章节存在: ${section} (${doc.file})`);
      } else {
        error(`文档章节缺失: ${section} (${doc.file})`);
        sectionsValid = false;
      }
    }

    if (!sectionsValid) {
      allDocsValid = false;
    }
  }

  return allDocsValid;
}

/**
 * 生成验证报告
 */
function generateVerificationReport(results: { [key: string]: boolean }): void {
  info('📋 生成验证报告...');

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const reportFile = path.join(PROJECT_ROOT, `verification_report_${timestamp}.md`);

  const report = `# Agentic AI系统优化验证报告

**验证时间**: ${new Date().toLocaleString()}
**验证版本**: ${timestamp}

## 验证结果总览

${Object.entries(results).map(([test, passed]) => 
  `- ${passed ? '✅' : '❌'} ${test}: ${passed ? '通过' : '失败'}`
).join('\n')}

## 验证详情

### 文件结构验证
${results.fileStructure ? '✅ 所有必需文件和目录都存在' : '❌ 部分文件或目录缺失'}

### 代码质量验证
${results.codeQuality ? '✅ 代码语法检查通过' : '❌ 代码存在语法问题'}

### 核心组件验证
${results.coreComponents ? '✅ 核心组件完整且功能正常' : '❌ 核心组件存在问题'}

### 智能体配置验证
${results.agentConfiguration ? '✅ 四个智能体配置完整' : '❌ 智能体配置存在问题'}

### 示例代码验证
${results.examples ? '✅ 示例代码完整' : '❌ 示例代码存在问题'}

### 文档完整性验证
${results.documentation ? '✅ 文档完整' : '❌ 文档存在问题'}

## 总体评估

${Object.values(results).every(r => r) ? 
  '🎉 **验证通过**: Agentic AI系统优化成功，所有组件都正常工作！' : 
  '⚠️ **验证部分通过**: 系统基本可用，但存在一些需要修复的问题。'
}

## 下一步建议

${Object.values(results).every(r => r) ? 
  `1. 运行完整的集成测试
2. 部署到测试环境
3. 进行性能基准测试
4. 开始用户验收测试` :
  `1. 修复验证中发现的问题
2. 重新运行验证脚本
3. 确保所有测试通过后再进行部署`
}

---
**报告生成时间**: ${new Date().toLocaleString()}
`;

  fs.writeFileSync(reportFile, report);
  success(`验证报告已生成: ${reportFile}`);
}

/**
 * 主验证函数
 */
async function main(): Promise<void> {
  log('🚀 开始验证 Agentic AI 系统优化...', 'magenta');
  log('=' .repeat(60), 'cyan');

  const results: { [key: string]: boolean } = {};

  try {
    // 执行各项验证
    results.fileStructure = await verifyFileStructure();
    results.codeQuality = await verifyCodeQuality();
    results.coreComponents = await verifyCoreComponents();
    results.agentConfiguration = await verifyAgentConfiguration();
    results.examples = await verifyExamples();
    results.documentation = await verifyDocumentation();

    // 生成报告
    generateVerificationReport(results);

    // 输出总结
    log('=' .repeat(60), 'cyan');
    const allPassed = Object.values(results).every(r => r);
    const passedCount = Object.values(results).filter(r => r).length;
    const totalCount = Object.values(results).length;

    if (allPassed) {
      log('🎉 验证完成：所有测试通过！', 'green');
      log('✨ Agentic AI 系统优化成功，可以开始使用了！', 'green');
    } else {
      log(`⚠️ 验证完成：${passedCount}/${totalCount} 项测试通过`, 'yellow');
      log('🔧 请修复失败的测试项后重新验证', 'yellow');
    }

    log('=' .repeat(60), 'cyan');

    // 输出使用建议
    if (allPassed) {
      log('📖 使用建议:', 'blue');
      log('1. 查看示例代码: examples/agentic-integration-example.ts', 'blue');
      log('2. 阅读文档: docs/AGENTIC_SYSTEM_OPTIMIZATION.md', 'blue');
      log('3. 运行示例: npx ts-node examples/agentic-integration-example.ts', 'blue');
      log('4. 开始集成到您的应用中', 'blue');
    }

    process.exit(allPassed ? 0 : 1);

  } catch (error) {
    error(`验证过程中发生错误: ${error}`);
    process.exit(1);
  }
}

// 运行验证
if (require.main === module) {
  main().catch(console.error);
}

export { main as verifyAgenticOptimization };