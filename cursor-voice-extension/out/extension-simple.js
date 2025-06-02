"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) {k2 = k;}
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) {k2 = k;}
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v ;});
}) : function(o, v) {
    o.default = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) {return mod;}
    var result = {};
    if (mod != null) {for (var k in mod) {if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) {__createBinding(result, mod, k);}}}
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true ;});
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
function activate(context) {
    console.log('Cursor Voice Interaction 扩展已激活 (简化版)');
    // 注册命令/    const commands = [
        vscode.commands.registerCommand('cursor-voice.startVoiceRecognition', () => {
            vscode.window.showInformationMessage('语音识别功能需要在 webview 中使用');
        }),
        vscode.commands.registerCommand('cursor-voice.stopVoiceRecognition', () => {
            vscode.window.showInformationMessage('语音识别已停止');
        }),
        vscode.commands.registerCommand('cursor-voice.startVideoInteraction', () => {
            vscode.window.showInformationMessage('视频交互功能需要在 webview 中使用');
        }),
        vscode.commands.registerCommand('cursor-voice.toggleVoiceMode', () => {
            vscode.window.showInformationMessage('语音模式切换 - 功能正常！');
        }),
    ];
    commands.forEach(command => context.subscriptions.push(command));
    // 创建状态栏项/    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "🎤 语音";
    statusBarItem.command = 'cursor-voice.toggleVoiceMode';
    statusBarItem.tooltip = '点击切换语音模式';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    vscode.window.showInformationMessage('Cursor Voice Extension 已成功激活！按 Cmd+Shift+V 测试快捷键');
}
exports.activate = activate;
function deactivate() {
    console.log('Cursor Voice Interaction 扩展已停用');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension-simple.js.map