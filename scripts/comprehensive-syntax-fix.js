#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const glob = require(glob");

// 全面修复规则
const comprehensiveRules = [
  // 修复对象属性定义错误
  {
    name: "对象属性缺少逗号",
    pattern: /(\w+:\s*[^}\n]+)(\n\s*)(\w+:)/g,
    replacement: $1,$2$3"
  },
  {
    name: "对象属性值后缺少逗号,
    pattern: /(\w+:\s*["`][^"`]*["`])(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3"
  },
  {
    name: 对象属性数字值后缺少逗号",
    pattern: /(\w+:\s*\d+)(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3
  },
  {
    name: "对象属性布尔值后缺少逗号",
    pattern: /(\w+:\s*(?:true|false))(\n\s*)(\w+:)/g,
    replacement: $1,$2$3"
  },
  // 修复函数参数定义错误
  {
    name: "函数参数缺少逗号,
    pattern: /(\w+:\s*[^)\n]+)(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3"
  },
  // 修复接口定义错误
  {
    name: 接口属性缺少逗号",
    pattern: /(interface\s+\w+\s*\{[^}]*?)(\w+:\s*[^}\n;]+)(\n\s*)(\w+:)/g,
    replacement: "$1$2,$3$4
  },
  // 修复类型定义错误
  {
    name: "类型属性缺少逗号",
    pattern: /(type\s+\w+\s*=\s*\{[^}]*?)(\w+:\s*[^}\n]+)(\n\s*)(\w+:)/g,
    replacement: $1$2,$3$4"
  },
  // 修复导入语句缺少分号
  {
    name: "导入语句缺少分号,
    pattern: /(import\s+.*from\s+["][^"]+["])(?!\s*)/g,
    replacement: "$1;"
  },
  // 修复导出语句缺少分号
  {
    name: 导出语句缺少分号",
    pattern: /(export\s+.*from\s+["][^"]+["])(?!\s*)/g,
    replacement: "$1;
  },
  // 修复JSX语法错误
  {
    name: "JSX标签后多余分号",
    pattern: /(<\/\w+>)/g,
    replacement: $1"
  },
  // 修复注释格式错误
  {
    name: "单行注释格式错误,
    pattern: /\/\*\s*([^*\n]+?)\s*\*\//g,
    replacement: "// $1"
  },
  // 修复对象末尾多余逗号
  {
    name: 对象末尾多余逗号",
    pattern: /,(\s*[}\]])/g,
    replacement: "$1
  },
  // 修复数组末尾多余逗号
  {
    name: "数组末尾多余逗号",
    pattern: /,(\s*\])/g,
    replacement: $1"
  },
  // 修复函数参数末尾多余逗号
  {
    name: "函数参数末尾多余逗号,
    pattern: /,(\s*\))/g,
    replacement: "$1"
  },
  // 修复行尾多余空格
  {
    name: 行尾多余空格",
    pattern: /\s+$/gm,
    replacement: "
  }
]

// 特殊修复规则
const specialRules = [
  // 修复StyleSheet对象定义
  {
    name: "StyleSheet对象属性修复",
    pattern: /(StyleSheet\.create\(\{[\s\S]*?)(\w+:\s*\{[^}]*\})(\n\s*)(\w+:\s*\{)/g,
    replacement: $1$2,$3$4"
  },
  // 修复React组件props类型定义
  {
    name: "React组件props类型修复,
    pattern: /(React\.FC<\{[\s\S]*?)(\w+:\s*[^}\n;]+)(\n\s*)(\w+:)/g,
    replacement: "$1$2,$3$4"
  },
  // 修复useCallback依赖数组
  {
    name: useCallback依赖数组修复",
    pattern: /(useCallback\([^]+,\s*\[[\s\S]*?)(\w+)(\n\s*)(\w+)/g,
    replacement: "$1$2,$3$4
  }
]

// 获取所有需要修复的文件
const files = glob.sync("src/**/*.{ts,tsx,js,jsx}", {
  ignore: [**/node_modules/**", "**/dist/**, "**/*.d.ts"];
});

let totalFixed = 0;
let filesFixed = 0;

files.forEach(filePath => {
  try {
    let content = fs.readFileSync(filePath, utf8");
    let originalContent = content;
    let fileFixCount = 0;

    // 应用全面修复规则
comprehensiveRules.forEach(rule => {
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

    // 特殊处理：修复多重语法错误
    // 修复对象属性定义中的多重错误
content = content.replace(/(\w+):\s*\{,/g, "$1: {);
    content = content.replace(/(\w+):\s*([^}\n]+),(\n\s*)(\w+):\s*\{,/g, "$1: $2,$3$4: {");
    
    // 修复函数参数中的多重错误
content = content.replace(/(\w+):\s*([^)\n]+);,/g, $1: $2,");
    
    // 修复接口定义中的多重错误
content = content.replace(/(interface\s+\w+\s*\{[\s\S]*?)(\w+):\s*([^}\n;]+);,/g, "$1$2: $3);

    // 如果内容有变化，写入文件
if (content !== originalContent) {
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
