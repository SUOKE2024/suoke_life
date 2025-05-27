export class VoiceRecognitionService {
    private recognition: any;
    private recognizing: boolean = false;
    private onResultCallback?: (text: string) => void;
    private speechSynthesis?: SpeechSynthesis;
    private language: string = 'zh-CN';

    constructor() {
        // 在 VS Code 扩展环境中，需要检查 window 对象是否存在
        if (typeof window !== 'undefined') {
            this.speechSynthesis = window.speechSynthesis;
            this.initializeRecognition();
        } else {
            console.log('语音功能在 VS Code 扩展环境中不可用，需要在 webview 中使用');
        }
    }

    private initializeRecognition() {
        // 检查浏览器是否支持语音识别
        if (typeof window === 'undefined') {
            console.log('window 对象不存在，语音识别不可用');
            return;
        }
        
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn('浏览器不支持语音识别');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = this.language;

        this.recognition.onstart = () => {
            console.log('语音识别已开始');
            this.recognizing = true;
        };

        this.recognition.onresult = (event: any) => {
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                }
            }

            if (finalTranscript && this.onResultCallback) {
                this.onResultCallback(finalTranscript.trim());
            }
        };

        this.recognition.onerror = (event: any) => {
            console.error('语音识别错误:', event.error);
            this.recognizing = false;
        };

        this.recognition.onend = () => {
            console.log('语音识别已结束');
            this.recognizing = false;
        };
    }

    async startRecognition(): Promise<void> {
        if (!this.recognition) {
            throw new Error('语音识别不可用');
        }

        if (this.recognizing) {
            console.log('语音识别已在运行');
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            throw new Error(`启动语音识别失败: ${error}`);
        }
    }

    async stopRecognition(): Promise<void> {
        if (this.recognition && this.recognizing) {
            this.recognition.stop();
        }
    }

    onRecognitionResult(callback: (text: string) => void): void {
        this.onResultCallback = callback;
    }

    isRecognizing(): boolean {
        return this.recognizing;
    }

    async speak(text: string): Promise<void> {
        return new Promise((resolve, reject) => {
            if (!this.speechSynthesis) {
                reject(new Error('语音合成不可用'));
                return;
            }

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = this.language;
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            utterance.onend = () => resolve();
            utterance.onerror = (event) => reject(new Error(`语音合成失败: ${event.error}`));

            this.speechSynthesis.speak(utterance);
        });
    }

    updateConfiguration(config: { language?: string }): void {
        if (config.language) {
            this.language = config.language;
            if (this.recognition) {
                this.recognition.lang = this.language;
            }
        }
    }

    dispose(): void {
        if (this.recognition && this.recognizing) {
            this.recognition.stop();
        }
        this.onResultCallback = undefined;
    }
} 