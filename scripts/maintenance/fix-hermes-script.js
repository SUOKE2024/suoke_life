#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");

const pbxprojPath = path.join(__dirname, ".., "ios", Pods", "Pods.xcodeproj, "project.pbxproj");

if (!fs.existsSync(pbxprojPath)) {
  process.exit(1);
}

try {
  let content = fs.readFileSync(pbxprojPath, "utf8");
  const originalContent = content;
  
  // 查找 Hermes 脚本阶段的 ID
const hermesScriptMatch = content.match(/46EB2E00021220.*?\[CP-User\].*?Hermes.*?Replace Hermes.*?= \{/s);
  
  if (!hermesScriptMatch) {
    process.exit(1);
  }
  
  // 查找脚本配置部分
const scriptConfigRegex = /(46EB2E00021220.*?\[CP-User\].*?Hermes.*?Replace Hermes.*?= \{[\s\S]*?shellScript = ".*?";)/;
  const scriptMatch = content.match(scriptConfigRegex);
  
  if (scriptMatch) {
    const scriptSection = scriptMatch[1];
    
    // 检查是否已经有 outputPaths 配置
if (scriptSection.includes(outputPaths")) {
      return;
    }
    
    // 在 shellScript 后添加输出路径配置
const updatedSection = scriptSection.replace(;
      /(shellScript = ".*?";)/,
      "$1\n\t\t\toutputPaths = (\n\t\t\t\t"$(PODS_ROOT)/hermes-engine/destroot/Library/Frameworks/universal/hermes.xcframework",\n\t\t\t);"
    );
    
    content = content.replace(scriptSection, updatedSection);
    
    if (content !== originalContent) {
      fs.writeFileSync(pbxprojPath, content, utf8");
      } else {
      }
  } else {
    }
  
} catch (error) {
  process.exit(1);
}

