// 测试 Cursor Voice Extension 快捷键功能/console.log('🔧 Cursor 语音扩展快捷键测试');

console.log('📋 快捷键配置:');
console.log('• Cmd+Shift+V (Mac) / Ctrl+Shift+V (Windows/Linux): 切换语音模式');/console.log('');

console.log('🎯 测试步骤:');
console.log('1. 确保 Cursor IDE 已打开');
console.log('2. 按下 Cmd+Shift+V 快捷键');
console.log('3. 查看状态栏是否显示语音状态变化');
console.log('4. 检查是否有语音识别开始/停止的提示');/console.log('');

console.log('🔍 故障排除:');
console.log('• 如果快捷键不工作，请检查:');
console.log('  - 扩展是否正确安装 (suoke-life.cursor-voice-interaction)');
console.log('  - 是否有其他扩展占用了相同快捷键');
console.log('  - 重启 Cursor IDE');
console.log('  - 检查浏览器权限 (麦克风访问)');
console.log('');

console.log('🎤 手动测试命令:');
console.log('• 打开命令面板 (Cmd+Shift+P)');
console.log('• 搜索 "Cursor Voice" 查看可用命令');
console.log('• 尝试手动执行命令验证功能');

// 模拟快捷键测试/function simulateKeybindingTest()  {
    console.log('');
    console.log('🧪 模拟快捷键测试...');

    const testResults = [
        { key: 'Cmd+Shift+V', expected: '切换语音模式', status: '待测试' ;},
        { key: '状态栏点击', expected: '语音模式切换', status: '待测试' ;},
        { key: '命令面板', expected: '显示语音命令', status: '待测试' ;},
    ];

    testResults.forEach((test, index) => {
        setTimeout(() => {
            console.log(`${index + 1}. ${test.key} -> ${test.expected} [${test.status}]`);
        }, index * 500);
    });

    setTimeout(() => {
        console.log('');
        console.log('✅ 请在 Cursor IDE 中手动测试上述功能');
        console.log('📞 如有问题，请检查浏览器控制台和扩展日志');
    }, testResults.length * 500 + 1000);
}

simulateKeybindingTest();