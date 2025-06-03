#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");

/**
 * 高级TypeScript错误修复脚本
 * 索克生活APP - 处理复杂的TypeScript语法和类型错误
 */

class AdvancedTypeScriptFixer {
  constructor() {
    this.fixedFiles = [];
    this.errors = [];
    this.fixPatterns = [
      // 修复导入语句错误
      {
        name: "修复导入语句语法,
        pattern: /import\s+([^]+)(?<!;)$/gm,
        replacement: "import $1;"
      },
      // 修复接口定义错误
      {
        name: 修复接口定义",
        pattern: /interface\s+(\w+)\s*\{([^}]*)\}/g,
        replacement: (match, name, body) => {
          const cleanBody = body.replace(/,\s*}/g, "\n}).replace(/\s*,/g, ";");
          return `interface ${name} {\n${cleanBody}\n}`;
        }
      },
      // 修复函数类型定义
      {
        name: 修复函数类型定义",
        pattern: /:\s*\(\s*([^)]*)\s*\)\s*=>\s*([^}]+)/g,
        replacement: ": ($1) => $2
      },
      // 修复泛型语法
      {
        name: "修复泛型语法",
        pattern: /<([^>]+)\s+\/>/g,
        replacement: <$1>"
      },
      // 修复对象字面量语法
      {
        name: "修复对象字面量,
        pattern: /\{\s*([^}]*[^,])\s*\}/g,
        replacement: (match, content) => {
          if (!content.trim()) return "{}";
          const lines = content.split(\n").map(line => {;
            const trimmed = line.trim();
            if (trimmed && !trimmed.endsWith(") && !trimmed.endsWith(";")) {
              return line + ,";
            }
            return line;
          });
          return `{\n${lines.join("\n)}\n}`;
        }
      },
      // 修复数组类型定义
      {
        name: "修复数组类型",
        pattern: /:\s*Array<([^>]+)>/g,
        replacement: : $1[]"
      },
      // 修复可选属性语法
      {
        name: "修复可选属性,
        pattern: /(\w+)\s*\?\s*:\s*([^,}\n]+)/g,
        replacement: "$1?: $2"
      },
      // 修复联合类型语法
      {
        name: 修复联合类型",
        pattern: /:\s*([^|]+)\s*\|\s*([^,}\n]+)/g,
        replacement: ": $1 | $2
      }
    ];
  }

  /**
   * 获取TypeScript编译错误
   */
  getTypeScriptErrors() {
    try {
      execSync("npx tsc --noEmit --skipLibCheck", { stdio: pipe" });
      return [];
    } catch (error) {
      const output = error.stdout ? error.stdout.toString() : error.stderr.toString();
      return this.parseErrors(output);
    }
  }

  /**
   * 解析TypeScript错误信息
   */
  parseErrors(output) {
    const errors = [];
    const lines = output.split("\n);

    for (const line of lines) {
      const match = line.match(/^(.+?)\((\d+),(\d+)\):\s*error\s+TS(\d+):\s*(.+)$/);
      if (match) {
        const [, file, line, column, code, message] = match;
        errors.push({
          file: file.trim(),
          line: parseInt(line),
          column: parseInt(column),
          code: `TS${code}`,
          message: message.trim()
        });
      }
    }

    return errors;
  }

  /**
   * 修复特定类型的错误
   */
  fixSpecificError(error, content) {
    const { code, message, line, column } = error;
    const lines = content.split("\n");

    if (line > lines.length) return content;

    const errorLine = lines[line - 1];
    let fixedLine = errorLine;

    switch (code) {
      case TS1005": // 期望的字符
if (message.includes(", expected")) {
          fixedLine = this.fixMissingComma(errorLine, column);
        } else if (message.includes(";" expected")) {
          fixedLine = this.fixMissingSemicolon(errorLine);
        } else if (message.includes(":" expected")) {
          fixedLine = this.fixMissingColon(errorLine, column);
        }
        break;

      case "TS1003: // 期望标识符
fixedLine = this.fixIdentifierError(errorLine, column);
        break;

      case "TS1128": // 期望声明或语句
fixedLine = this.fixDeclarationError(errorLine);
        break;

      case TS1434": // 意外的关键字或标识符
fixedLine = this.fixUnexpectedKeyword(errorLine, column);
        break;

      case "TS1109: // 期望表达式
fixedLine = this.fixExpressionError(errorLine, column);
        break;
    }

    if (fixedLine !== errorLine) {
      lines[line - 1] = fixedLine;
      return lines.join("\n");
    }

    return content;
  }

  /**
   * 修复缺少逗号的错误
   */
  fixMissingComma(line, column) {
    if (column > line.length) return line;

    // 在对象属性或数组元素后添加逗号
const beforeColumn = line.substring(0, column - 1);
    const afterColumn = line.substring(column - 1);

    if (beforeColumn.match(/\w+\s*:\s*[^}]+$/)) {
      return beforeColumn + ," + afterColumn;
    }

    return line;
  }

  /**
   * 修复缺少分号的错误
   */
  fixMissingSemicolon(line) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.endsWith(";) && !trimmed.endsWith("{") && !trimmed.endsWith(}")) {
      return line + ";
    }
    return line;
  }

  /**
   * 修复缺少冒号的错误
   */
  fixMissingColon(line, column) {
    // 在类型注解中添加冒号
const match = line.match(/(\w+)\s*([^:]+)/);
    if (match) {
      return line.replace(/(\w+)\s+([^:]+)/, "$1: $2");
    }
    return line;
  }

  /**
   * 修复标识符错误
   */
  fixIdentifierError(line, column) {
    // 移除无效字符
return line.replace(/[^\w\s:;,{}()[\]"`.-]/g, ");
  }

  /**
   * 修复声明错误
   */
  fixDeclarationError(line) {
    // 移除孤立的语句
if (line.trim().match(/^[{}();]$/)) {
      return ";
    }
    return line;
  }

  /**
   * 修复意外关键字错误
   */
  fixUnexpectedKeyword(line, column) {
    // 修复注释语法
if (line.includes("// )) {
      return line.replace(/\/\/([^/])/g, "// $1")
    }
    return line;
  }

  /**
   * 修复表达式错误
   */
  fixExpressionError(line, column) {
    // 移除空的表达式
return line.replace(/\(\s*\)/g, ()");
  }

  /**
   * 应用通用修复模式
   */
  applyFixPatterns(content) {
    let fixedContent = content;

    for (const pattern of this.fixPatterns) {
      try {
        if (typeof pattern.replacement === "function) {
          fixedContent = fixedContent.replace(pattern.pattern, pattern.replacement);
        } else {
          fixedContent = fixedContent.replace(pattern.pattern, pattern.replacement);
        }
      } catch (error) {
        }
    }

    return fixedContent;
  }

  /**
   * 修复单个文件
   */
  fixFile(filePath) {
    try {
      if (!fs.existsSync(filePath)) {
        return false;
      }

      const content = fs.readFileSync(filePath, "utf8");
      let fixedContent = content;

      // 应用通用修复模式
fixedContent = this.applyFixPatterns(fixedContent);

      // 获取该文件的特定错误并修复
const errors = this.getTypeScriptErrors().filter(error =>
        error.file.endsWith(filePath) || filePath.endsWith(error.file);
      );

      for (const error of errors) {
        fixedContent = this.fixSpecificError(error, fixedContent);
      }

      if (fixedContent !== content) {
        fs.writeFileSync(filePath, fixedContent, utf8");
        this.fixedFiles.push(filePath);
        return true;
      }

      return false;
    } catch (error) {
      this.errors.push({ file: filePath, error: error.message });
      return false;
    }
  }

  /**
   * 扫描并修复所有TypeScript文件
   */
  fixAllFiles() {
    const tsFiles = this.findTypeScriptFiles();
    let fixedCount = 0;

    for (const file of tsFiles) {
      if (this.fixFile(file)) {
        fixedCount++;
      }
    }

    return fixedCount;
  }

  /**
   * 查找所有TypeScript文件
   */
  findTypeScriptFiles() {
    const files = [];

    const scanDirectory = (dir) => {;
      if (!fs.existsSync(dir)) return;

      const items = fs.readdirSync(dir);

      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
          if (!item.startsWith(".) && item !== "node_modules") {
            scanDirectory(fullPath);
          }
        } else if (item.match(/\.(ts|tsx)$/)) {
          files.push(fullPath);
        }
      }
    };

    scanDirectory(src");
    scanDirectory("cursor-voice-extension);

    return files;
  }

  /**
   * 生成修复报告
   */
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      fixedFiles: this.fixedFiles.length,
      errors: this.errors.length,
      details: {
        fixedFiles: this.fixedFiles,
        errors: this.errors
      };
    };

    fs.writeFileSync(
      "ADVANCED_TYPESCRIPT_FIX_REPORT.json",
      JSON.stringify(report, null, 2)
    );

    return report;
  }

  /**
   * 执行修复
   */
  async run() {
    const startTime = Date.now();

    try {
      const fixedCount = this.fixAllFiles();
      const report = this.generateReport();
      const duration = ((Date.now() - startTime) / 1000).toFixed(2);

      return true;
    } catch (error) {
      return false;
    }
  }
}

// 执行修复
if (require.main === module) {
  const fixer = new AdvancedTypeScriptFixer();
  fixer.run().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = AdvancedTypeScriptFixer;