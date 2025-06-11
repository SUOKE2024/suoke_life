#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const glob = require('glob');
console.log('🔧 修复对象字面量语法错误...');
// 需要修复的文件列表
const filesToFix = [
  'src/algorithms/knowledge/__tests__/TCMKnowledgeBase.test.ts',
  'src/algorithms/quality/__tests__/QualityController.test.tsx',
  'src/algorithms/quality/__tests__/QualityController.test.ts',
  'src/algorithms/config/AlgorithmConfig.tsx',
  'src/algorithms/__tests__/FiveDiagnosisEngine.test.ts',
  'src/algorithms/quality/QualityController.tsx',
  'src/algorithms/knowledge/TCMKnowledgeBase.ts'
];
let totalFixed = 0;
filesToFix.forEach(filePath => {
  if (fs.existsSync(filePath)) {
    console.log(`📝 修复文件: ${filePath}`);
    let content = fs.readFileSync(filePath, 'utf8');
    let fixCount = 0;
    // 修复对象字面量中的分号错误
    // 修复 {; 错误
    const beforeFix1 = content;
    content = content.replace(/\{\s*;/g, '{');
    if (content !== beforeFix1) {
      fixCount += (beforeFix1.match(/\{\s*;/g) || []).length;
    }
    // 修复 , 错误
    const beforeFix2 = content;
    content = content.replace(/,\s*;/g, ',');
    if (content !== beforeFix2) {
      fixCount += (beforeFix2.match(/,\s*;/g) || []).length;
    }
    // 修复对象属性后的分号错误 (属性: 值;)
    const beforeFix3 = content;
    content = content.replace(/:\s*([^,}\n]+);(\s*[}])/g, ': $1$2');
    if (content !== beforeFix3) {
      fixCount += (beforeFix3.match(/:\s*([^,}\n]+);(\s*[}])/g) || []).length;
    }
    // 修复对象最后一个属性的分号错误
    const beforeFix4 = content;
    content = content.replace(/([^:,{\s]+)\s*;\s*}/g, '$1\n}');
    if (content !== beforeFix4) {
      fixCount += (beforeFix4.match(/([^:,{\s]+)\s*;\s*}/g) || []).length;
    }
    // 修复嵌套对象的分号错误
    const beforeFix5 = content;
    content = content.replace(/}\s*;\s*}/g, '}\n}');
    if (content !== beforeFix5) {
      fixCount += (beforeFix5.match(/}\s*;\s*}/g) || []).length;
    }
    // 修复函数调用中的注释错误
    const beforeFix6 = content;
    content = content.replace(/FiveDiagnosisEngine\(\/\/ valid params\);/g, 'FiveDiagnosisEngine({});');
    if (content !== beforeFix6) {
      fixCount += (beforeFix6.match(/FiveDiagnosisEngine\(\/\/ valid params\);/g) || []).length;
    }
    // 修复 return {; 错误
    const beforeFix7 = content;
    content = content.replace(/return\s*\{\s*;/g, 'return {');
    if (content !== beforeFix7) {
      fixCount += (beforeFix7.match(/return\s*\{\s*;/g) || []).length;
    }
    // 修复属性名后的分号错误 (tongueAnalysis:;)
    const beforeFix8 = content;
    content = content.replace(/([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*;/g, '$1:');
    if (content !== beforeFix8) {
      fixCount += (beforeFix8.match(/([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*;/g) || []).length;
    }
    // 修复函数调用中的分号错误 (.filter(;)
    const beforeFix9 = content;
    content = content.replace(/\.filter\(\s*;/g, '.filter(');
    if (content !== beforeFix9) {
      fixCount += (beforeFix9.match(/\.filter\(\s*;/g) || []).length;
    }
    // 修复多行函数调用中的分号错误
    const beforeFix10 = content;
    content = content.replace(/symptom => pattern\.symptoms\.includes\(symptom\) \|\| pattern\.signs\.includes\(symptom\)\s*;/g, 
      'symptom => pattern.symptoms.includes(symptom) || pattern.signs.includes(symptom)');
    if (content !== beforeFix10) {
      fixCount += (beforeFix10.match(/symptom => pattern\.symptoms\.includes\(symptom\) \|\| pattern\.signs\.includes\(symptom\)\s*;/g) || []).length;
    }
    // 修复 || ; 错误 (config?.models?.syndromeClassification ||;)
    const beforeFix11 = content;
    content = content.replace(/\|\|\s*;/g, '||');
    if (content !== beforeFix11) {
      fixCount += (beforeFix11.match(/\|\|\s*;/g) || []).length;
    }
    // 修复数组中的分号错误 (issues: [;)
    const beforeFix12 = content;
    content = content.replace(/:\s*\[\s*;/g, ': [');
    if (content !== beforeFix12) {
      fixCount += (beforeFix12.match(/:\s*\[\s*;/g) || []).length;
    }
    // 修复箭头函数中的分号错误 (symptom =>;)
    const beforeFix13 = content;
    content = content.replace(/=>\s*;/g, '=>');
    if (content !== beforeFix13) {
      fixCount += (beforeFix13.match(/=>\s*;/g) || []).length;
    }
    if (fixCount > 0) {
      fs.writeFileSync(filePath, content);
      console.log(`  ✅ 修复了 ${fixCount} 个错误`);
      totalFixed += fixCount;
    } else {
      console.log(`  ✅ 无需修复`);
    }
  } else {
    console.log(`  ❌ 文件不存在: ${filePath}`);
  }
});
console.log(`\n📊 修复报告:`);
console.log(`✅ 总共修复了 ${totalFixed} 个对象字面量语法错误`); 
