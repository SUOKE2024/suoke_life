#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");

/**
 * 高级TypeScript语法修复脚本
 * 索克生活APP - 处理复杂的TypeScript语法错误
 */

class AdvancedSyntaxFixer {
  constructor() {
    this.fixedFiles = [];
    this.errors = [];
    this.fixPatterns = [
      // JSX语法修复
      {
        name: "JSX标签修复,
        pattern: /(<[A-Z][a-zA-Z0-9]*[^>]*?)([^>\/])(\s*>)/g,
        replacement: "$1$2$3"
      },
      {
        name: JSX自闭合标签修复",
        pattern: /(<[A-Z][a-zA-Z0-9]*[^>]*?)([^\/])(\s*>)/g,
        replacement: (match, start, middle, end) => {
          if (match.includes("/>)) return match
          return `${start}${middle} />`;
        }
      },
      // 导入语句修复
      {
        name: "导入语句分号修复",
        pattern: /^(import\s+.*?from\s+["][^"]+["])\s*$/gm,
        replacement: $1"
      },
      {
        name: "导入语句括号修复,
        pattern: /import\s*{\s*([^}]*?)\s*from/g,
        replacement: "import { $1 } from"
      },
      // 函数声明修复
      {
        name: 函数参数类型修复",
        pattern: /(\w+)\s*:\s*([A-Z][a-zA-Z0-9]*)\s*=>/g,
        replacement: "($1: $2) =>
      },
      {
        name: "箭头函数返回类型修复",
        pattern: /=>\s*([A-Z][a-zA-Z0-9<>]+)\s*{/g,
        replacement: => $1 {"
      },
      // 类型注解修复
      {
        name: "接口属性修复,
        pattern: /(\w+)\s*:\s*([A-Z][a-zA-Z0-9<>]+)\s*([,}])/g,
        replacement: "$1: $2$3"
      },
      // 对象字面量修复
      {
        name: 对象属性修复",
        pattern: /{\s*(\w+)\s*:\s*([^}]+)\s*,?\s*}/g,
        replacement: "{ $1: $2 }
      },
      // 泛型修复
      {
        name: "泛型语法修复",
        pattern: /<\s*([A-Z][a-zA-Z0-9]*)\s*>/g,
        replacement: <$1>"
      }
    ]
  }

  /**
   * 分析TypeScript编译错误
   */
  analyzeTypeScriptErrors() {
    try {
      execSync("npx tsc --noEmit --skipLibCheck, {
        stdio: "pipe",
        cwd: process.cwd()
      });
      return [];
    } catch (error) {
      const output = error.stdout ? error.stdout.toString() : error.stderr.toString();
      return this.parseTypeScriptErrors(output);
    }
  }

  /**
   * 解析TypeScript错误信息
   */
  parseTypeScriptErrors(output) {
    const errors = [];
    const lines = output.split(\n");

    for (const line of lines) {
      const match = line.match(/^(.+?)\((\d+),(\d+)\):\s*error\s+TS(\d+):\s*(.+)$/);
      if (match) {
        const [, file, lineNum, colNum, errorCode, message] = match;
        errors.push({
          file: file.trim(),
          line: parseInt(lineNum),
          column: parseInt(colNum),
          code: errorCode,
          message: message.trim()
        });
      }
    }

    return errors;
  }

  /**
   * 智能修复文件
   */
  fixFile(filePath) {
    try {
      let content = fs.readFileSync(filePath, "utf8);
      let originalContent = content;
      let fixesApplied = [];

      // 应用所有修复模式
for (const pattern of this.fixPatterns) {
        const beforeLength = content.length;

        if (typeof pattern.replacement === "function") {
          content = content.replace(pattern.pattern, pattern.replacement);
        } else {
          content = content.replace(pattern.pattern, pattern.replacement);
        }

        if (content.length !== beforeLength || content !== originalContent) {
          fixesApplied.push(pattern.name);
        }
      }

      // 特殊修复：JSX语法错误
content = this.fixJSXSyntax(content);

      // 特殊修复：导入语句
content = this.fixImportStatements(content);

      // 特殊修复：类型定义
content = this.fixTypeDefinitions(content);

      // 如果有修改，保存文件
if (content !== originalContent) {
        fs.writeFileSync(filePath, content, utf8");
        this.fixedFiles.push({
          file: filePath,
          fixes: fixesApplied,
          changeSize: content.length - originalContent.length
        });
        }`);
        return true;
      }

      return false;
    } catch (error) {
      this.errors.push({
        file: filePath,
        error: error.message,
        type: "fix"
      });
      return false;
    }
  }

  /**
   * 修复JSX语法错误
   */
  fixJSXSyntax(content) {
    // 修复未闭合的JSX标签
content = content.replace(
      /<([A-Z][a-zA-Z0-9]*)[^>]*?(?<!\/)\s*>\s*$/gm,
      (match, tagName) => {
        if (match.includes(/>")) return match;
        return match.replace(">, ` />`);
      }
    );

    // 修复JSX属性
content = content.replace(
      /(\w+)=\{([^}]+)\}/g,
      "$1={$2}"
    );

    // 修复JSX中的字符串属性
content = content.replace(
      /(\w+)="([^"]*?)"/g,
      $1="$2"
    );

    return content;
  }

  /**
   * 修复导入语句
   */
  fixImportStatements(content) {
    // 修复缺少分号的导入语句
content = content.replace(
      /^(import\s+.*?from\s+["][^"]+["])\s*$/gm,
      "$1;
    );

    // 修复导入语句的花括号
content = content.replace(
      /import\s+([^{]*?)\s*{\s*([^}]*?)\s*}\s*([^{]*?)\s*from/g,
      "import$1{ $2 }$3from"
    );

    // 修复默认导入和命名导入的组合
content = content.replace(
      /import\s+(\w+)\s*,\s*{\s*([^}]*?)\s*}\s*from/g,
      import $1, { $2 } from"
    );

    return content;
  }

  /**
   * 修复类型定义
   */
  fixTypeDefinitions(content) {
    // 修复接口定义
content = content.replace(
      /interface\s+(\w+)\s*{([^}]*?)}/gs,
      (match, name, body) => {
        const fixedBody = body.replace(;
          /(\w+)\s*:\s*([^;,\n]+)\s*([;]?)/g,
          "$1: $2$3
        );
        return `interface ${name} {${fixedBody}}`;
      }
    );

    // 修复类型别名
content = content.replace(
      /type\s+(\w+)\s*=\s*([^;]+);?/g,
      "type $1 = $2;"
    );

    // 修复泛型约束
content = content.replace(
      /<\s*(\w+)\s+extends\s+([^>]+)\s*>/g,
      <$1 extends $2>"
    );

    return content;
  }

  /**
   * 递归查找所有TypeScript文件
   */
  findTypeScriptFiles(dir) {
    const files = [];

    try {
      const items = fs.readdirSync(dir);

      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
          if (!["node_modules, ".git", .expo", "android, "ios", Pods"].includes(item)) {
            files.push(...this.findTypeScriptFiles(fullPath));
          }
        } else if (item.endsWith(".ts) || item.endsWith(".tsx")) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      }

    return files;
  }

  /**
   * 执行高级语法修复
   */
  async fix() {
    const projectRoot = process.cwd();

    // 第一步：分析当前错误
const errors = this.analyzeTypeScriptErrors();
    // 第二步：查找所有TypeScript文件
const tsFiles = this.findTypeScriptFiles(projectRoot);
    // 第三步：修复文件
for (const file of tsFiles) {
      this.fixFile(file);
    }

    // 第四步：再次检查错误
const remainingErrors = this.analyzeTypeScriptErrors();

    this.generateReport(errors.length, remainingErrors.length);
  }

  /**
   * 生成修复报告
   */
  generateReport(initialErrors, remainingErrors) {
    );

    if (this.fixedFiles.length > 0) {
      this.fixedFiles.forEach(file => {
        }`);
        });
    }

    if (this.errors.length > 0) {
      this.errors.forEach(error => {
        });
    }

    // 保存详细报告
const report = {
      timestamp: new Date().toISOString(),
      summary: {
        initialErrors,
        remainingErrors,
        fixedErrors: initialErrors - remainingErrors,
        fixedFiles: this.fixedFiles.length,
        failedFiles: this.errors.length,
        successRate: this.fixedFiles.length > 0 ?
          ((initialErrors - remainingErrors) / initialErrors * 100).toFixed(2) + "%" : 0%"
      },
      fixedFiles: this.fixedFiles,
      errors: this.errors;
    };

    fs.writeFileSync(
      "ADVANCED_SYNTAX_FIX_REPORT.json,
      JSON.stringify(report, null, 2),
      "utf8"
    );

    if (remainingErrors < initialErrors) {
      } else {
      }
  }
}

// 执行修复
if (require.main === module) {
  const fixer = new AdvancedSyntaxFixer();
  fixer.fix().catch(console.error);
}

module.exports = AdvancedSyntaxFixer;