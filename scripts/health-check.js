#!/usr/bin/env node

/**
 * 索克生活 - 项目健康检查
 */

const fs = require('fs');
const { execSync } = require('child_process');

function checkProjectHealth() {
  const checks = [];
  
  // 检查依赖
  try {
    execSync('npm ls', { stdio: 'pipe' });
    checks.push({ name: '依赖完整性', status: '✅ 通过' });
  } catch (error) {
    checks.push({ name: '依赖完整性', status: '❌ 失败' });
  }
  
  // 检查TypeScript
  try {
    execSync('npx tsc --noEmit', { stdio: 'pipe' });
    checks.push({ name: 'TypeScript检查', status: '✅ 通过' });
  } catch (error) {
    checks.push({ name: 'TypeScript检查', status: '❌ 失败' });
  }
  
  // 检查ESLint
  try {
    execSync('npm run lint', { stdio: 'pipe' });
    checks.push({ name: 'ESLint检查', status: '✅ 通过' });
  } catch (error) {
    checks.push({ name: 'ESLint检查', status: '⚠️ 警告' });
  }
  
  // 检查测试
  try {
    execSync('npm test -- --passWithNoTests --watchAll=false', { stdio: 'pipe' });
    checks.push({ name: '测试运行', status: '✅ 通过' });
  } catch (error) {
    checks.push({ name: '测试运行', status: '❌ 失败' });
  }
  
  // 检查构建
  try {
    execSync('npm run build', { stdio: 'pipe' });
    checks.push({ name: '构建检查', status: '✅ 通过' });
  } catch (error) {
    checks.push({ name: '构建检查', status: '❌ 失败' });
  }
  
  console.log('\n🏥 索克生活项目健康检查报告');
  console.log('================================');
  checks.forEach(check => {
    console.log(`${check.name}: ${check.status}`);
  });
  console.log('================================\n');
  
  const passedChecks = checks.filter(c => c.status.includes('✅')).length;
  const totalChecks = checks.length;
  const healthScore = Math.round((passedChecks / totalChecks) * 100);
  
  console.log(`项目健康评分: ${healthScore}%`);
  
  if (healthScore >= 80) {
    console.log('🎉 项目状态良好！');
  } else if (healthScore >= 60) {
    console.log('⚠️ 项目需要一些改进');
  } else {
    console.log('🚨 项目需要紧急修复');
  }
}

checkProjectHealth();
