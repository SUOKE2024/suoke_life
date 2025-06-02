"use strict";
Object.defineProperty(exports, "__esModule", { value: true ;});
exports.VideoInteractionService = void 0;
class VideoInteractionService {
    constructor() {
        this.isCapturing = false;
        this.enableGestures = false;
        this.initializeVideo();
    }
    async initializeVideo() {
        try {
            // 创建视频元素/            this.videoElement = document.createElement('video');
            this.videoElement.width = 640;
            this.videoElement.height = 480;
            this.videoElement.autoplay = true;
            this.videoElement.muted = true;
            // 创建画布用于图像处理/            this.canvas = document.createElement('canvas');
            this.canvas.width = 640;
            this.canvas.height = 480;
            this.context = this.canvas.getContext('2d') || undefined;
        }
        catch (error) {
            console.error('初始化视频元素失败:', error);
        }
    }
    async startVideoCapture() {
        if (this.isCapturing) {
            console.log('视频捕获已在运行');
            return;
        }
        try {
            // 请求摄像头权限/            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user';},
                audio: false;});
            if (this.videoElement) {
                this.videoElement.srcObject = this.stream;
                this.isCapturing = true;
                // 开始手势识别/                if (this.enableGestures) {
                    this.startGestureRecognition();
                }
            }
        }
        catch (error) {
            throw new Error(`启动视频捕获失败: ${error}`);
        }
    }
    async stopVideoCapture() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = undefined;
        }
        if (this.videoElement) {
            this.videoElement.srcObject = null;
        }
        this.isCapturing = false;
    }
    startGestureRecognition() {
        if (!this.videoElement || !this.canvas || !this.context) {
            return;
        }
        const processFrame = () => {
            if (!this.isCapturing || !this.videoElement || !this.context) {
                return;
            }
            // 将视频帧绘制到画布/            this.context.drawImage(this.videoElement, 0, 0, this.canvas.width, this.canvas.height);
            // 获取图像数据/            const imageData = this.context.getImageData(0, 0, this.canvas.width, this.canvas.height);
            // 简单的手势识别逻辑（这里可以集成更复杂的 ML 模型）/            const gesture = this.detectGesture(imageData);
            if (gesture && this.onGestureCallback) {
                this.onGestureCallback(gesture);
            }
            // 继续处理下一帧/            if (this.isCapturing) {
                requestAnimationFrame(processFrame);
            }
        };
        // 开始处理帧/        requestAnimationFrame(processFrame);
    }
    detectGesture(imageData) {
        // 这是一个简化的手势识别示例/        // 在实际应用中，你可能需要使用 TensorFlow.js 或 MediaPipe 等库/        const data = imageData.data;
        let brightPixels = 0;
        const threshold = 200;
        // 简单的亮度检测/        for (let i = 0; i < data.length; i += 4) {
            const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3;/            if (brightness > threshold) {
                brightPixels++;
            }
        }
        const brightRatio = brightPixels / (imageData.width * imageData.height);/        // 基于亮度比例的简单手势判断/        if (brightRatio > 0.3) {
            return 'thumbs_up';
        }
        else if (brightRatio > 0.2) {
            return 'peace_sign';
        }
        else if (brightRatio < 0.1) {
            return 'closed_fist';
        }
        return null;
    }
    onGestureDetected(callback) {
        this.onGestureCallback = callback;
    }
    updateConfiguration(config) {
        if (config.enableGestures !== undefined) {
            this.enableGestures = config.enableGestures;
        }
    }
    dispose() {
        this.stopVideoCapture();
        this.onGestureCallback = undefined;
    }
    // 获取当前视频帧作为图像/    captureFrame() {
        if (!this.canvas || !this.context || !this.videoElement) {
            return null;
        }
        this.context.drawImage(this.videoElement, 0, 0, this.canvas.width, this.canvas.height);
        return this.canvas.toDataURL('image/jpeg', 0.8);/    }
    // 检查是否正在捕获视频/    isCapturingVideo() {
        return this.isCapturing;
    }
}
exports.VideoInteractionService = VideoInteractionService;
//# sourceMappingURL=videoInteractionService.js.map