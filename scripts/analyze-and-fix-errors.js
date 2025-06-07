const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 获取详细的TypeScript错误信息
function getDetailedErrors() {
  try {
    const output = execSync('npx tsc --noEmit 2>&1', { encoding: 'utf8' });
    const lines = output.split('\n');
    const errors = [];
    
    for (const line of lines) {
      const match = line.match(/^(.+?)\((\d+),(\d+)\):\s*error\s+(TS\d+):\s*(.+)$/);
      if (match) {
        const [, filePath, lineNum, colNum, errorCode, message] = match;
        errors.push({
          file: filePath,
          line: parseInt(lineNum),
          column: parseInt(colNum),
          code: errorCode,
          message: message.trim()
        });
      }
    }
    
    return errors;
  } catch (error) {
    return [];
  }
}

// 分析错误类型
function analyzeErrors(errors) {
  const analysis = {
    byType: {},
    byFile: {},
    commonPatterns: {},
    total: errors.length
  };
  
  for (const error of errors) {
    // 按错误类型分组
    if (!analysis.byType[error.code]) {
      analysis.byType[error.code] = [];
    }
    analysis.byType[error.code].push(error);
    
    // 按文件分组
    if (!analysis.byFile[error.file]) {
      analysis.byFile[error.file] = [];
    }
    analysis.byFile[error.file].push(error);
    
    // 分析常见模式
    const pattern = error.message.toLowerCase();
    if (pattern.includes('cannot find name')) {
      analysis.commonPatterns['undefinedVariable'] = (analysis.commonPatterns['undefinedVariable'] || 0) + 1;
    } else if (pattern.includes('property') && pattern.includes('does not exist')) {
      analysis.commonPatterns['missingProperty'] = (analysis.commonPatterns['missingProperty'] || 0) + 1;
    } else if (pattern.includes('type') && pattern.includes('is not assignable')) {
      analysis.commonPatterns['typeAssignment'] = (analysis.commonPatterns['typeAssignment'] || 0) + 1;
    } else if (pattern.includes('expected')) {
      analysis.commonPatterns['syntaxError'] = (analysis.commonPatterns['syntaxError'] || 0) + 1;
    }
  }
  
  return analysis;
}

// 智能修复规则
const intelligentFixRules = [
  // 修复常见的未定义变量
  {
    errorCode: 'TS2304',
    pattern: /Cannot find name '(\w+)'/,
    fix: (content, error, match) => {
      const varName = match[1];
      const commonImports = {
        'React': "import React from 'react';",
        'View': "import { View } from 'react-native';",
        'Text': "import { Text } from 'react-native';",
        'StyleSheet': "import { StyleSheet } from 'react-native';",
        'TouchableOpacity': "import { TouchableOpacity } from 'react-native';",
        'useState': "import { useState } from 'react';",
        'useEffect': "import { useEffect } from 'react';",
        'useCallback': "import { useCallback } from 'react';",
        'useMemo': "import { useMemo } from 'react';",
        'Alert': "import { Alert } from 'react-native';",
        'Dimensions': "import { Dimensions } from 'react-native';",
        'Platform': "import { Platform } from 'react-native';"
      };
      
      if (commonImports[varName] && !content.includes(`import`)) {
        return commonImports[varName] + '\n' + content;
      }
      return content;
    },
    description: '添加缺失的导入语句'
  },
  
  // 修复类型赋值错误
  {
    errorCode: 'TS2322',
    pattern: /Type '(.+)' is not assignable to type '(.+)'/,
    fix: (content, error, match) => {
      const lines = content.split('\n');
      const lineIndex = error.line - 1;
      
      if (lineIndex >= 0 && lineIndex < lines.length) {
        let line = lines[lineIndex];
        
        // 修复常见的类型问题
        if (line.includes(': any')) {
          line = line.replace(': any', ': unknown');
        } else if (line.includes('= {}')) {
          line = line.replace('= {}', ': Record<string, unknown> = {}');
        } else if (line.includes('= []')) {
          line = line.replace('= []', ': unknown[] = []');
        }
        
        lines[lineIndex] = line;
        return lines.join('\n');
      }
      return content;
    },
    description: '修复类型赋值错误'
  },
  
  // 修复属性不存在错误
  {
    errorCode: 'TS2339',
    pattern: /Property '(\w+)' does not exist on type '(.+)'/,
    fix: (content, error, match) => {
      const propName = match[1];
      const typeName = match[2];
      
      // 如果是对象类型，添加可选属性
      if (typeName === 'object' || typeName === '{}') {
        const lines = content.split('\n');
        const lineIndex = error.line - 1;
        
        if (lineIndex >= 0 && lineIndex < lines.length) {
          let line = lines[lineIndex];
          // 添加可选链操作符
          if (line.includes(`.${propName}`)) {
            line = line.replace(`.${propName}`, `?.${propName}`);
            lines[lineIndex] = line;
            return lines.join('\n');
          }
        }
      }
      return content;
    },
    description: '修复属性不存在错误'
  },
  
  // 修复语法错误
  {
    errorCode: 'TS1005',
    pattern: /'(.+)' expected/,
    fix: (content, error, match) => {
      const expected = match[1];
      const lines = content.split('\n');
      const lineIndex = error.line - 1;
      
      if (lineIndex >= 0 && lineIndex < lines.length) {
        let line = lines[lineIndex];
        
        // 修复常见的语法问题
        if (expected === ';') {
          if (!line.trim().endsWith(';') && !line.trim().endsWith('{') && !line.trim().endsWith('}')) {
            line = line.trimEnd() + ';';
          }
        } else if (expected === ',') {
          if (!line.trim().endsWith(',') && !line.trim().endsWith('{')) {
            line = line.trimEnd() + ',';
          }
        } else if (expected === '}') {
          // 检查是否缺少闭合括号
          const openBraces = (line.match(/{/g) || []).length;
          const closeBraces = (line.match(/}/g) || []).length;
          if (openBraces > closeBraces) {
            line = line.trimEnd() + '}';
          }
        }
        
        lines[lineIndex] = line;
        return lines.join('\n');
      }
      return content;
    },
    description: '修复语法错误'
  }
];

// 应用智能修复
function applyIntelligentFixes(filePath, errors) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let fixCount = 0;
    const appliedFixes = [];
    
    // 按行号排序，从后往前修复避免行号偏移
    const sortedErrors = errors.sort((a, b) => b.line - a.line);
    
    for (const error of sortedErrors) {
      for (const rule of intelligentFixRules) {
        if (error.code === rule.errorCode) {
          const match = error.message.match(rule.pattern);
          if (match) {
            const originalContent = content;
            content = rule.fix(content, error, match);
            
            if (content !== originalContent) {
              fixCount++;
              appliedFixes.push(rule.description);
              break; // 每个错误只应用一个修复规则
            }
          }
        }
      }
    }
    
    return { content, fixCount, appliedFixes };
  } catch (error) {
    return { content: null, fixCount: 0, appliedFixes: [] };
  }
}

// 修复单个文件
function fixFileIntelligently(filePath, fileErrors) {
  try {
    const fileName = path.basename(filePath);
    console.log(`\n🧠 智能修复: ${fileName} (${fileErrors.length}个错误)`);
    
    // 备份原文件
    const originalContent = fs.readFileSync(filePath, 'utf8');
    fs.writeFileSync(filePath + '.intelligent-backup', originalContent);
    
    // 应用智能修复
    const result = applyIntelligentFixes(filePath, fileErrors);
    
    if (result.content && result.content !== originalContent) {
      fs.writeFileSync(filePath, result.content);
      console.log(`✅ 智能修复完成: ${fileName}`);
      console.log(`   - 修复数量: ${result.fixCount}处`);
      if (result.appliedFixes.length > 0) {
        const uniqueFixes = [...new Set(result.appliedFixes)];
        console.log(`   - 修复类型: ${uniqueFixes.slice(0, 3).join(', ')}`);
      }
      return true;
    } else {
      console.log(`ℹ️  无法智能修复: ${fileName}`);
      return false;
    }
    
  } catch (error) {
    console.error(`❌ 智能修复失败: ${filePath} - ${error.message}`);
    return false;
  }
}

function main() {
  console.log('🧠 开始智能错误分析和修复...\n');
  
  // 获取详细错误信息
  console.log('📊 分析TypeScript错误...');
  const errors = getDetailedErrors();
  
  if (errors.length === 0) {
    console.log('🎉 没有发现TypeScript错误！');
    return;
  }
  
  // 分析错误
  const analysis = analyzeErrors(errors);
  
  console.log(`\n📈 错误分析结果:`);
  console.log(`   - 总错误数: ${analysis.total}`);
  console.log(`   - 错误类型数: ${Object.keys(analysis.byType).length}`);
  console.log(`   - 受影响文件数: ${Object.keys(analysis.byFile).length}`);
  
  console.log(`\n🔍 常见错误模式:`);
  for (const [pattern, count] of Object.entries(analysis.commonPatterns)) {
    console.log(`   - ${pattern}: ${count}个`);
  }
  
  console.log(`\n📋 错误类型分布 (Top 10):`);
  const sortedTypes = Object.entries(analysis.byType)
    .sort(([,a], [,b]) => b.length - a.length)
    .slice(0, 10);
  
  for (const [code, errorList] of sortedTypes) {
    console.log(`   - ${code}: ${errorList.length}个`);
  }
  
  // 选择错误最多的文件进行修复
  const sortedFiles = Object.entries(analysis.byFile)
    .sort(([,a], [,b]) => b.length - a.length)
    .slice(0, 10); // 只修复前10个错误最多的文件
  
  console.log(`\n🎯 开始修复错误最多的文件:`);
  
  let totalFixed = 0;
  let totalAttempted = 0;
  
  for (const [filePath, fileErrors] of sortedFiles) {
    totalAttempted++;
    if (fixFileIntelligently(filePath, fileErrors)) {
      totalFixed++;
    }
  }
  
  console.log(`\n📊 智能修复完成:`);
  console.log(`   - 尝试修复文件数: ${totalAttempted}`);
  console.log(`   - 成功修复文件数: ${totalFixed}`);
  console.log(`   - 修复率: ${((totalFixed / totalAttempted) * 100).toFixed(1)}%`);
  
  // 检查修复效果
  console.log(`\n🔍 检查修复效果...`);
  try {
    const newErrorCount = execSync('npx tsc --noEmit 2>&1 | grep -E "error TS[0-9]+" | wc -l', { encoding: 'utf8' }).trim();
    const reduction = analysis.total - parseInt(newErrorCount);
    console.log(`📈 修复前错误数: ${analysis.total}`);
    console.log(`📉 修复后错误数: ${newErrorCount}`);
    console.log(`🎯 减少错误数: ${reduction} (${((reduction / analysis.total) * 100).toFixed(1)}%)`);
  } catch (error) {
    console.log('⚠️  无法获取修复后错误数量');
  }
  
  console.log(`\n💡 提示: 原文件已备份为 .intelligent-backup 后缀`);
}

main(); 