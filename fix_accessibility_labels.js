#!/usr/bin/env node

/**
 * 索克生活项目 - 无障碍标签修复脚本
 * 批量修复项目中的 "TODO: 添加无障碍标签" 问题
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// 无障碍标签映射表
const accessibilityLabels = {
  // 按钮相关
  'onPress={onClose}': '关闭',
  'onPress={handleStartChat}': '开始聊天',
  'onPress={handleBookAppointment}': '预约挂号',
  'onPress={requestAllPermissions}': '请求所有权限',
  'onPress={testCamera}': '测试相机功能',
  'onPress={testVoiceRecognition}': '测试语音识别',
  'onPress={testLocation}': '测试定位功能',
  'onPress={testNotifications}': '测试通知功能',
  'onPress={createHealthReminders}': '创建健康提醒',
  'onPress={onRetryTest}': '重试测试',
  'onPress={onViewDetails}': '查看详情',
  'onPress={() => setSearchQuery("")}': '清除搜索',
  'onPress={() => resetConfig()}': '重置配置',
  'onPress={() => onInteraction?.("dismissError")}': '关闭错误提示',
  
  // 图标和图片
  'name="bug-report"': '错误报告图标',
  'name="shield-key"': '权限图标',
  'name="close"': '关闭图标',
  'name="account-search"': '搜索联系人图标',
  'name="cloud-upload"': '上传图标',
  'name="lock-closed"': '锁定图标',
  'name="share"': '分享图标',
  'name="shield-checkmark"': '安全验证图标',
  
  // 输入框和表单
  'rightIcon': '输入框右侧图标',
  'leftIcon': '输入框左侧图标',
  
  // 通用操作
  '取消': '取消操作',
  '确认': '确认操作',
  '上传': '上传文件',
  '下载': '下载文件',
  '保存': '保存数据',
  '删除': '删除项目',
  '编辑': '编辑内容',
  '添加': '添加新项目',
  '搜索': '搜索功能',
  '筛选': '筛选内容',
  '排序': '排序列表',
  '刷新': '刷新页面',
  '返回': '返回上一页',
  '前进': '前进到下一页',
  '播放': '播放媒体',
  '暂停': '暂停播放',
  '停止': '停止操作',
  '开始': '开始操作',
  '完成': '完成操作',
  '跳过': '跳过当前步骤',
  '重试': '重试操作',
  '帮助': '获取帮助',
  '设置': '打开设置',
  '更多': '更多选项',
  '收藏': '收藏项目',
  '分享': '分享内容',
  '复制': '复制内容',
  '粘贴': '粘贴内容',
  '撤销': '撤销操作',
  '重做': '重做操作'
};

// 智能推断无障碍标签
function inferAccessibilityLabel(line) {
  // 移除TODO注释
  let cleanLine = line.replace(/accessibilityLabel="TODO: 添加无障碍标签"\s*\/?>/, '');
  
  // 查找匹配的模式
  for (const [pattern, label] of Object.entries(accessibilityLabels)) {
    if (cleanLine.includes(pattern)) {
      return `accessibilityLabel="${label}"`;
    }
  }
  
  // 基于文本内容推断
  const textMatch = cleanLine.match(/<Text[^>]*>([^<]+)<\/Text>/);
  if (textMatch) {
    const text = textMatch[1].trim();
    if (text && text.length < 20) {
      return `accessibilityLabel="${text}"`;
    }
  }
  
  // 基于图标名称推断
  const iconMatch = cleanLine.match(/name="([^"]+)"/);
  if (iconMatch) {
    const iconName = iconMatch[1];
    const labelMap = {
      'close': '关闭',
      'check': '确认',
      'add': '添加',
      'remove': '删除',
      'edit': '编辑',
      'search': '搜索',
      'settings': '设置',
      'home': '首页',
      'back': '返回',
      'forward': '前进',
      'refresh': '刷新',
      'share': '分享',
      'download': '下载',
      'upload': '上传',
      'play': '播放',
      'pause': '暂停',
      'stop': '停止'
    };
    
    if (labelMap[iconName]) {
      return `accessibilityLabel="${labelMap[iconName]}"`;
    }
    
    return `accessibilityLabel="${iconName}图标"`;
  }
  
  // 默认标签
  return 'accessibilityLabel="操作按钮"';
}

// 修复文件中的无障碍标签
function fixAccessibilityLabels(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    let modified = false;
    
    const fixedLines = lines.map(line => {
      if (line.includes('accessibilityLabel="TODO: 添加无障碍标签"')) {
        const newLabel = inferAccessibilityLabel(line);
        const fixedLine = line.replace(
          /accessibilityLabel="TODO: 添加无障碍标签"\s*\/?>/,
          newLabel + ' />'
        );
        modified = true;
        console.log(`修复: ${path.basename(filePath)}`);
        console.log(`  原: ${line.trim()}`);
        console.log(`  新: ${fixedLine.trim()}`);
        return fixedLine;
      }
      return line;
    });
    
    if (modified) {
      fs.writeFileSync(filePath, fixedLines.join('\n'));
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`处理文件 ${filePath} 时出错:`, error.message);
    return false;
  }
}

// 主函数
function main() {
  console.log('🚀 开始修复索克生活项目中的无障碍标签...\n');
  
  // 查找所有需要修复的文件
  const patterns = [
    'src/**/*.tsx',
    'src/**/*.ts',
    'src/**/*.jsx',
    'src/**/*.js'
  ];
  
  let totalFiles = 0;
  let fixedFiles = 0;
  
  patterns.forEach(pattern => {
    const files = glob.sync(pattern, { ignore: ['node_modules/**', 'dist/**', 'build/**'] });
    
    files.forEach(file => {
      totalFiles++;
      if (fixAccessibilityLabels(file)) {
        fixedFiles++;
      }
    });
  });
  
  console.log(`\n✅ 修复完成!`);
  console.log(`📊 统计信息:`);
  console.log(`   - 扫描文件: ${totalFiles}`);
  console.log(`   - 修复文件: ${fixedFiles}`);
  console.log(`   - 修复率: ${((fixedFiles / totalFiles) * 100).toFixed(1)}%`);
}

// 运行脚本
if (require.main === module) {
  main();
}

module.exports = { fixAccessibilityLabels, inferAccessibilityLabel }; 