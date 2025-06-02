import OpenAI from 'openai';

interface VoiceCommand {
    type: 'file_operation' | 'code_generation' | 'navigation' | 'ai_chat';
    action?: string;
    prompt?: string;
    message?: string;
    path?: string;
}

export class AIAssistantService {
    private openai?: OpenAI;
    private apiKey: string = '';

    constructor() {
        this.initializeOpenAI();
    }

    private initializeOpenAI(): void {
        if (this.apiKey) {
            this.openai = new OpenAI({
                apiKey: this.apiKey,
                dangerouslyAllowBrowser: true // 注意：在生产环境中不建议这样做
            });
        }
    }

    async parseVoiceCommand(text: string): Promise<VoiceCommand> {
        // 简单的命令解析逻辑
        const lowerText = text.toLowerCase();

        // 文件操作命令
        if (lowerText.includes('打开文件') || lowerText.includes('open file')) {
            return {
                type: 'file_operation',
                action: 'open',
                path: this.extractFilePath(text)
            };
        }

        if (lowerText.includes('保存') || lowerText.includes('save')) {
            return {
                type: 'file_operation',
                action: 'save'
            };
        }

        if (lowerText.includes('新建文件') || lowerText.includes('new file')) {
            return {
                type: 'file_operation',
                action: 'new'
            };
        }

        // 导航命令
        if (lowerText.includes('跳转到') || lowerText.includes('goto')) {
            return {
                type: 'navigation',
                action: 'goto_line'
            };
        }

        if (lowerText.includes('查找') || lowerText.includes('find')) {
            return {
                type: 'navigation',
                action: 'find'
            };
        }

        if (lowerText.includes('替换') || lowerText.includes('replace')) {
            return {
                type: 'navigation',
                action: 'replace'
            };
        }

        // 代码生成命令
        if (lowerText.includes('生成代码') || lowerText.includes('generate code') || 
            lowerText.includes('写一个') || lowerText.includes('create function')) {
            return {
                type: 'code_generation',
                prompt: text
            };
        }

        // 默认为 AI 对话
        return {
            type: 'ai_chat',
            message: text
        };
    }

    private extractFilePath(text: string): string {
        // 简单的文件路径提取逻辑
        const pathMatch = text.match(/["']([^"']+)["']/);
        return pathMatch ? pathMatch[1] : '';
    }

    async generateCode(prompt: string, language: string): Promise<string> {
        if (!this.openai) {
            throw new Error('OpenAI 未初始化，请检查 API 密钥');
        }

        try {
            const response = await this.openai.chat.completions.create({
                model: 'gpt-3.5-turbo',
                messages: [
                    {
                        role: 'system',
                        content: `你是一个专业的${language}程序员。请根据用户的要求生成简洁、高质量的代码。只返回代码，不要包含解释。`
                    },
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                max_tokens: 1000,
                temperature: 0.7
            });

            return response.choices[0]?.message?.content || '';
        } catch (error) {
            throw new Error(`代码生成失败: ${error}`);
        }
    }

    async chat(message: string): Promise<string> {
        if (!this.openai) {
            // 如果没有 OpenAI，返回简单的回复
            return this.getSimpleResponse(message);
        }

        try {
            const response = await this.openai.chat.completions.create({
                model: 'gpt-3.5-turbo',
                messages: [
                    {
                        role: 'system',
                        content: '你是 Cursor IDE 的智能助手，专门帮助用户进行代码开发和编程相关的问题。请用中文回答。'
                    },
                    {
                        role: 'user',
                        content: message
                    }
                ],
                max_tokens: 500,
                temperature: 0.7
            });

            return response.choices[0]?.message?.content || '抱歉，我无法理解您的问题。';
        } catch (error) {
            console.error('AI 对话失败:', error);
            return this.getSimpleResponse(message);
        }
    }

    private getSimpleResponse(message: string): string {
        const lowerMessage = message.toLowerCase();

        if (lowerMessage.includes('你好') || lowerMessage.includes('hello')) {
            return '你好！我是 Cursor 的语音助手，有什么可以帮助您的吗？';
        }

        if (lowerMessage.includes('帮助') || lowerMessage.includes('help')) {
            return '我可以帮您：\n1. 语音控制文件操作\n2. 生成代码\n3. 导航和搜索\n4. 回答编程问题';
        }

        if (lowerMessage.includes('谢谢') || lowerMessage.includes('thank')) {
            return '不客气！随时为您服务。';
        }

        return '我正在学习中，请尝试更具体的指令，比如"打开文件"、"生成代码"或"保存文件"。';
    }

    updateConfiguration(config: { apiKey?: string }): void {
        if (config.apiKey) {
            this.apiKey = config.apiKey;
            this.initializeOpenAI();
        }
    }

    dispose(): void {
        this.openai = undefined;
    }

    // 检查 AI 服务是否可用
    isAvailable(): boolean {
        return !!this.openai;
    }

    // 获取支持的命令列表
    getSupportedCommands(): string[] {
        return [
            '打开文件 "文件路径"',
            '保存文件',
            '新建文件',
            '生成代码：创建一个函数',
            '查找文本',
            '替换文本',
            '跳转到行号',
            '格式化代码',
            '运行代码'
        ];
    }
} 