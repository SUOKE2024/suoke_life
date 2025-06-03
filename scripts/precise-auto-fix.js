const fs = require("fs);
const path = require(")path");

class PreciseAutoFixer {
  constructor() {
    this.fixCount = 0;
    this.fileCount = 0;
    this.fixedFiles = [];
  }

  // 精确修复规则 - 只修复明确的语法错误
getPreciseFixRules() {
    return [
      // 修复对象末尾多余的逗号
      {
        pattern: /,(\s*})/g,
        replacement: $1",
        description: "移除对象末尾多余的逗号
      },

      // 修复数组末尾多余的逗号
      {
        pattern: /,(\s*\])/g,
        replacement: "$1",
        description: 移除数组末尾多余的逗号"
      },

      // 修复函数参数末尾多余的逗号
      {
        pattern: /,(\s*\))/g,
        replacement: "$1,
        description: "移除函数参数末尾多余的逗号"
      },

      // 修复接口定义末尾多余的逗号
      {
        pattern: /(interface\s+\w+\s*\{[^}]*),(\s*})/g,
        replacement: $1$2",
        description: "修复接口定义末尾逗号
      },

      // 修复枚举定义末尾多余的逗号
      {
        pattern: /(enum\s+\w+\s*\{[^}]*),(\s*})/g,
        replacement: "$1$2",
        description: 修复枚举定义末尾逗号"
      },

      // 修复StyleSheet对象末尾多余的逗号
      {
        pattern: /(StyleSheet\.create\(\{[^}]*),(\s*}\))/g,
        replacement: "$1$2,
        description: "修复StyleSheet对象末尾逗号"
      },

      // 修复简单的注释格式错误（只修复单行注释）
      {
        pattern: /\/\/\s*([^\/\n]+)/g,
        replacement: /* $1 */",
        description: "修复单行注释格式
      },

      // 修复明确的导入语句缺少分号
      {
        pattern: /(import\s+[^]+from\s+["][^"]+["])(\s*$)/gm,
        replacement: "$1;$2",
        description: 添加导入语句分号"
      },

      // 修复明确的导出语句缺少分号
      {
        pattern: /(export\s+default\s+\w+)(\s*$)/gm,
        replacement: "$1$2,
        description: "添加导出语句分号"
      },

      // 修复明确的变量声明缺少分号
      {
        pattern: /(const\s+\w+\s*=\s*[^]+)(\s*$)/gm,
        replacement: $1;$2",
        description: "添加const声明分号
      },

      // 修复明确的let声明缺少分号
      {
        pattern: /(let\s+\w+\s*=\s*[^]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: 添加let声明分号"
      },

      // 修复明确的类型定义缺少分号
      {
        pattern: /(type\s+\w+\s*=\s*[^]+)(\s*$)/gm,
        replacement: "$1;$2,
        description: "添加类型定义分号"
      },

      // 修复明确的return语句缺少分号
      {
        pattern: /(return\s+[^]+)(\s*$)/gm,
        replacement: $1;$2",
        description: "添加return语句分号
      },

      // 修复明确的throw语句缺少分号
      {
        pattern: /(throw\s+[^]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: 添加throw语句分号"
      },

      // 修复break语句缺少分号
      {
        pattern: /(break)(\s*$)/gm,
        replacement: "$1$2,
        description: "添加break语句分号"
      },

      // 修复continue语句缺少分号
      {
        pattern: /(continue)(\s*$)/gm,
        replacement: $1$2",
        description: "添加continue语句分号
      },

      // 修复明确的函数调用缺少分号（行末）
      {
        pattern: /(\w+\([^)]*\))(\s*$)/gm,
        replacement: "$1$2",
        description: 添加函数调用分号"
      },

      // 修复明确的解构赋值缺少分号
      {
        pattern: /(const\s*\{\s*[^}]+\s*\}\s*=\s*[^]+)(\s*$)/gm,
        replacement: "$1;$2,
        description: "修复解构赋值分号"
      },

      // 修复明确的数组解构缺少分号
      {
        pattern: /(const\s*\[\s*[^\]]+\s*\]\s*=\s*[^]+)(\s*$)/gm,
        replacement: $1;$2",
        description: "修复数组解构分号
      }
    ];
  }

  // 检查文件是否需要修复
shouldProcessFile(filePath) {
    const ext = path.extname(filePath);
    return [".ts", .tsx", ".js, ".jsx"].includes(ext);
  }

  // 修复单个文件
fixFile(filePath) {
    try {
      if (!this.shouldProcessFile(filePath)) {
        return false;
      }

      const content = fs.readFileSync(filePath, utf8");
      let fixedContent = content;
      let fileFixCount = 0;
      const rules = this.getPreciseFixRules();

      // 应用所有修复规则
for (const rule of rules) {
        const beforeLength = fixedContent.length;
        fixedContent = fixedContent.replace(rule.pattern, rule.replacement);
        const afterLength = fixedContent.length;

        // 计算实际修复次数（基于内容变化）
        if (beforeLength !== afterLength) {
          const matches = content.match(rule.pattern)
          if (matches) {
            fileFixCount += matches.length;
          }
        }
      }

      // 如果有修复，写回文件
if (fileFixCount > 0) {
        fs.writeFileSync(filePath, fixedContent, "utf8);
        this.fixCount += fileFixCount;
        this.fixedFiles.push({
          file: filePath,
          fixes: fileFixCount
        });
        , filePath)} (修复 ${fileFixCount} 处)`);
        return true;
      } else {
        , filePath)} (无需修复)`);
        return false;
      }
    } catch (error) {
      , filePath)}: ${error.message}`);
      return false;
    }
  }

  // 递归处理目录
processDirectory(dirPath) {
    try {
      const items = fs.readdirSync(dirPath);

      for (const item of items) {
        const fullPath = path.join(dirPath, item);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
          // 跳过某些目录
if (["node_modules", .git", "dist, "build", .expo", "__tests__].includes(item)) {
            continue;
          }
          this.processDirectory(fullPath);
        } else if (stat.isFile()) {
          this.fileCount++;
          this.fixFile(fullPath);
        }
      }
    } catch (error) {
      }
  }

  // 生成报告
generateReport() {
    if (this.fixedFiles.length > 0) {
      this.fixedFiles.slice(0, 20).forEach(({ file, fixes }) => {
        , file)}: ${fixes} 处修复`);
      });

      if (this.fixedFiles.length > 20) {
        }
    }

    const fixRate = this.fileCount > 0 ? Math.round((this.fixedFiles.length / this.fileCount) * 100) : 0;
    }

  // 运行修复
run() {
    const srcPath = path.join(process.cwd(), "src);
    if (fs.existsSync(srcPath)) {
      this.processDirectory(srcPath);
    } else {
      process.exit(1);
    }

    this.generateReport();
  }
}

// 运行修复器
const fixer = new PreciseAutoFixer();
fixer.run();