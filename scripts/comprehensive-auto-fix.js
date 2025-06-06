#!/usr/bin/env node

/**
 * 索克生活项目 - 综合自动修复工具
 * 整合ESLint、Prettier和自定义修复规则
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const glob = require("glob");

class ComprehensiveAutoFixer {
  constructor() {
    this.fixedFiles = [];
    this.totalFixes = 0;
    this.errors = [];
    this.stats = {
      eslintFixes: 0,
      prettierFixes: 0,
      customFixes: 0,
      totalFiles: 0
    };
  }

  /**
   * 运行综合修复
   */
  async run() {
    console.log("🚀 开始综合自动修复...");
    console.log("=" .repeat(50));

    try {
      // 1. 运行自定义语法修复
      await this.runCustomFixes();

      // 2. 运行ESLint自动修复
      await this.runESLintFix();

      // 3. 运行Prettier格式化
      await this.runPrettierFix();

      // 4. 再次运行ESLint检查
      await this.runFinalESLintCheck();

      // 5. 生成报告
      this.generateReport();

      console.log("\n✅ 综合自动修复完成！");
    } catch (error) {
      console.error("❌ 综合自动修复失败:", error.message);
      process.exit(1);
    }
  }

  /**
   * 运行自定义语法修复
   */
  async runCustomFixes() {
    console.log("\n🔧 步骤1: 运行自定义语法修复...");
    
    const files = glob.sync("src/**/*.{ts,tsx,js,jsx}", {
      ignore: ["**/node_modules/**", "**/dist/**", "**/*.d.ts"]
    });

    this.stats.totalFiles = files.length;
    console.log(`📁 找到 ${files.length} 个文件需要检查`);

    const customRules = this.getCustomFixRules();
    
    for (const file of files) {
      await this.applyCustomFixes(file, customRules);
    }

    console.log(`✅ 自定义修复完成: ${this.stats.customFixes} 处修复`);
  }

  /**
   * 获取自定义修复规则
   */
  getCustomFixRules() {
    return [
      // 修复注释格式错误
      {
        name: "注释格式修复",
        pattern: /\/\*\s*([^*\n]+?)\s*\*\//g,
        replacement: "// $1",
        description: "修复单行注释格式"
      },

      // 修复对象属性缺少逗号
      {
        name: "对象属性逗号修复",
        pattern: /^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)(\s*\n\s*)(\w+):/gm,
        replacement: (match, indent1, prop1, value1, newline, prop2) => {
          const trimmedValue = value1.trim();
          if (!trimmedValue.endsWith(",") && !trimmedValue.endsWith(";") &&
              !trimmedValue.endsWith("{") && !trimmedValue.endsWith("[") &&
              !trimmedValue.endsWith("}") && !trimmedValue.endsWith("]") &&
              !trimmedValue.endsWith(")")) {
            return `${indent1}${prop1}: ${trimmedValue},${newline}${prop2}:`;
          }
          return match;
        },
        description: "添加缺少的对象属性逗号"
      },

      // 修复导入语句缺少分号
      {
        name: "导入语句分号修复",
        pattern: /(import\s+[^;\n]+)(\n)/g,
        replacement: (match, importStatement, newline) => {
          if (!importStatement.trim().endsWith(";")) {
            return importStatement + ";" + newline;
          }
          return match;
        },
        description: "添加导入语句分号"
      },

      // 修复导出语句缺少分号
      {
        name: "导出语句分号修复",
        pattern: /(export\s+[^\n{]+)(\n)/g,
        replacement: (match, exportStatement, newline) => {
          if (!exportStatement.trim().endsWith(";") && 
              !exportStatement.includes("{") && 
              !exportStatement.includes("function") && 
              !exportStatement.includes("class")) {
            return exportStatement + ";" + newline;
          }
          return match;
        },
        description: "添加导出语句分号"
      },

      // 修复对象末尾多余逗号
      {
        name: "对象末尾逗号清理",
        pattern: /,(\s*[}\]])/g,
        replacement: "$1",
        description: "移除对象末尾多余逗号"
      },

      // 修复字符串属性值缺少逗号
      {
        name: "字符串属性逗号修复",
        pattern: /^(\s*)(\w+):\s*(["'][^"']*["'])(\s*\n\s*)(\w+):/gm,
        replacement: "$1$2: $3,$4$5:",
        description: "添加字符串属性值后的逗号"
      },

      // 修复数字属性值缺少逗号
      {
        name: "数字属性逗号修复",
        pattern: /^(\s*)(\w+):\s*(\d+(?:\.\d+)?)(\s*\n\s*)(\w+):/gm,
        replacement: "$1$2: $3,$4$5:",
        description: "添加数字属性值后的逗号"
      },

      // 修复布尔属性值缺少逗号
      {
        name: "布尔属性逗号修复",
        pattern: /^(\s*)(\w+):\s*(true|false)(\s*\n\s*)(\w+):/gm,
        replacement: "$1$2: $3,$4$5:",
        description: "添加布尔属性值后的逗号"
      }
    ];
  }

  /**
   * 应用自定义修复规则
   */
  async applyCustomFixes(filePath, rules) {
    try {
      let content = fs.readFileSync(filePath, "utf8");
      const originalContent = content;
      let fileFixCount = 0;

      for (const rule of rules) {
        if (typeof rule.replacement === "function") {
          const beforeContent = content;
          content = content.replace(rule.pattern, rule.replacement);
          if (content !== beforeContent) {
            fileFixCount += 1;
          }
        } else {
          const beforeMatches = content.match(rule.pattern);
          if (beforeMatches) {
            content = content.replace(rule.pattern, rule.replacement);
            const afterMatches = content.match(rule.pattern);
            const fixedCount = (beforeMatches ? beforeMatches.length : 0) - (afterMatches ? afterMatches.length : 0);
            if (fixedCount > 0) {
              fileFixCount += fixedCount;
            }
          }
        }
      }

      if (content !== originalContent) {
        fs.writeFileSync(filePath, content);
        this.fixedFiles.push({
          file: filePath,
          fixes: fileFixCount,
          type: "custom"
        });
        this.stats.customFixes += fileFixCount;
        console.log(`  📝 ${path.relative(process.cwd(), filePath)}: ${fileFixCount} 处修复`);
      }
    } catch (error) {
      this.errors.push(`自定义修复失败: ${filePath} - ${error.message}`);
    }
  }

  /**
   * 运行ESLint自动修复
   */
  async runESLintFix() {
    console.log("\n🔍 步骤2: 运行ESLint自动修复...");
    
    try {
      const result = execSync("npx eslint --fix --ext .ts,.tsx,.js,.jsx src/", { 
        stdio: "pipe",
        encoding: "utf8"
      });
      
      console.log("✅ ESLint自动修复完成");
      this.stats.eslintFixes = 1;
    } catch (error) {
      // ESLint可能会返回非零退出码，但仍然进行了修复
      console.log("⚠️ ESLint修复完成（有部分警告）");
      this.stats.eslintFixes = 1;
    }
  }

  /**
   * 运行Prettier格式化
   */
  async runPrettierFix() {
    console.log("\n🎨 步骤3: 运行Prettier格式化...");
    
    try {
      execSync("npx prettier --write \"src/**/*.{ts,tsx,js,jsx}\"", { 
        stdio: "pipe"
      });
      
      console.log("✅ Prettier格式化完成");
      this.stats.prettierFixes = 1;
    } catch (error) {
      console.log("⚠️ Prettier格式化部分完成");
      this.errors.push(`Prettier格式化失败: ${error.message}`);
    }
  }

  /**
   * 运行最终ESLint检查
   */
  async runFinalESLintCheck() {
    console.log("\n🔎 步骤4: 运行最终ESLint检查...");
    
    try {
      const result = execSync("npx eslint --ext .ts,.tsx,.js,.jsx src/ --format=compact", { 
        stdio: "pipe",
        encoding: "utf8"
      });
      
      console.log("✅ 最终ESLint检查通过");
    } catch (error) {
      const output = error.stdout || error.stderr || "";
      const lines = output.split("\n").filter(line => line.trim());
      const errorCount = lines.filter(line => line.includes("error")).length;
      const warningCount = lines.filter(line => line.includes("warning")).length;
      
      console.log(`⚠️ 最终检查完成: ${errorCount} 个错误, ${warningCount} 个警告`);
      
      if (errorCount > 0) {
        console.log("\n❌ 仍有错误需要手动修复:");
        lines.slice(0, 10).forEach(line => {
          if (line.includes("error")) {
            console.log(`  ${line}`);
          }
        });
        if (lines.length > 10) {
          console.log(`  ... 还有 ${lines.length - 10} 个问题`);
        }
      }
    }
  }

  /**
   * 生成修复报告
   */
  generateReport() {
    console.log("\n" + "=".repeat(50));
    console.log("📊 综合修复报告");
    console.log("=".repeat(50));
    
    console.log(`📁 总文件数: ${this.stats.totalFiles}`);
    console.log(`🔧 自定义修复: ${this.stats.customFixes} 处`);
    console.log(`🔍 ESLint修复: ${this.stats.eslintFixes ? "✅" : "❌"}`);
    console.log(`🎨 Prettier格式化: ${this.stats.prettierFixes ? "✅" : "❌"}`);
    console.log(`✅ 修复的文件数: ${this.fixedFiles.length}`);
    console.log(`❌ 错误数: ${this.errors.length}`);

    if (this.errors.length > 0) {
      console.log("\n❌ 错误详情:");
      this.errors.slice(0, 5).forEach(error => {
        console.log(`  - ${error}`);
      });
      if (this.errors.length > 5) {
        console.log(`  ... 还有 ${this.errors.length - 5} 个错误`);
      }
    }

    if (this.fixedFiles.length > 0) {
      console.log("\n✅ 修复的文件 (前10个):");
      this.fixedFiles.slice(0, 10).forEach(({ file, fixes, type }) => {
        console.log(`  - ${path.relative(process.cwd(), file)}: ${fixes} 处修复 (${type})`);
      });
      if (this.fixedFiles.length > 10) {
        console.log(`  ... 还有 ${this.fixedFiles.length - 10} 个文件`);
      }
    }

    // 提供下一步建议
    console.log("\n💡 下一步建议:");
    console.log("  1. 运行 'npm test' 检查测试是否通过");
    console.log("  2. 运行 'npm run build' 检查构建是否成功");
    console.log("  3. 检查Git差异确认修复是否正确");
    console.log("  4. 如有必要，手动修复剩余的复杂错误");
  }
}

// 运行综合修复器
if (require.main === module) {
  const fixer = new ComprehensiveAutoFixer();
  fixer.run().catch(console.error);
}

module.exports = ComprehensiveAutoFixer; 