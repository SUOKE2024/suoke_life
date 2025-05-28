#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 索克生活设备功能验证');
console.log('==========================');

// 验证结果存储
const validationResults = {
  timestamp: new Date().toISOString(),
  platform: process.platform,
  tests: [],
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    warnings: 0
  }
};

// 添加测试结果
function addTestResult(name, status, details = '', recommendation = '') {
  const result = {
    name,
    status, // 'pass', 'fail', 'warning'
    details,
    recommendation,
    timestamp: new Date().toISOString()
  };
  
  validationResults.tests.push(result);
  validationResults.summary.total++;
  
  if (status === 'pass') {
    validationResults.summary.passed++;
    console.log(`✅ ${name}: ${details}`);
  } else if (status === 'fail') {
    validationResults.summary.failed++;
    console.log(`❌ ${name}: ${details}`);
    if (recommendation) {
      console.log(`   💡 建议: ${recommendation}`);
    }
  } else if (status === 'warning') {
    validationResults.summary.warnings++;
    console.log(`⚠️  ${name}: ${details}`);
    if (recommendation) {
      console.log(`   💡 建议: ${recommendation}`);
    }
  }
}

// 1. 验证项目结构
function validateProjectStructure() {
  console.log('\n📁 验证项目结构...');
  
  const requiredFiles = [
    'src/utils/deviceInfo.ts',
    'src/utils/performanceMonitor.ts',
    'src/utils/deviceIntegrationTest.ts',
    'src/components/common/DeviceTestDashboard.tsx',
    'package.json',
    'app.json'
  ];
  
  requiredFiles.forEach(file => {
    if (fs.existsSync(file)) {
      addTestResult(`文件存在: ${file}`, 'pass', '文件结构正确');
    } else {
      addTestResult(`文件缺失: ${file}`, 'fail', '关键文件不存在', '检查文件路径或重新创建');
    }
  });
}

// 2. 验证依赖安装
function validateDependencies() {
  console.log('\n📦 验证依赖安装...');
  
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const requiredDeps = [
    'react-native-device-info',
    'react-native-permissions',
    'react-native-vision-camera',
    'react-native-voice',
    '@react-native-community/geolocation',
    'react-native-push-notification'
  ];
  
  const allDeps = { ...packageJson.dependencies, ...packageJson.devDependencies };
  
  requiredDeps.forEach(dep => {
    if (allDeps[dep]) {
      addTestResult(`依赖已安装: ${dep}`, 'pass', `版本: ${allDeps[dep]}`);
    } else {
      addTestResult(`依赖缺失: ${dep}`, 'fail', '必要依赖未安装', `运行: npm install ${dep}`);
    }
  });
}

// 3. 验证TypeScript编译
function validateTypeScript() {
  console.log('\n🔧 验证TypeScript编译...');
  
  try {
    execSync('npx tsc --noEmit --skipLibCheck', { stdio: 'pipe' });
    addTestResult('TypeScript编译', 'pass', '所有类型检查通过');
  } catch (error) {
    const errorOutput = error.stdout ? error.stdout.toString() : error.message;
    addTestResult('TypeScript编译', 'fail', '类型检查失败', '修复TypeScript错误');
    console.log('   错误详情:', errorOutput.slice(0, 500));
  }
}

// 4. 验证原生配置
function validateNativeConfiguration() {
  console.log('\n📱 验证原生配置...');
  
  // 检查Android配置
  const androidManifest = 'android/app/src/main/AndroidManifest.xml';
  if (fs.existsSync(androidManifest)) {
    const manifestContent = fs.readFileSync(androidManifest, 'utf8');
    
    // 检查权限
    const requiredPermissions = [
      'android.permission.CAMERA',
      'android.permission.RECORD_AUDIO',
      'android.permission.ACCESS_FINE_LOCATION'
    ];
    
    requiredPermissions.forEach(permission => {
      if (manifestContent.includes(permission)) {
        addTestResult(`Android权限: ${permission}`, 'pass', '权限已配置');
      } else {
        addTestResult(`Android权限: ${permission}`, 'warning', '权限未配置', '添加到AndroidManifest.xml');
      }
    });
  } else {
    addTestResult('Android配置', 'fail', 'AndroidManifest.xml不存在', '检查Android项目结构');
  }
  
  // 检查iOS配置
  const iosInfoPlist = 'ios/SuokeLife/Info.plist';
  if (fs.existsSync(iosInfoPlist)) {
    const plistContent = fs.readFileSync(iosInfoPlist, 'utf8');
    
    // 检查权限描述
    const requiredKeys = [
      'NSCameraUsageDescription',
      'NSMicrophoneUsageDescription',
      'NSLocationWhenInUseUsageDescription'
    ];
    
    requiredKeys.forEach(key => {
      if (plistContent.includes(key)) {
        addTestResult(`iOS权限: ${key}`, 'pass', '权限描述已配置');
      } else {
        addTestResult(`iOS权限: ${key}`, 'warning', '权限描述未配置', '添加到Info.plist');
      }
    });
  } else {
    addTestResult('iOS配置', 'fail', 'Info.plist不存在', '检查iOS项目结构');
  }
}

// 5. 验证测试脚本
function validateTestScripts() {
  console.log('\n🧪 验证测试脚本...');
  
  const testScripts = [
    'test:native',
    'test:device',
    'test:device:android',
    'test:device:ios'
  ];
  
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  
  testScripts.forEach(script => {
    if (packageJson.scripts && packageJson.scripts[script]) {
      addTestResult(`测试脚本: ${script}`, 'pass', '脚本已配置');
    } else {
      addTestResult(`测试脚本: ${script}`, 'fail', '测试脚本缺失', '添加到package.json scripts');
    }
  });
}

// 6. 验证设备连接
function validateDeviceConnection() {
  console.log('\n📱 验证设备连接...');
  
  try {
    // 检查Android设备
    const adbDevices = execSync('adb devices', { encoding: 'utf8' });
    const androidDevices = adbDevices.split('\n').filter(line => line.includes('\tdevice')).length;
    
    if (androidDevices > 0) {
      addTestResult('Android设备连接', 'pass', `${androidDevices}个设备已连接`);
    } else {
      addTestResult('Android设备连接', 'warning', '无Android设备连接', '连接Android设备或启动模拟器');
    }
    
    // 检查iOS设备
    if (process.platform === 'darwin') {
      try {
        const xcrunDevices = execSync('xcrun simctl list devices | grep "Booted"', { encoding: 'utf8' });
        const iosDevices = xcrunDevices.split('\n').filter(line => line.trim()).length;
        
        if (iosDevices > 0) {
          addTestResult('iOS设备连接', 'pass', `${iosDevices}个设备/模拟器已启动`);
        } else {
          addTestResult('iOS设备连接', 'warning', '无iOS设备连接', '启动iOS模拟器');
        }
      } catch (error) {
        addTestResult('iOS设备连接', 'warning', '无iOS设备连接', '启动iOS模拟器');
      }
    }
  } catch (error) {
    addTestResult('设备连接检查', 'fail', '无法检查设备连接', '确保开发工具已安装');
  }
}

// 7. 性能基准测试
function validatePerformanceBenchmarks() {
  console.log('\n⚡ 验证性能基准...');
  
  // 检查性能监控文件大小
  const perfMonitorFile = 'src/utils/performanceMonitor.ts';
  if (fs.existsSync(perfMonitorFile)) {
    const stats = fs.statSync(perfMonitorFile);
    const sizeKB = Math.round(stats.size / 1024);
    
    if (sizeKB < 100) {
      addTestResult('性能监控文件大小', 'pass', `${sizeKB}KB - 合理大小`);
    } else {
      addTestResult('性能监控文件大小', 'warning', `${sizeKB}KB - 文件较大`, '考虑代码分割');
    }
  }
  
  // 检查测试文件复杂度
  const testFile = 'src/utils/deviceIntegrationTest.ts';
  if (fs.existsSync(testFile)) {
    const content = fs.readFileSync(testFile, 'utf8');
    const lineCount = content.split('\n').length;
    
    if (lineCount < 1000) {
      addTestResult('测试文件复杂度', 'pass', `${lineCount}行 - 合理复杂度`);
    } else {
      addTestResult('测试文件复杂度', 'warning', `${lineCount}行 - 文件较复杂`, '考虑模块化');
    }
  }
}

// 8. 生成优化建议
function generateOptimizationRecommendations() {
  console.log('\n💡 生成优化建议...');
  
  const recommendations = [];
  
  // 基于测试结果生成建议
  const failedTests = validationResults.tests.filter(t => t.status === 'fail');
  const warningTests = validationResults.tests.filter(t => t.status === 'warning');
  
  if (failedTests.length > 0) {
    recommendations.push('🔴 立即修复失败的测试项目');
    failedTests.forEach(test => {
      if (test.recommendation) {
        recommendations.push(`   - ${test.name}: ${test.recommendation}`);
      }
    });
  }
  
  if (warningTests.length > 0) {
    recommendations.push('🟡 考虑优化警告项目');
    warningTests.forEach(test => {
      if (test.recommendation) {
        recommendations.push(`   - ${test.name}: ${test.recommendation}`);
      }
    });
  }
  
  // 通用优化建议
  recommendations.push('🚀 性能优化建议:');
  recommendations.push('   - 定期运行集成测试');
  recommendations.push('   - 监控应用启动时间');
  recommendations.push('   - 优化内存使用');
  recommendations.push('   - 实施代码分割');
  recommendations.push('   - 使用懒加载策略');
  
  return recommendations;
}

// 生成详细报告
function generateDetailedReport() {
  const recommendations = generateOptimizationRecommendations();
  
  const report = `
# 索克生活设备功能验证报告

## 📊 验证概览
- **验证时间**: ${validationResults.timestamp}
- **平台**: ${validationResults.platform}
- **总测试数**: ${validationResults.summary.total}
- **通过**: ${validationResults.summary.passed}
- **失败**: ${validationResults.summary.failed}
- **警告**: ${validationResults.summary.warnings}
- **通过率**: ${((validationResults.summary.passed / validationResults.summary.total) * 100).toFixed(1)}%

## 📋 详细测试结果

${validationResults.tests.map(test => {
  const icon = test.status === 'pass' ? '✅' : test.status === 'fail' ? '❌' : '⚠️';
  let result = `### ${icon} ${test.name}\n- **状态**: ${test.status}\n- **详情**: ${test.details}`;
  if (test.recommendation) {
    result += `\n- **建议**: ${test.recommendation}`;
  }
  return result;
}).join('\n\n')}

## 💡 优化建议

${recommendations.join('\n')}

## 🎯 下一步行动

### 立即执行
1. 修复所有失败的测试项目
2. 解决关键的警告项目
3. 确保设备连接正常
4. 运行完整的集成测试

### 短期优化 (1-2周)
1. 优化应用启动时间
2. 实施内存管理最佳实践
3. 添加更多性能监控指标
4. 完善错误处理机制

### 中期规划 (1-3个月)
1. 集成到CI/CD流程
2. 实施自动化性能测试
3. 添加更多设备兼容性测试
4. 优化用户体验

---
**报告生成时间**: ${new Date().toLocaleString()}
**验证工具版本**: 1.0.0
  `;
  
  // 保存报告
  const reportPath = path.join(process.cwd(), 'DEVICE_VALIDATION_REPORT.md');
  fs.writeFileSync(reportPath, report.trim());
  
  console.log(`\n📄 详细报告已保存: ${reportPath}`);
  
  return report;
}

// 主验证流程
async function runValidation() {
  try {
    console.log('🚀 开始设备功能验证...\n');
    
    validateProjectStructure();
    validateDependencies();
    validateTypeScript();
    validateNativeConfiguration();
    validateTestScripts();
    validateDeviceConnection();
    validatePerformanceBenchmarks();
    
    console.log('\n📊 验证总结:');
    console.log(`   总测试数: ${validationResults.summary.total}`);
    console.log(`   ✅ 通过: ${validationResults.summary.passed}`);
    console.log(`   ❌ 失败: ${validationResults.summary.failed}`);
    console.log(`   ⚠️  警告: ${validationResults.summary.warnings}`);
    console.log(`   📈 通过率: ${((validationResults.summary.passed / validationResults.summary.total) * 100).toFixed(1)}%`);
    
    generateDetailedReport();
    
    // 返回验证状态
    const success = validationResults.summary.failed === 0;
    console.log(`\n🎯 验证${success ? '成功' : '失败'}！`);
    
    if (!success) {
      console.log('💡 请查看详细报告并修复失败的项目');
      process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ 验证过程中发生错误:', error);
    process.exit(1);
  }
}

// 运行验证
runValidation(); 