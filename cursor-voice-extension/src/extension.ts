import * as vscode from 'vscode';
import { VoiceRecognitionService } from './services/voiceRecognitionService';
import { VideoInteractionService } from './services/videoInteractionService';
import { AIAssistantService } from './services/aiAssistantService';

let voiceService: VoiceRecognitionService;
let videoService: VideoInteractionService;
let aiService: AIAssistantService;

export function activate(context: vscode.ExtensionContext) {
    console.log('Cursor Voice Interaction 扩展已激活');

    // 初始化服务
    voiceService = new VoiceRecognitionService();
    videoService = new VideoInteractionService();
    aiService = new AIAssistantService();

    // 注册命令
    const commands = [
        vscode.commands.registerCommand('cursor-voice.startVoiceRecognition', startVoiceRecognition),
        vscode.commands.registerCommand('cursor-voice.stopVoiceRecognition', stopVoiceRecognition),
        vscode.commands.registerCommand('cursor-voice.startVideoInteraction', startVideoInteraction),
        vscode.commands.registerCommand('cursor-voice.toggleVoiceMode', toggleVoiceMode),
    ];

    commands.forEach(command => context.subscriptions.push(command));

    // 创建状态栏项
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "🎤 语音";
    statusBarItem.command = 'cursor-voice.toggleVoiceMode';
    statusBarItem.tooltip = '点击切换语音模式';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // 监听配置变化
    vscode.workspace.onDidChangeConfiguration(event => {
        if (event.affectsConfiguration('cursor-voice')) {
            updateConfiguration();
        }
    });

    updateConfiguration();
}

async function startVoiceRecognition() {
    try {
        await voiceService.startRecognition();
        vscode.window.showInformationMessage('语音识别已开始');
        
        // 监听语音识别结果
        voiceService.onRecognitionResult(async (text: string) => {
            await handleVoiceCommand(text);
        });
    } catch (error) {
        vscode.window.showErrorMessage(`启动语音识别失败: ${error}`);
    }
}

async function stopVoiceRecognition() {
    try {
        await voiceService.stopRecognition();
        vscode.window.showInformationMessage('语音识别已停止');
    } catch (error) {
        vscode.window.showErrorMessage(`停止语音识别失败: ${error}`);
    }
}

async function startVideoInteraction() {
    try {
        await videoService.startVideoCapture();
        vscode.window.showInformationMessage('视频交互已开始');
        
        // 监听手势识别结果
        videoService.onGestureDetected((gesture: string) => {
            handleGestureCommand(gesture);
        });
    } catch (error) {
        vscode.window.showErrorMessage(`启动视频交互失败: ${error}`);
    }
}

async function toggleVoiceMode() {
    if (voiceService.isRecognizing()) {
        await stopVoiceRecognition();
    } else {
        await startVoiceRecognition();
    }
}

async function handleVoiceCommand(text: string) {
    console.log(`收到语音命令: ${text}`);
    
    try {
        // 使用 AI 助手解析语音命令
        const command = await aiService.parseVoiceCommand(text);
        await executeCommand(command);
    } catch (error) {
        console.error('处理语音命令失败:', error);
        vscode.window.showErrorMessage(`处理语音命令失败: ${error}`);
    }
}

function handleGestureCommand(gesture: string) {
    console.log(`检测到手势: ${gesture}`);
    
    switch (gesture) {
        case 'swipe_left':
            vscode.commands.executeCommand('workbench.action.previousEditor');
            break;
        case 'swipe_right':
            vscode.commands.executeCommand('workbench.action.nextEditor');
            break;
        case 'thumbs_up':
            vscode.commands.executeCommand('editor.action.formatDocument');
            break;
        case 'peace_sign':
            vscode.commands.executeCommand('workbench.action.files.save');
            break;
        default:
            console.log(`未识别的手势: ${gesture}`);
    }
}

async function executeCommand(command: any) {
    switch (command.type) {
        case 'file_operation':
            await handleFileOperation(command);
            break;
        case 'code_generation':
            await handleCodeGeneration(command);
            break;
        case 'navigation':
            await handleNavigation(command);
            break;
        case 'ai_chat':
            await handleAIChat(command);
            break;
        default:
            vscode.window.showWarningMessage(`未知命令类型: ${command.type}`);
    }
}

async function handleFileOperation(command: any) {
    switch (command.action) {
        case 'open':
            const uri = vscode.Uri.file(command.path);
            await vscode.window.showTextDocument(uri);
            break;
        case 'save':
            await vscode.commands.executeCommand('workbench.action.files.save');
            break;
        case 'new':
            await vscode.commands.executeCommand('workbench.action.files.newUntitledFile');
            break;
    }
}

async function handleCodeGeneration(command: any) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('没有活动的编辑器');
        return;
    }

    try {
        const generatedCode = await aiService.generateCode(command.prompt, editor.document.languageId);
        const position = editor.selection.active;
        await editor.edit(editBuilder => {
            editBuilder.insert(position, generatedCode);
        });
    } catch (error) {
        vscode.window.showErrorMessage(`代码生成失败: ${error}`);
    }
}

async function handleNavigation(command: any) {
    switch (command.action) {
        case 'goto_line':
            await vscode.commands.executeCommand('workbench.action.gotoLine');
            break;
        case 'find':
            await vscode.commands.executeCommand('actions.find');
            break;
        case 'replace':
            await vscode.commands.executeCommand('editor.action.startFindReplaceAction');
            break;
    }
}

async function handleAIChat(command: any) {
    try {
        const response = await aiService.chat(command.message);
        
        // 创建一个新的输出通道显示 AI 回复
        const outputChannel = vscode.window.createOutputChannel('Cursor AI Assistant');
        outputChannel.appendLine(`用户: ${command.message}`);
        outputChannel.appendLine(`AI: ${response}`);
        outputChannel.show();
        
        // 可选：使用语音合成播放回复
        if (vscode.workspace.getConfiguration('cursor-voice').get('enableVoiceFeedback')) {
            await voiceService.speak(response);
        }
    } catch (error) {
        vscode.window.showErrorMessage(`AI 对话失败: ${error}`);
    }
}

function updateConfiguration() {
    const config = vscode.workspace.getConfiguration('cursor-voice');
    const language = config.get<string>('language', 'zh-CN');
    const apiKey = config.get<string>('apiKey', '');
    const enableVideoGestures = config.get<boolean>('enableVideoGestures', false);

    voiceService.updateConfiguration({ language });
    aiService.updateConfiguration({ apiKey });
    videoService.updateConfiguration({ enableGestures: enableVideoGestures });
}

export function deactivate() {
    if (voiceService) {
        voiceService.dispose();
    }
    if (videoService) {
        videoService.dispose();
    }
    if (aiService) {
        aiService.dispose();
    }
} 