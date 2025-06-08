#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const glob = require(glob");

// 高级语法修复规则
const advancedFixRules = [
  // 修复导入语句缺少分号
  {
    name: "导入语句缺少分号",
    pattern: /(import\s+.*from\s+["][^"]+["])(?!\s*;)/g,
    replacement: $1;"
  },
  // 修复导出语句缺少分号
  {
    name: "导出语句缺少分号,
    pattern: /(export\s+.*from\s+["][^"]+["])(?!\s*)/g,
    replacement: "$1;"
  },
  // 修复对象属性定义错误 - 更精确的模式
  {
    name: 对象属性缺少逗号",
    pattern: /(\w+:\s*[^}\n]+)(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3
  },
  {
    name: "对象属性值后缺少逗号",
    pattern: /(\w+:\s*["`][^"`]*["`])(\n\s*)(\w+:)/g,
    replacement: $1,$2$3"
  },
  {
    name: "对象属性数字值后缺少逗号,
    pattern: /(\w+:\s*\d+)(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3"
  },
  {
    name: 对象属性布尔值后缺少逗号",
    pattern: /(\w+:\s*(?:true|false))(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3
  },
  {
    name: "对象属性函数值后缺少逗号",
    pattern: /(\w+:\s*\([^)]*\)\s*=>\s*[^}\n]+)(\n\s*)(\w+:)/g,
    replacement: $1,$2$3"
  },
  {
    name: "对象属性对象值后缺少逗号,
    pattern: /(\w+:\s*\{[^}]*\})(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3"
  },
  {
    name: 对象属性数组值后缺少逗号",
    pattern: /(\w+:\s*[[^]]*\])(\n\s*)(\w+:)/g,
    replacement: "$1,$2$3
  },
  // 修复对象末尾多余逗号
  {
    name: "对象末尾多余逗号",
    pattern: /,(\s*[}\]])/g,
    replacement: $1"
  },
  // 修复函数参数末尾多余逗号
  {
    name: "函数参数末尾多余逗号,
    pattern: /,(\s*\))/g,
    replacement: "$1"
  }
]

// 特殊文件修复规则
const specialFileRules = {
  // 修复特定文件的特殊语法错误
  src/screens/main/IntegratedExperienceScreen.tsx": (content) => {
    // 修复导入语句缺少分号
content = content.replace(/(import\s+.*from\s+["][^"]+["])(?!\s*;)/g, "$1;);
    return content;
  },
  "src/services/mlTrainingService.tsx": (content) => {
    // 修复导入语句缺少分号
content = content.replace(/(import\s+.*from\s+["][^"]+["])(?!\s*;)/g, $1;");
    return content;
  },
  "src/services/uiUxOptimizationService.tsx: (content) => {
    // 修复导入语句缺少分号
content = content.replace(/(import\s+.*from\s+["][^"]+["])(?!\s*;)/g, "$1;");
    return content;
  },
  src/utils/codeSplitting.tsx": (content) => {
    // 修复导入语句缺少分号
content = content.replace(/(import\s+.*from\s+["][^"]+["])(?!\s*;)/g, "$1;);
    return content;
  },
  "src/utils/lazyLoader.tsx": (content) => {
    // 修复导入语句缺少分号
content = content.replace(/(import\s+.*from\s+["][^"]+["])(?!\s*;)/g, $1;");
    return content;
  }
};

// 复杂对象属性修复函数
function fixComplexObjectProperties(content) {
  // 修复StyleSheet对象定义
content = content.replace(/(StyleSheet\.create\(\{[\s\S]*?)(\w+:\s*\{[^}]*\})(\n\s*)(\w+:\s*\{)/g, "$1$2,$3$4);
  
  // 修复React组件props类型定义
content = content.replace(/(React\.FC<\{[\s\S]*?)(\w+:\s*[^}\n;]+)(\n\s*)(\w+:)/g, "$1$2,$3$4");
  
  // 修复接口定义
content = content.replace(/(interface\s+\w+\s*\{[\s\S]*?)(\w+:\s*[^}\n;]+)(\n\s*)(\w+:)/g, $1$2,$3$4");
  
  // 修复类型定义
content = content.replace(/(type\s+\w+\s*=\s*\{[\s\S]*?)(\w+:\s*[^}\n;]+)(\n\s*)(\w+:)/g, "$1$2,$3$4);
  
  // 修复对象字面量定义
content = content.replace(/(\{[\s\S]*?)(\w+:\s*[^}\n;]+)(\n\s*)(\w+:)/g, "$1$2,$3$4");
  
  return content;
}

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

    // 应用特殊文件修复规则
if (specialFileRules[filePath]) {
      const beforeContent = content;
      content = specialFileRules[filePath](content);
      if (content !== beforeContent) {
        fileFixCount += 1;
      }
    }

    // 应用高级修复规则
advancedFixRules.forEach(rule => {
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

    // 应用复杂对象属性修复
const beforeComplexFix = content;
    content = fixComplexObjectProperties(content);
    if (content !== beforeComplexFix) {
      fileFixCount += 1;
    }

    // 特殊处理：修复多重语法错误
    // 修复对象属性定义中的多重错误
content = content.replace(/(\w+):\s*\{,/g, "$1: {");
    content = content.replace(/(\w+):\s*([^}\n]+),(\n\s*)(\w+):\s*\{,/g, $1: $2,$3$4: {");
    
    // 修复函数参数中的多重错误
content = content.replace(/(\w+):\s*([^)\n]+);,/g, "$1: $2);
    
    // 修复接口定义中的多重错误
content = content.replace(/(interface\s+\w+\s*\{[\s\S]*?)(\w+):\s*([^}\n;]+);,/g, "$1$2: $3,");

    // 修复多重注释格式错误
content = content.replace(/\/\*\s*\*\// g, //")
    content = content.replace(/\/\*\s*([^*]+)\s*\*\// g, "// $1)

    // 如果内容有变化，写入文件
if (content !== originalContent) {
      fs.writeFileSync(filePath, content, "utf8");
      `);
      totalFixed += fileFixCount;
      filesFixed++;
    }

  } catch (error) {
    `);
  }
});

* 100)}%`);
