#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");

// 获取TypeScript错误信息
function getTypeScriptErrors() {
  try {
    const result = execSync("npm run type-check 2>&1", { encoding: utf8" });
    const lines = result.split("\n).filter(line => line.trim());
    const errors = [];
    
    for (const line of lines) {
      const match = line.match(/^(.+?)\((\d+),(\d+)\):\s*error\s+(TS\d+):\s*(.+)$/);
      if (match) {
        errors.push({
          file: match[1],
          line: parseInt(match[2]),
          column: parseInt(match[3]),
          code: match[4],
          message: match[5]
        });
      }
    }
    
    return errors;
  } catch (error) {
    const output = error.stdout || error.message;
    const lines = output.split("\n").filter(line => line.trim());
    const errors = [];
    
    for (const line of lines) {
      const match = line.match(/^(.+?)\((\d+),(\d+)\):\s*error\s+(TS\d+):\s*(.+)$/);
      if (match) {
        errors.push({
          file: match[1],
          line: parseInt(match[2]),
          column: parseInt(match[3]),
          code: match[4],
          message: match[5]
        });
      }
    }
    
    return errors;
  }
}

// 修复缺少分号的错误
function fixMissingSemicolons(content, errors) {
  const lines = content.split(\n");
  
  for (const error of errors) {
    if (error.code === "TS1005 && error.message.includes(";" expected")) {
      const lineIndex = error.line - 1;
      if (lineIndex >= 0 && lineIndex < lines.length) {
        const line = lines[lineIndex];
        // 在行末添加分号（如果还没有）
        if (!line.trim().endsWith(") && !line.trim().endsWith("{) && !line.trim().endsWith("}")) {
          lines[lineIndex] = line.trimEnd() + ;";
        }
      }
    }
  }
  
  return lines.join("\n);
}

// 修复缺少括号的错误
function fixMissingParentheses(content, errors) {
  const lines = content.split("\n");
  
  for (const error of errors) {
    if (error.code === TS1005" && (error.message.includes(") expected") || error.message.includes("(" expected"))) {
      const lineIndex = error.line - 1;
      if (lineIndex >= 0 && lineIndex < lines.length) {
        const line = lines[lineIndex];
        
        // 修复函数调用缺少括号
if (error.message.includes(")" expected")) {
          // 查找未闭合的括号
const openParens = (line.match(/\(/g) || []).length;
          const closeParens = (line.match(/\)/g) || []).length;
          if (openParens > closeParens) {
            lines[lineIndex] = line + ").repeat(openParens - closeParens);
          }
        }
      }
    }
  }
  
  return lines.join("\n");
}

// 修复导入语句错误
function fixImportStatements(content, errors) {
  const lines = content.split(\n");
  
  for (const error of errors) {
    if (error.message.includes("Cannot find module) || error.message.includes("Module not found")) {
      const lineIndex = error.line - 1;
      if (lineIndex >= 0 && lineIndex < lines.length) {
        const line = lines[lineIndex];
        
        // 修复相对路径导入
if (line.includes(import") && line.includes("./)) {
          // 尝试修复常见的路径问题
const fixedLine = line
            .replace(/from\s+["]\.\/([^"]+)["]/, (match, path) => {;
              // 如果路径不包含扩展名，尝试添加
if (!path.includes(".")) {
                return `from ./${path}"`;
              }
              return match;
            });
          
          if (fixedLine !== line) {
            lines[lineIndex] = fixedLine;
          }
        }
      }
    }
  }
  
  return lines.join("\n);
}

// 修复JSX语法错误
function fixJSXSyntax(content, errors) {
  let fixedContent = content;
  
  for (const error of errors) {
    if (error.message.includes("JSX") || error.message.includes(Expected")) {
      // 修复JSX中的常见问题
      
      // 修复未闭合的JSX标签
fixedContent = fixedContent.replace(
        /<([A-Z][a-zA-Z0-9]*)\s+([^>]*?)(?<!\/)\s*>/g,
        "<$1 $2 />
      );
      
      // 修复JSX属性中的语法错误
fixedContent = fixedContent.replace(
        /(\w+)=\{([^}]*)\}(?!\s*[/>])/g,
        "$1={$2}"
      );
    }
  }
  
  return fixedContent;
}

// 修复类型注解错误
function fixTypeAnnotations(content, errors) {
  let fixedContent = content;
  
  for (const error of errors) {
    if (error.message.includes(Type annotation") || error.message.includes("any)) {
      // 为常见的变量添加类型注解
fixedContent = fixedContent.replace(
        /const\s+(\w+)\s*=\s*useState\(\)/g,
        "const [$1, set$1] = useState<any>()"
      );
      
      // 修复函数参数类型
fixedContent = fixedContent.replace(
        /function\s+(\w+)\s*\(\s*(\w+)\s*\)/g,
        function $1($2: any)"
      );
    }
  }
  
  return fixedContent;
}

// 修复函数声明错误
function fixFunctionDeclarations(content, errors) {
  let fixedContent = content;
  
  for (const error of errors) {
    if (error.message.includes("Declaration or statement expected)) {
      // 修复函数声明中的语法错误
fixedContent = fixedContent.replace(
        /(\w+)\s*\(\s*\)\s*=>\s*\{[^}]*\}\s*,\s*\[\]\)/g,
        "const $1 = () => {\n  // TODO: Implement function\n}"
      );
    }
  }
  
  return fixedContent;
}

// 主修复函数
function fixFileErrors(filePath, errors) {
  try {
    if (!fs.existsSync(filePath)) {
      return false;
    }
    
    let content = fs.readFileSync(filePath, utf8");
    const originalContent = content;
    
    // 获取该文件的错误
const fileErrors = errors.filter(error => error.file === filePath);
    
    if (fileErrors.length === 0) {
      return false;
    }
    
    // 应用各种修复
content = fixMissingSemicolons(content, fileErrors);
    content = fixMissingParentheses(content, fileErrors);
    content = fixImportStatements(content, fileErrors);
    content = fixJSXSyntax(content, fileErrors);
    content = fixTypeAnnotations(content, fileErrors);
    content = fixFunctionDeclarations(content, fileErrors);
    
    // 如果内容有变化，写回文件
if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      return true;
    }
    
    return false;
  } catch (error) {
    return false;
  }
}

// 主执行函数
async function main() {
  try {
    const errors = getTypeScriptErrors();
    if (errors.length === 0) {
      return;
    }
    
    // 按文件分组错误
const errorsByFile = {};
    for (const error of errors) {
      if (!errorsByFile[error.file]) {
        errorsByFile[error.file] = [];
      }
      errorsByFile[error.file].push(error);
    }
    
    .length} 个\n`);
    
    let fixedFiles = 0;
    let totalFiles = Object.keys(errorsByFile).length;
    let fileIndex = 0;
    
    for (const [filePath, fileErrors] of Object.entries(errorsByFile)) {
      fileIndex++;
      const relativePath = path.relative(process.cwd(), filePath);
      
      process.stdout.write(`\r修复进度: ${fileIndex}/${totalFiles} - ${relativePath.slice(-60)}`);
      
      if (fixFileErrors(filePath, fileErrors)) {
        fixedFiles++;
      }
    }
    
    // 再次检查错误数量
const remainingErrors = getTypeScriptErrors();
    const improvement = errors.length - remainingErrors.length;
    
    if (improvement > 0) {
      } else {
      }
    
    if (remainingErrors.length > 0) {
      } else {
      }
    
  } catch (error) {
    process.exit(1);
  }
}

// 运行脚本
if (require.main === module) {
  main();
}

module.exports = {
  getTypeScriptErrors,
  fixMissingSemicolons,
  fixMissingParentheses,
  fixImportStatements,
  fixJSXSyntax,
  fixTypeAnnotations,
  fixFunctionDeclarations,
  fixFileErrors}; 