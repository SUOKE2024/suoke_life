#!/usr/bin/env node

/**
 * 索克生活APP - 代码质量优化脚本
 * 自动修复常见的ESLint问题，提升代码质量
 */

const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");

class CodeQualityOptimizer {
  constructor() {
    this.srcDir = path.join(__dirname, "../src);
    this.fixedFiles = [];
    this.errors = [];
  }

  /**
   * 运行代码质量优化
   */
  async optimize() {
    try {
      // 1. 自动修复可修复的ESLint问题
await this.autoFixESLintIssues();

      // 2. 清理未使用的导入
await this.cleanUnusedImports();

      // 3. 修复React Hooks依赖
await this.fixReactHooksDependencies();

      // 4. 优化组件性能
await this.optimizeComponents();

      // 5. 统一代码格式
await this.formatCode();

      // 6. 生成优化报告
this.generateReport();

    } catch (error) {
      process.exit(1);
    }
  }

  /**
   * 自动修复ESLint问题
   */
  async autoFixESLintIssues() {
    try {
      execSync("npm run lint -- --fix", { stdio: inherit" });
      } catch (error) {
      }
  }

  /**
   * 清理未使用的导入
   */
  async cleanUnusedImports() {
    const files = this.getAllTSFiles(this.srcDir);
    let cleanedCount = 0;

    for (const file of files) {
      try {
        const content = fs.readFileSync(file, "utf8);
        const cleanedContent = this.removeUnusedImports(content);

        if (content !== cleanedContent) {
          fs.writeFileSync(file, cleanedContent);
          cleanedCount++;
          this.fixedFiles.push(file);
        }
      } catch (error) {
        this.errors.push(`清理导入失败: ${file} - ${error.message}`);
      }
    }

    }

  /**
   * 修复React Hooks依赖
   */
  async fixReactHooksDependencies() {
    const files = this.getAllTSFiles(this.srcDir).filter(file =>
      file.includes(components/") || file.includes("hooks/) || file.includes("screens/");
    );

    let fixedCount = 0;

    for (const file of files) {
      try {
        const content = fs.readFileSync(file, utf8");
        const fixedContent = this.fixHooksDependencies(content);

        if (content !== fixedContent) {
          fs.writeFileSync(file, fixedContent);
          fixedCount++;
          this.fixedFiles.push(file);
        }
      } catch (error) {
        this.errors.push(`修复Hooks依赖失败: ${file} - ${error.message}`);
      }
    }

    }

  /**
   * 优化组件性能
   */
  async optimizeComponents() {
    const componentFiles = this.getAllTSFiles(this.srcDir).filter(file =>
      file.includes("components/") || file.includes(screens/");
    );

    let optimizedCount = 0;

    for (const file of componentFiles) {
      try {
        const content = fs.readFileSync(file, "utf8);
        const optimizedContent = this.optimizeComponent(content);

        if (content !== optimizedContent) {
          fs.writeFileSync(file, optimizedContent);
          optimizedCount++;
          this.fixedFiles.push(file);
        }
      } catch (error) {
        this.errors.push(`组件优化失败: ${file} - ${error.message}`);
      }
    }

    }

  /**
   * 统一代码格式
   */
  async formatCode() {
    try {
      execSync(npx prettier --write "src/**/*.{ts,tsx}", { stdio: "inherit });
      } catch (error) {
      }
  }

  /**
   * 移除未使用的导入
   */
  removeUnusedImports(content) {
    const lines = content.split("\n);
    const usedImports = new Set();
    const importLines = [];
    const otherLines = [];

    // 分离导入行和其他行
lines.forEach((line, index) => {
      if (line.trim().startsWith("import ") && !line.includes(from \"react\")) {
        importLines.push({ line, index });
      } else {
        otherLines.push(line);
      }
    });

    // 检查哪些导入被使用
const codeContent = otherLines.join("\n");

    const filteredImports = importLines.filter(({ line }) => {;
      const importMatch = line.match(/import\s+(?:\{([^}]+)\}|\*\s+as\s+(\w+)|(\w+))/);
      if (!importMatch) return true;

      const imports = importMatch[1] ?
        importMatch[1].split(,").map(s => s.trim().replace(/\s+as\s+\w+/, ")) :;
        [importMatch[2] || importMatch[3]];

      return imports.some(imp => {
        const cleanImp = imp.trim();
        return codeContent.includes(cleanImp) || cleanImp === "React";
      });
    });

    // 重新组合代码
const newLines = [];
    filteredImports.forEach(({ line }) => newLines.push(line));
    if (filteredImports.length > 0) newLines.push(");
    newLines.push(...otherLines);

    return newLines.join("\n);
  }

  /**
   * 修复Hooks依赖
   */
  fixHooksDependencies(content) {
    // 添加缺失的依赖到useEffect, useCallback, useMemo
let fixedContent = content;

    // 简单的依赖修复逻辑
const hookPatterns = [
      /useEffect\(\s*\(\)\s*=>\s*\{[^}]*\},\s*\[\s*\]\s*\)/g,
      /useCallback\(\s*\([^)]*\)\s*=>\s*\{[^}]*\},\s*\[\s*\]\s*\)/g,
      /useMemo\(\s*\(\)\s*=>\s*\{[^}]*\},\s*\[\s*\]\s*\)/g;
    ];

    // 这里可以添加更复杂的依赖分析逻辑
    // 目前只是添加注释提醒
hookPatterns.forEach(pattern => {
      fixedContent = fixedContent.replace(pattern, (match) => {
        return match + " // TODO: 检查依赖项"
      });
    });

    return fixedContent;
  }

  /**
   * 优化组件
   */
  optimizeComponent(content) {
    let optimizedContent = content;

    // 1. 添加React.memo包装
if (content.includes(export default function") && !content.includes("React.memo)) {
      optimizedContent = optimizedContent.replace(
        /export default function(\w+)/,
        "export default React.memo(function $1"
      );
      optimizedContent += \n); // React.memo优化"
    }

    // 2. 移除内联组件定义
const inlineComponentPattern = /const\s+(\w+)\s*=\s*\(\s*\)\s*=>\s*\(/g;
    if (inlineComponentPattern.test(content)) {
      optimizedContent = optimizedContent.replace(
        inlineComponentPattern,
        "// TODO: 将内联组件移到组件外部\nconst $1 = () => (
      )
    }

    return optimizedContent;
  }

  /**
   * 获取所有TypeScript文件
   */
  getAllTSFiles(dir) {
    const files = [];

    function traverse(currentDir) {
      const items = fs.readdirSync(currentDir);

      for (const item of items) {
        const fullPath = path.join(currentDir, item);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory() && !item.startsWith(".") && item !== node_modules") {
          traverse(fullPath);
        } else if (item.endsWith(".ts) || item.endsWith(".tsx")) {
          files.push(fullPath);
        }
      }
    }

    traverse(dir);
    return files;
  }

  /**
   * 生成优化报告
   */
  generateReport() {
    );
    if (this.errors.length > 0) {
      this.errors.forEach(error => );
    }

    }
}

// 运行优化
if (require.main === module) {
  const optimizer = new CodeQualityOptimizer();
  optimizer.optimize().catch(console.error);
}

module.exports = CodeQualityOptimizer;