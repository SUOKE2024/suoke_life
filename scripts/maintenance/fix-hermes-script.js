#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🏃 修复 Hermes 构建脚本警告...\n');

const pbxprojPath = path.join(__dirname, '..', 'ios', 'Pods', 'Pods.xcodeproj', 'project.pbxproj');

if (!fs.existsSync(pbxprojPath)) {
  console.error('❌ 找不到 Pods project.pbxproj 文件');
  console.log('请确保已经运行了 pod install');
  process.exit(1);
}

try {
  let content = fs.readFileSync(pbxprojPath, 'utf8');
  const originalContent = content;
  
  // 查找 Hermes 脚本阶段的 ID
  const hermesScriptMatch = content.match(/46EB2E00021220.*?\[CP-User\].*?Hermes.*?Replace Hermes.*?= \{/s);
  
  if (!hermesScriptMatch) {
    console.log('❌ 找不到 Hermes 脚本阶段');
    console.log('脚本可能已经被修复或者结构发生了变化');
    process.exit(1);
  }
  
  console.log('✅ 找到 Hermes 脚本阶段');
  
  // 查找脚本配置部分
  const scriptConfigRegex = /(46EB2E00021220.*?\[CP-User\].*?Hermes.*?Replace Hermes.*?= \{[\s\S]*?shellScript = ".*?";)/;
  const scriptMatch = content.match(scriptConfigRegex);
  
  if (scriptMatch) {
    const scriptSection = scriptMatch[1];
    
    // 检查是否已经有 outputPaths 配置
    if (scriptSection.includes('outputPaths')) {
      console.log('✅ Hermes 脚本已经配置了输出路径');
      return;
    }
    
    // 在 shellScript 后添加输出路径配置
    const updatedSection = scriptSection.replace(
      /(shellScript = ".*?";)/,
      '$1\n\t\t\toutputPaths = (\n\t\t\t\t"$(PODS_ROOT)/hermes-engine/destroot/Library/Frameworks/universal/hermes.xcframework",\n\t\t\t);'
    );
    
    content = content.replace(scriptSection, updatedSection);
    
    if (content !== originalContent) {
      fs.writeFileSync(pbxprojPath, content, 'utf8');
      console.log('✅ 已为 Hermes 脚本添加输出路径配置');
      console.log('📝 修复内容：添加了 outputPaths 来消除构建警告');
      console.log('\n🔄 请重新构建项目以验证修复效果：');
      console.log('   npm run ios');
    } else {
      console.log('⚠️  没有进行任何修改');
    }
  } else {
    console.log('❌ 找不到 Hermes 脚本配置部分');
  }
  
} catch (error) {
  console.error('❌ 修复过程中出现错误:', error.message);
  process.exit(1);
}

console.log('\n📚 如果自动修复失败，请参考文档手动修复：');
console.log('   docs/HERMES_WARNING_FIX.md'); 