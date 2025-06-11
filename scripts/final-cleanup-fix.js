#!/usr/bin/env node;
const fs = require("fs");
const path = require("path");
const glob = require("glob");
// 最终清理修复规则
const finalCleanupRules = [
  // 修复注释格式错误 - 更精确的模式
  {"
    name: "单行注释格式错误",
    pattern: /\/\*\s*([^*\n]+?)\s*\*\//g,"
    replacement: // $1"
  },
  {"
    name: "多行注释转单行,
    pattern: /\/\*\*\s*([^*\n]+?)\s*\*\//g,"
    replacement: "// $1"
  },
  {"
    name: 复杂注释格式修复",
    pattern: /\/\*([^*]|\*(?!\/))*\*\//g,
    replacement: (match) => {
      // 提取注释内容"
const content = match.replace(/\/\*|\*\// g, ").replace(/\*/g, ").trim()
      if (content) {
        return `// ${content}`
      }
      return // "
    }
  },
  // 修复对象属性定义错误
  {"
    name: "对象属性缺少逗号,
    pattern: /(\w+:\s*[^}\n]+)(\n\s*)(\w+:)/g,"
    replacement: "$1,$2$3"
  },
  {"
    name: 对象属性值后缺少逗号","
    pattern: /(\w+:\s*["`][^"`]*["`])(\n\s*)(\w+:)/g,"
    replacement: "$1,$2$3
  },
  {"
    name: "对象属性数字值后缺少逗号",
    pattern: /(\w+:\s*\d+)(\n\s*)(\w+:)/g,"
    replacement: $1,$2$3"
  },
  {"
    name: "对象属性布尔值后缺少逗号,
    pattern: /(\w+:\s*(?:true|false))(\n\s*)(\w+:)/g,"
    replacement: "$1,$2$3"
  },
  {"
    name: 对象属性函数值后缺少逗号",
    pattern: /(\w+:\s*\([^)]*\)\s*=>\s*[^}\n]+)(\n\s*)(\w+:)/g,"
    replacement: "$1,$2$3
  },
  // 修复导入语句缺少分号
  {"
    name: "导入语句缺少分号","
    pattern: /(import\s+.*from\s+["][^"]+["])(?!\s*)/g,"
    replacement: $1;
  },
  {"
    name: "导出语句缺少分号,"
    pattern: /(export\s+.*from\s+["][^"]+["])(?!\s*;)/g,"
    replacement: "$1;
  },
  // 修复对象末尾多余逗号
  {"
    name: 对象末尾多余逗号",
    pattern: /,(\s*[}\]])/g,"
    replacement: "$1
  },
  // 修复行尾多余空格
  {"
    name: "行尾多余空格",
    pattern: /\s+$/gm,"
    replacement: "
  }
]
// 特殊修复规则 - 针对特定文件类型
const specialRules = [
  // 修复StyleSheet对象定义
  {"
    name: "StyleSheet对象属性修复,
    pattern: /(StyleSheet\.create\(\{[\s\S]*?)(\w+:\s*\{[^}]*\})(\n\s*)(\w+:\s*\{)/g,"
    replacement: "$1$2,$3$4"
  },
  // 修复React组件props类型定义
  {"
    name: React组件props类型修复",
    pattern: /(React\.FC<\{[\s\S]*?)(\w+:\s*[^}\n;]+)(\n\s*)(\w+:)/g,"
    replacement: "$1$2,$3$4
  },
  // 修复接口定义
  {"
    name: "接口属性修复",
    pattern: /(interface\s+\w+\s*\{[\s\S]*?)(\w+:\s*[^}\n]+)(\n\s*)(\w+:)/g,"
    replacement: $1$2,$3$4"
  },
  // 修复类型定义
  {"
    name: "类型属性修复,
    pattern: /(type\s+\w+\s*=\s*\{[\s\S]*?)(\w+:\s*[^}\n]+)(\n\s*)(\w+:)/g,"
    replacement: "$1$2,$3$4"
  }
];
// 获取所有需要修复的文件"
const files = glob.sync(src/**/*.{ts,tsx,js,jsx}", {"
  ignore: ["**/node_modules/**, "**/dist/**", **/*.d.ts"];
});
let totalFixed = 0;
let filesFixed = 0;
files.forEach(filePath => {
  try {"
    let content = fs.readFileSync(filePath, "utf8);
    let originalContent = content;
    let fileFixCount = 0;
    // 应用最终清理修复规则
finalCleanupRules.forEach(rule => {
      const beforeMatches = content.match(rule.pattern);
      if (beforeMatches) {
        content = content.replace(rule.pattern, rule.replacement);
        const afterMatches = content.match(rule.pattern);
        const fixedCount = (beforeMatches ? beforeMatches.length : 0) - (afterMatches ? afterMatches.length : 0);
        if (fixedCount > 0) {
          fileFixCount += fixedCount;
        }
      }
    });
    // 应用特殊修复规则
specialRules.forEach(rule => {
      const beforeMatches = content.match(rule.pattern);
      if (beforeMatches) {
        content = content.replace(rule.pattern, rule.replacement);
        const afterMatches = content.match(rule.pattern);
        const fixedCount = (beforeMatches ? beforeMatches.length : 0) - (afterMatches ? afterMatches.length : 0);
        if (fixedCount > 0) {
          fileFixCount += fixedCount;
        }
      }
    });
    // 特殊处理：修复复杂的语法错误
    // 修复对象属性定义中的复杂错误"
content = content.replace(/(\w+):\s*\{,/g, "$1: {");
    content = content.replace(/(\w+):\s*([^}\n]+),(\n\s*)(\w+):\s*\{,/g, $1: $2,$3$4: {");
    // 修复函数参数中的错误"
content = content.replace(/(\w+):\s*([^)\n]+);/g, "$1: $2);
    // 修复接口定义中的错误"
content = content.replace(/(interface\s+\w+\s*\{[\s\S]*?)(\w+):\s*([^}\n;]+);/g, "$1$2: $3,");
    // 修复多重注释格式错误"
content = content.replace(/\/\*\s*\*\// g, //")"
    content = content.replace(/\/\*\s*([^*]+)\s*\*\// g, "// $1)
    // 如果内容有变化，写入文件
if (content !== originalContent) {"
      fs.writeFileSync(filePath, content, "utf8");
      `);
      totalFixed += fileFixCount;
      filesFixed++;
    } else {
      `);
    }
  } catch (error) {
    `);
  }
});
* 100)}%`);