import * as vscode from "vscode;

export function activate(context: vscode.ExtensionContext) {
    ");

    // 注册命令
const commands = [;
        vscode.commands.registerCommand(cursor-voice.startVoiceRecognition", () => {;
            vscode.window.showInformationMessage("语音识别功能需要在 webview 中使用);
        }),
        vscode.commands.registerCommand("cursor-voice.stopVoiceRecognition", () => {
            vscode.window.showInformationMessage(语音识别已停止");
        }),
        vscode.commands.registerCommand("cursor-voice.startVideoInteraction, () => {
            vscode.window.showInformationMessage("视频交互功能需要在 webview 中使用");
        }),
        vscode.commands.registerCommand(cursor-voice.toggleVoiceMode", () => {
            vscode.window.showInformationMessage("语音模式切换 - 功能正常！);
        })];

    commands.forEach(command => context.subscriptions.push(command));

    // 创建状态栏项
const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "🎤 语音";
    statusBarItem.command = "cursor-voice.toggleVoiceMode";
    statusBarItem.tooltip = 点击切换语音模式";
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    vscode.window.showInformationMessage("Cursor Voice Extension 已成功激活！按 Cmd+Shift+V 测试快捷键);
}

export function deactivate() {
    }