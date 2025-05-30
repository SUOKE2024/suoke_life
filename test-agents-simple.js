/**
 * 简单的智能体测试脚本
 */

async function testAgents() {
  console.log('🚀 开始测试索克生活四智能体系统...\n');

  try {
    // 动态导入智能体模块
    const { createAgent } = await import('./src/agents/index.ts');

    // 测试小艾智能体
    console.log('🤖 测试小艾智能体...');
    const xiaoai = await createAgent('xiaoai');
    await xiaoai.initialize();
    console.log(`✅ ${xiaoai.getName()} 初始化成功`);
    console.log(`   描述: ${xiaoai.getDescription()}`);

    // 测试小克智能体
    console.log('\n🛒 测试小克智能体...');
    const xiaoke = await createAgent('xiaoke');
    await xiaoke.initialize();
    console.log(`✅ ${xiaoke.getName()} 初始化成功`);
    console.log(`   描述: ${xiaoke.getDescription()}`);

    // 测试老克智能体
    console.log('\n📚 测试老克智能体...');
    const laoke = await createAgent('laoke');
    await laoke.initialize();
    console.log(`✅ ${laoke.getName()} 初始化成功`);
    console.log(`   描述: ${laoke.getDescription()}`);

    // 测试索儿智能体
    console.log('\n💝 测试索儿智能体...');
    const soer = await createAgent('soer');
    await soer.initialize();
    console.log(`✅ ${soer.getName()} 初始化成功`);
    console.log(`   描述: ${soer.getDescription()}`);

    // 测试基本交互
    console.log('\n🗣️ 测试基本交互...');
    
    const xiaoaiResponse = await xiaoai.processMessage('你好', { userId: 'test' });
    console.log(`小艾回复: ${xiaoaiResponse.success ? '✅ 成功' : '❌ 失败'}`);
    
    const xiaokeResponse = await xiaoke.processMessage('推荐服务', { userId: 'test' });
    console.log(`小克回复: ${xiaokeResponse.success ? '✅ 成功' : '❌ 失败'}`);
    
    const laokeResponse = await laoke.processMessage('学习知识', { userId: 'test' });
    console.log(`老克回复: ${laokeResponse.success ? '✅ 成功' : '❌ 失败'}`);
    
    const soerResponse = await soer.processMessage('生活建议', { userId: 'test' });
    console.log(`索儿回复: ${soerResponse.success ? '✅ 成功' : '❌ 失败'}`);

    // 清理资源
    console.log('\n🧹 清理资源...');
    await xiaoai.shutdown();
    await xiaoke.shutdown();
    await laoke.shutdown();
    await soer.shutdown();

    console.log('\n🎉 所有测试完成！索克生活四智能体系统运行正常。');

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.error('详细错误:', error);
  }
}

// 运行测试
testAgents(); 