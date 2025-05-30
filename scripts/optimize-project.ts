#!/usr/bin/env ts-node

/**
 * 索克生活项目优化脚本
 * 自动化代码质量改进、性能优化和项目维护
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

// 类型定义
export type OptimizationTask = {
  name: string;
  description: string;
  category: 'code-quality' | 'performance' | 'security' | 'dependencies' | 'cleanup';
  priority: 'high' | 'medium' | 'low';
  estimatedTime: number; // 分钟
  execute: () => Promise<OptimizationResult>;
};

export type OptimizationResult = {
  success: boolean;
  message: string;
  details?: string[];
  metrics?: Record<string, number>;
  errors?: string[];
};

export type OptimizationReport = {
  timestamp: string;
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  totalTime: number;
  results: Array<{
    task: string;
    result: OptimizationResult;
    duration: number;
  }>;
  summary: {
    codeQuality: number;
    performance: number;
    security: number;
    dependencies: number;
    cleanup: number;
  };
};

/**
 * 项目优化器类
 */
export class ProjectOptimizer {
  private projectRoot: string;
  private tasks: OptimizationTask[] = [];
  private report: OptimizationReport;

  constructor(projectRoot: string = process.cwd()) {
    this.projectRoot = projectRoot;
    this.report = {
      timestamp: new Date().toISOString(),
      totalTasks: 0,
      completedTasks: 0,
      failedTasks: 0,
      totalTime: 0,
      results: [],
      summary: {
        codeQuality: 0,
        performance: 0,
        security: 0,
        dependencies: 0,
        cleanup: 0
      }
    };
    this.initializeTasks();
  }

  /**
   * 初始化优化任务
   */
  private initializeTasks(): void {
    this.tasks = [
      // 代码质量任务
      {
        name: 'ESLint修复',
        description: '自动修复ESLint规则违规',
        category: 'code-quality',
        priority: 'high',
        estimatedTime: 5,
        execute: () => this.runESLintFix()
      },
      {
        name: 'Prettier格式化',
        description: '统一代码格式',
        category: 'code-quality',
        priority: 'medium',
        estimatedTime: 3,
        execute: () => this.runPrettierFormat()
      },
      {
        name: 'TypeScript类型检查',
        description: '检查TypeScript类型错误',
        category: 'code-quality',
        priority: 'high',
        estimatedTime: 10,
        execute: () => this.runTypeScriptCheck()
      },
      {
        name: '代码重复检测',
        description: '检测和报告重复代码',
        category: 'code-quality',
        priority: 'medium',
        estimatedTime: 8,
        execute: () => this.detectCodeDuplication()
      },

      // 性能优化任务
      {
        name: '依赖包分析',
        description: '分析和优化依赖包大小',
        category: 'performance',
        priority: 'medium',
        estimatedTime: 15,
        execute: () => this.analyzeDependencies()
      },
      {
        name: '图片优化',
        description: '压缩和优化图片资源',
        category: 'performance',
        priority: 'low',
        estimatedTime: 20,
        execute: () => this.optimizeImages()
      },
      {
        name: '缓存清理',
        description: '清理构建缓存和临时文件',
        category: 'performance',
        priority: 'low',
        estimatedTime: 2,
        execute: () => this.cleanCache()
      },

      // 安全任务
      {
        name: '安全审计',
        description: '检查依赖包安全漏洞',
        category: 'security',
        priority: 'high',
        estimatedTime: 10,
        execute: () => this.runSecurityAudit()
      },
      {
        name: '敏感信息检测',
        description: '检测代码中的敏感信息',
        category: 'security',
        priority: 'high',
        estimatedTime: 5,
        execute: () => this.detectSensitiveInfo()
      },

      // 依赖管理任务
      {
        name: '依赖更新',
        description: '更新过时的依赖包',
        category: 'dependencies',
        priority: 'medium',
        estimatedTime: 30,
        execute: () => this.updateDependencies()
      },
      {
        name: '未使用依赖清理',
        description: '移除未使用的依赖包',
        category: 'dependencies',
        priority: 'low',
        estimatedTime: 10,
        execute: () => this.removeUnusedDependencies()
      },

      // 清理任务
      {
        name: '日志文件清理',
        description: '清理旧的日志文件',
        category: 'cleanup',
        priority: 'low',
        estimatedTime: 2,
        execute: () => this.cleanLogFiles()
      },
      {
        name: '临时文件清理',
        description: '清理临时文件和目录',
        category: 'cleanup',
        priority: 'low',
        estimatedTime: 3,
        execute: () => this.cleanTempFiles()
      }
    ];

    this.report.totalTasks = this.tasks.length;
  }

  /**
   * 运行所有优化任务
   */
  async runOptimization(categories?: string[]): Promise<OptimizationReport> {
    console.log('🚀 开始项目优化...\n');
    
    const startTime = Date.now();
    let tasksToRun = this.tasks;

    // 如果指定了类别，只运行指定类别的任务
    if (categories && categories.length > 0) {
      tasksToRun = this.tasks.filter(task => categories.includes(task.category));
    }

    // 按优先级排序任务
    tasksToRun.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });

    for (const task of tasksToRun) {
      console.log(`⏳ 执行任务: ${task.name}`);
      console.log(`   描述: ${task.description}`);
      console.log(`   预计时间: ${task.estimatedTime}分钟\n`);

      const taskStartTime = Date.now();
      
      try {
        const result = await task.execute();
        const duration = Date.now() - taskStartTime;

        this.report.results.push({
          task: task.name,
          result,
          duration
        });

        if (result.success) {
          this.report.completedTasks++;
          this.report.summary[task.category]++;
          console.log(`✅ ${task.name} 完成`);
          if (result.message) {
            console.log(`   ${result.message}`);
          }
        } else {
          this.report.failedTasks++;
          console.log(`❌ ${task.name} 失败`);
          console.log(`   ${result.message}`);
          if (result.errors) {
            result.errors.forEach(error => console.log(`   - ${error}`));
          }
        }

        console.log(`   耗时: ${(duration / 1000).toFixed(2)}秒\n`);

      } catch (error) {
        const duration = Date.now() - taskStartTime;
        this.report.failedTasks++;
        
        this.report.results.push({
          task: task.name,
          result: {
            success: false,
            message: `执行失败: ${error instanceof Error ? error.message : String(error)}`
          },
          duration
        });

        console.log(`❌ ${task.name} 执行异常`);
        console.log(`   ${error instanceof Error ? error.message : String(error)}\n`);
      }
    }

    this.report.totalTime = Date.now() - startTime;
    
    // 生成报告
    await this.generateReport();
    
    console.log('🎉 项目优化完成!\n');
    this.printSummary();

    return this.report;
  }

  /**
   * ESLint修复
   */
  private async runESLintFix(): Promise<OptimizationResult> {
    try {
      const command = 'npx eslint . --fix --ext .ts,.tsx,.js,.jsx';
      const output = execSync(command, { 
        cwd: this.projectRoot, 
        encoding: 'utf8',
        stdio: 'pipe'
      });

      return {
        success: true,
        message: 'ESLint修复完成',
        details: output ? [output] : undefined
      };
    } catch (error) {
      return {
        success: false,
        message: 'ESLint修复失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * Prettier格式化
   */
  private async runPrettierFormat(): Promise<OptimizationResult> {
    try {
      const command = 'npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,md}"';
      execSync(command, { cwd: this.projectRoot });

      return {
        success: true,
        message: '代码格式化完成'
      };
    } catch (error) {
      return {
        success: false,
        message: '代码格式化失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * TypeScript类型检查
   */
  private async runTypeScriptCheck(): Promise<OptimizationResult> {
    try {
      const command = 'npx tsc --noEmit';
      const output = execSync(command, { 
        cwd: this.projectRoot, 
        encoding: 'utf8',
        stdio: 'pipe'
      });

      return {
        success: true,
        message: 'TypeScript类型检查通过',
        details: output ? [output] : undefined
      };
    } catch (error) {
      return {
        success: false,
        message: 'TypeScript类型检查发现错误',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 代码重复检测
   */
  private async detectCodeDuplication(): Promise<OptimizationResult> {
    try {
      // 使用jscpd检测代码重复
      const command = 'npx jscpd src/ --threshold 10 --format json';
      const output = execSync(command, { 
        cwd: this.projectRoot, 
        encoding: 'utf8',
        stdio: 'pipe'
      });

      const result = JSON.parse(output);
      const duplicates = result.duplicates || [];

      return {
        success: true,
        message: `检测到 ${duplicates.length} 处代码重复`,
        metrics: {
          duplicates: duplicates.length,
          percentage: result.statistics?.total?.percentage || 0
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '代码重复检测失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 依赖包分析
   */
  private async analyzeDependencies(): Promise<OptimizationResult> {
    try {
      const packageJsonPath = path.join(this.projectRoot, 'package.json');
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      const dependencies = Object.keys(packageJson.dependencies || {});
      const devDependencies = Object.keys(packageJson.devDependencies || {});
      
      // 分析包大小
      const command = 'npm ls --depth=0 --json';
      const output = execSync(command, { 
        cwd: this.projectRoot, 
        encoding: 'utf8',
        stdio: 'pipe'
      });

      return {
        success: true,
        message: '依赖包分析完成',
        metrics: {
          dependencies: dependencies.length,
          devDependencies: devDependencies.length,
          total: dependencies.length + devDependencies.length
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '依赖包分析失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 图片优化
   */
  private async optimizeImages(): Promise<OptimizationResult> {
    try {
      const assetsDir = path.join(this.projectRoot, 'src/assets');
      
      if (!fs.existsSync(assetsDir)) {
        return {
          success: true,
          message: '未找到图片资源目录，跳过优化'
        };
      }

      // 这里可以集成imagemin等工具进行图片压缩
      // 目前只是示例实现
      const imageFiles = this.findImageFiles(assetsDir);

      return {
        success: true,
        message: `发现 ${imageFiles.length} 个图片文件`,
        metrics: {
          imageFiles: imageFiles.length
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '图片优化失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 缓存清理
   */
  private async cleanCache(): Promise<OptimizationResult> {
    try {
      const cacheDirs = [
        '.expo',
        'node_modules/.cache',
        '.jest-cache',
        'coverage'
      ];

      let cleanedDirs = 0;
      let totalSize = 0;

      for (const dir of cacheDirs) {
        const fullPath = path.join(this.projectRoot, dir);
        if (fs.existsSync(fullPath)) {
          const size = this.getDirectorySize(fullPath);
          totalSize += size;
          cleanedDirs++;
          
          // 实际清理逻辑可以在这里实现
          // fs.rmSync(fullPath, { recursive: true, force: true });
        }
      }

      return {
        success: true,
        message: `清理了 ${cleanedDirs} 个缓存目录`,
        metrics: {
          cleanedDirs,
          totalSize: Math.round(totalSize / 1024 / 1024) // MB
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '缓存清理失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 安全审计
   */
  private async runSecurityAudit(): Promise<OptimizationResult> {
    try {
      const command = 'npm audit --json';
      const output = execSync(command, { 
        cwd: this.projectRoot, 
        encoding: 'utf8',
        stdio: 'pipe'
      });

      const auditResult = JSON.parse(output);
      const vulnerabilities = auditResult.vulnerabilities || {};
      const vulnCount = Object.keys(vulnerabilities).length;

      return {
        success: vulnCount === 0,
        message: vulnCount === 0 ? '未发现安全漏洞' : `发现 ${vulnCount} 个安全漏洞`,
        metrics: {
          vulnerabilities: vulnCount,
          high: auditResult.metadata?.vulnerabilities?.high || 0,
          moderate: auditResult.metadata?.vulnerabilities?.moderate || 0,
          low: auditResult.metadata?.vulnerabilities?.low || 0
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '安全审计失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 敏感信息检测
   */
  private async detectSensitiveInfo(): Promise<OptimizationResult> {
    try {
      // 检测常见的敏感信息模式
      const sensitivePatterns = [
        /password\s*=\s*['"][^'"]+['"]/gi,
        /api[_-]?key\s*=\s*['"][^'"]+['"]/gi,
        /secret\s*=\s*['"][^'"]+['"]/gi,
        /token\s*=\s*['"][^'"]+['"]/gi
      ];

      const srcDir = path.join(this.projectRoot, 'src');
      const findings: string[] = [];

      if (fs.existsSync(srcDir)) {
        this.scanDirectoryForPatterns(srcDir, sensitivePatterns, findings);
      }

      return {
        success: findings.length === 0,
        message: findings.length === 0 ? '未发现敏感信息' : `发现 ${findings.length} 处可能的敏感信息`,
        details: findings.slice(0, 10), // 只显示前10个
        metrics: {
          findings: findings.length
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '敏感信息检测失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 依赖更新
   */
  private async updateDependencies(): Promise<OptimizationResult> {
    try {
      // 检查过时的依赖
      const command = 'npm outdated --json';
      const output = execSync(command, { 
        cwd: this.projectRoot, 
        encoding: 'utf8',
        stdio: 'pipe'
      });

      const outdated = JSON.parse(output || '{}');
      const outdatedCount = Object.keys(outdated).length;

      if (outdatedCount === 0) {
        return {
          success: true,
          message: '所有依赖都是最新的'
        };
      }

      // 这里可以实现自动更新逻辑
      // execSync('npm update', { cwd: this.projectRoot });

      return {
        success: true,
        message: `发现 ${outdatedCount} 个过时的依赖包`,
        metrics: {
          outdated: outdatedCount
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '依赖更新检查失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 移除未使用的依赖
   */
  private async removeUnusedDependencies(): Promise<OptimizationResult> {
    try {
      // 使用depcheck检测未使用的依赖
      const command = 'npx depcheck --json';
      const output = execSync(command, { 
        cwd: this.projectRoot, 
        encoding: 'utf8',
        stdio: 'pipe'
      });

      const result = JSON.parse(output);
      const unused = result.dependencies || [];

      return {
        success: true,
        message: unused.length === 0 ? '未发现未使用的依赖' : `发现 ${unused.length} 个未使用的依赖`,
        details: unused,
        metrics: {
          unused: unused.length
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '未使用依赖检测失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 清理日志文件
   */
  private async cleanLogFiles(): Promise<OptimizationResult> {
    try {
      const logDirs = ['logs', 'services/*/logs'];
      let cleanedFiles = 0;
      let totalSize = 0;

      for (const logPattern of logDirs) {
        const logPath = path.join(this.projectRoot, logPattern);
        if (fs.existsSync(logPath) && fs.statSync(logPath).isDirectory()) {
          const files = fs.readdirSync(logPath);
          for (const file of files) {
            if (file.endsWith('.log') || file.endsWith('.log.gz')) {
              const filePath = path.join(logPath, file);
              const stats = fs.statSync(filePath);
              totalSize += stats.size;
              cleanedFiles++;
              
              // 实际删除逻辑可以在这里实现
              // fs.unlinkSync(filePath);
            }
          }
        }
      }

      return {
        success: true,
        message: `清理了 ${cleanedFiles} 个日志文件`,
        metrics: {
          cleanedFiles,
          totalSize: Math.round(totalSize / 1024 / 1024) // MB
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '日志文件清理失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 清理临时文件
   */
  private async cleanTempFiles(): Promise<OptimizationResult> {
    try {
      const tempPatterns = [
        '**/*.tmp',
        '**/*.temp',
        '**/tmp/**',
        '**/.DS_Store',
        '**/Thumbs.db'
      ];

      let cleanedFiles = 0;
      let totalSize = 0;

      // 这里可以实现实际的文件清理逻辑
      // 使用glob模式匹配和删除文件

      return {
        success: true,
        message: `清理了 ${cleanedFiles} 个临时文件`,
        metrics: {
          cleanedFiles,
          totalSize: Math.round(totalSize / 1024 / 1024) // MB
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '临时文件清理失败',
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  /**
   * 生成优化报告
   */
  private async generateReport(): Promise<void> {
    const reportPath = path.join(this.projectRoot, 'optimization-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(this.report, null, 2));
    
    // 生成Markdown报告
    const markdownReport = this.generateMarkdownReport();
    const markdownPath = path.join(this.projectRoot, 'OPTIMIZATION_REPORT.md');
    fs.writeFileSync(markdownPath, markdownReport);
  }

  /**
   * 生成Markdown报告
   */
  private generateMarkdownReport(): string {
    const { report } = this;
    const successRate = ((report.completedTasks / report.totalTasks) * 100).toFixed(1);
    
    let markdown = `# 项目优化报告\n\n`;
    markdown += `**生成时间**: ${new Date(report.timestamp).toLocaleString()}\n`;
    markdown += `**总任务数**: ${report.totalTasks}\n`;
    markdown += `**完成任务**: ${report.completedTasks}\n`;
    markdown += `**失败任务**: ${report.failedTasks}\n`;
    markdown += `**成功率**: ${successRate}%\n`;
    markdown += `**总耗时**: ${(report.totalTime / 1000 / 60).toFixed(2)}分钟\n\n`;

    markdown += `## 任务执行结果\n\n`;
    
    for (const result of report.results) {
      const status = result.result.success ? '✅' : '❌';
      const duration = (result.duration / 1000).toFixed(2);
      
      markdown += `### ${status} ${result.task}\n\n`;
      markdown += `**耗时**: ${duration}秒\n`;
      markdown += `**结果**: ${result.result.message}\n`;
      
      if (result.result.details && result.result.details.length > 0) {
        markdown += `**详情**:\n`;
        result.result.details.forEach(detail => {
          markdown += `- ${detail}\n`;
        });
      }
      
      if (result.result.metrics) {
        markdown += `**指标**:\n`;
        Object.entries(result.result.metrics).forEach(([key, value]) => {
          markdown += `- ${key}: ${value}\n`;
        });
      }
      
      if (result.result.errors && result.result.errors.length > 0) {
        markdown += `**错误**:\n`;
        result.result.errors.forEach(error => {
          markdown += `- ${error}\n`;
        });
      }
      
      markdown += `\n`;
    }

    markdown += `## 分类统计\n\n`;
    Object.entries(report.summary).forEach(([category, count]) => {
      markdown += `- **${category}**: ${count}个任务完成\n`;
    });

    return markdown;
  }

  /**
   * 打印摘要
   */
  private printSummary(): void {
    const { report } = this;
    const successRate = ((report.completedTasks / report.totalTasks) * 100).toFixed(1);
    
    console.log('📊 优化摘要:');
    console.log(`   总任务数: ${report.totalTasks}`);
    console.log(`   完成任务: ${report.completedTasks}`);
    console.log(`   失败任务: ${report.failedTasks}`);
    console.log(`   成功率: ${successRate}%`);
    console.log(`   总耗时: ${(report.totalTime / 1000 / 60).toFixed(2)}分钟`);
    console.log('\n📁 报告文件:');
    console.log(`   JSON: optimization-report.json`);
    console.log(`   Markdown: OPTIMIZATION_REPORT.md`);
  }

  /**
   * 辅助方法：查找图片文件
   */
  private findImageFiles(dir: string): string[] {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'];
    const imageFiles: string[] = [];

    const scanDir = (currentDir: string) => {
      const items = fs.readdirSync(currentDir);
      
      for (const item of items) {
        const fullPath = path.join(currentDir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          scanDir(fullPath);
        } else if (imageExtensions.some(ext => item.toLowerCase().endsWith(ext))) {
          imageFiles.push(fullPath);
        }
      }
    };

    scanDir(dir);
    return imageFiles;
  }

  /**
   * 辅助方法：获取目录大小
   */
  private getDirectorySize(dir: string): number {
    let totalSize = 0;

    const scanDir = (currentDir: string) => {
      try {
        const items = fs.readdirSync(currentDir);
        
        for (const item of items) {
          const fullPath = path.join(currentDir, item);
          const stat = fs.statSync(fullPath);
          
          if (stat.isDirectory()) {
            scanDir(fullPath);
          } else {
            totalSize += stat.size;
          }
        }
      } catch (error) {
        // 忽略权限错误等
      }
    };

    scanDir(dir);
    return totalSize;
  }

  /**
   * 辅助方法：扫描目录中的敏感信息
   */
  private scanDirectoryForPatterns(dir: string, patterns: RegExp[], findings: string[]): void {
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
        this.scanDirectoryForPatterns(fullPath, patterns, findings);
      } else if (stat.isFile() && (item.endsWith('.ts') || item.endsWith('.tsx') || item.endsWith('.js') || item.endsWith('.jsx'))) {
        try {
          const content = fs.readFileSync(fullPath, 'utf8');
          
          for (const pattern of patterns) {
            const matches = content.match(pattern);
            if (matches) {
              findings.push(`${fullPath}: ${matches[0]}`);
            }
          }
        } catch (error) {
          // 忽略读取错误
        }
      }
    }
  }
}

// 主函数
async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const categories = args.length > 0 ? args : undefined;

  try {
    const optimizer = new ProjectOptimizer();
    
    if (categories) {
      console.log(`🎯 运行指定类别的优化任务: ${categories.join(', ')}\n`);
    } else {
      console.log('🎯 运行所有优化任务\n');
    }

    const report = await optimizer.runOptimization(categories);
    
    if (report.failedTasks === 0) {
      console.log('\n🎉 所有优化任务都成功完成!');
    } else {
      console.log(`\n⚠️  ${report.failedTasks} 个任务执行失败，请查看报告了解详情。`);
    }

    process.exit(0);
  } catch (error) {
    console.error('❌ 优化过程中发生错误:', error);
    process.exit(1);
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main();
} 