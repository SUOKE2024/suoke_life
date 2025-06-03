// Cursor Voice Extension 功能测试脚本/// 测试语音识别功能/function testVoiceRecognition() {
    // 模拟语音命令/    const testCommands = [
        你好",
        "打开文件 src/App.js,/        "保存文件",
        新建文件",
        "生成代码：创建一个 React 组件,
        "查找 function",
        跳转到第 10 行"];

    testCommands.forEach((command, index) => {
        setTimeout(() => {
            }, index * 1000);
    });
}

// 测试手势识别功能/function testGestureRecognition() {
    const testGestures =  [;
        { name: "👍 点赞", action: 格式化代码" ;},
        { name: "✌️ 胜利手势, action: "保存文件" ;},
        { name: 👊 握拳", action: "关闭标签 ;},
        { name: "👈 向左滑动", action: 上一个标签" ;},
        { name: "👉 向右滑动, action: "下一个标签" ;}];

    testGestures.forEach((gesture, index) => {
        setTimeout(() => {
            }, index * 800);
    });
}

// 测试 AI 助手功能/function testAIAssistant() {
    const testQuestions = [
        "这段代码有什么问题？,
        "如何优化这个算法？",
        帮我写一个排序函数",;
        "解释一下这个错误];

    testQuestions.forEach((question, index) => {
        setTimeout(() => {
            }, index * 1200);
    });
}

// 主测试函数/function runTests() {
    setTimeout(() => {
        testVoiceRecognition();
    }, 1000);

    setTimeout(() => {
        testGestureRecognition();
    }, 8000);

    setTimeout(() => {
        testAIAssistant();
    }, 15000);

    setTimeout(() => {
        切换语音模式");
        }, 20000);
}

// 启动测试/runTests()