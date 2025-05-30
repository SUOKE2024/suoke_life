/**
 * 单智能体测试脚本
 * 直接测试智能体实现，避免复杂的模块导入问题
 */

async function testSingleAgent() {
  console.log('🚀 开始测试单个智能体...\n');

  try {
    // 直接导入小艾智能体实现
    const { XiaoaiAgentImpl } = await import('./src/agents/xiaoai/XiaoaiAgentImpl.ts');
    
    console.log('🤖 测试小艾智能体...');
    const xiaoai = new XiaoaiAgentImpl();
    await xiaoai.initialize();
    
    console.log(`✅ ${xiaoai.getName()} 初始化成功`);
    console.log(`   描述: ${xiaoai.getDescription()}`);
    console.log(`   能力: ${xiaoai.getCapabilities().slice(0, 3).join(', ')}...`);
    
    // 测试基本交互
    console.log('\n🗣️ 测试基本交互...');
    const response = await xiaoai.processMessage('你好，我想了解一下我的健康状况', { 
      userId: 'test-user' 
    });
    
    console.log(`小艾回复: ${response.success ? '✅ 成功' : '❌ 失败'}`);
    if (response.success && response.data) {
      console.log(`   回复内容: ${response.data.response || '无回复内容'}`);
    }
    
    // 测试健康状态
    console.log('\n📊 测试智能体状态...');
    const status = await xiaoai.getHealthStatus();
    console.log(`小艾状态: ${status.status}`);
    
    // 清理资源
    console.log('\n🧹 清理资源...');
    await xiaoai.shutdown();
    
    console.log('\n🎉 小艾智能体测试完成！');
    
    return { success: true, agent: '小艾' };

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.error('详细错误:', error);
    return { success: false, error: error.message };
  }
}

// 运行测试
testSingleAgent(); 