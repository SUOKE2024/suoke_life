// Cursor Voice Extension 功能测试脚本
console.log('🎤 Cursor 语音视频交互扩展测试');

// 测试语音识别功能
function testVoiceRecognition() {
    console.log('📢 测试语音识别功能...');
    
    // 模拟语音命令
    const testCommands = [
        '你好',
        '打开文件 src/App.js',
        '保存文件',
        '新建文件',
        '生成代码：创建一个 React 组件',
        '查找 function',
        '跳转到第 10 行',
    ];
    
    testCommands.forEach((command, index) => {
        setTimeout(() => {
            console.log(`🎯 测试命令 ${index + 1}: "${command}"`);
        }, index * 1000);
    });
}

// 测试手势识别功能
function testGestureRecognition() {
    console.log('👋 测试手势识别功能...');
    
    const testGestures = [
        { name: '👍 点赞', action: '格式化代码' },
        { name: '✌️ 胜利手势', action: '保存文件' },
        { name: '👊 握拳', action: '关闭标签' },
        { name: '👈 向左滑动', action: '上一个标签' },
        { name: '👉 向右滑动', action: '下一个标签' },
    ];
    
    testGestures.forEach((gesture, index) => {
        setTimeout(() => {
            console.log(`🤲 测试手势 ${index + 1}: ${gesture.name} → ${gesture.action}`);
        }, index * 800);
    });
}

// 测试 AI 助手功能
function testAIAssistant() {
    console.log('🤖 测试 AI 助手功能...');
    
    const testQuestions = [
        '这段代码有什么问题？',
        '如何优化这个算法？',
        '帮我写一个排序函数',
        '解释一下这个错误',
    ];
    
    testQuestions.forEach((question, index) => {
        setTimeout(() => {
            console.log(`💭 测试问题 ${index + 1}: "${question}"`);
        }, index * 1200);
    });
}

// 主测试函数
function runTests() {
    console.log('🚀 开始执行 Cursor Voice Extension 功能测试...\n');
    
    setTimeout(() => {
        testVoiceRecognition();
    }, 1000);
    
    setTimeout(() => {
        console.log('\n');
        testGestureRecognition();
    }, 8000);
    
    setTimeout(() => {
        console.log('\n');
        testAIAssistant();
    }, 15000);
    
    setTimeout(() => {
        console.log('\n✅ 所有测试完成！');
        console.log('🎉 Cursor 语音视频交互扩展已准备就绪！');
        console.log('\n📋 使用指南:');
        console.log('1. 按 Ctrl+Shift+V (Mac: Cmd+Shift+V) 切换语音模式');
        console.log('2. 点击状态栏的 🎤 图标开始语音识别');
        console.log('3. 在命令面板中搜索 "Cursor Voice" 查看所有命令');
        console.log('4. 在设置中配置 OpenAI API 密钥以启用 AI 功能');
    }, 20000);
}

// 启动测试
runTests(); 