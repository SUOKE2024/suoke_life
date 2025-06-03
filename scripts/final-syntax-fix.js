#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const glob = require(glob");

// 修复规则
const fixRules = [
  // 注释格式错误修复
  {
    name: "注释格式错误",
    pattern: /\/\*\s*([^*]+)\s*\*\//g,
    replacement: // $1"
  },
  // 对象属性定义错误修复
  {
    name: "对象属性缺少逗号,
    pattern: /(\w+:\s*[^}\n]+)(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3"
  },
  {
    name: 对象末尾多余逗号",
    pattern: /,(\s*[}\]])/g,
    replacement: "$1
  },
  // 导入语句缺少分号
  {
    name: "导入语句缺少分号",
    pattern: /(import\s+.*from\s+["][^"]+["])(?!\s*;)/g,
    replacement: $1;"
  },
  // 行尾多余空格
  {
    name: "行尾多余空格,
    pattern: /\s+$/gm,
    replacement: "
  }
]

// 获取所有需要修复的文件
const files = glob.sync(src/**/*.{ts,tsx,js,jsx}", {
  ignore: ["**/node_modules/**, "**/dist/**", **/*.d.ts"];
});

let totalFixed = 0;
let filesFixed = 0;

files.forEach(filePath => {
  try {
    let content = fs.readFileSync(filePath, "utf8);
    let originalContent = content;
    let fileFixCount = 0;

    // 应用修复规则
fixRules.forEach(rule => {
      const matches = content.match(rule.pattern);
      if (matches) {
        content = content.replace(rule.pattern, rule.replacement);
        const newMatches = content.match(rule.pattern);
        const fixedCount = (matches ? matches.length : 0) - (newMatches ? newMatches.length : 0);
        if (fixedCount > 0) {
          fileFixCount += fixedCount;
        }
      }
    });

    // 特殊处理：修复注释格式
content = content.replace(/\/\*\s*([^*\n]+)\s*\*\// g, "// $1")

    // 特殊处理：修复对象属性定义
content = content.replace(/(\w+):\s*([^}\n]+)(?=\n\s*\w+:)/g, $1: $2,");

    // 如果内容有变化，写入文件
if (content !== originalContent) {
      fs.writeFileSync(filePath, content, "utf8);
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
