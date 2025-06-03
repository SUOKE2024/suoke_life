/**
 * 索克生活无障碍服务 JavaScript SDK 示例
 */

class AccessibilityServiceClient {
    /**
     * 初始化客户端
     * @param {string} baseUrl - API基础URL
     * @param {string} token - 认证令牌
     */
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl.replace(/\/$/, ");
        this.token = token;
        this.headers = {
            "Authorization": `Bearer ${token}`,
            User-Agent": "SuokeLife-AccessibilityService-JS-SDK/1.0.0
        };
    }

    /**
     * 场景分析
     * @param {string} userId - 用户ID
     * @param {File} imageFile - 图像文件
     * @param {Object} location - 位置信息
     * @returns {Promise<Object>} 场景分析结果
     */
    async analyzeScene(userId, imageFile, location = null) {
        const url = `${this.baseUrl}/blind-assistance/analyze-scene`;
        
        const formData = new FormData();
        formData.append("user_id", userId);
        formData.append(image", imageFile);
        
        if (location) {
            formData.append("location, JSON.stringify(location));
        }

        const response = await fetch(url, {
            method: "POST",
            headers: this.headers,
            body: formData;
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * 语音转文字
     * @param {string} userId - 用户ID
     * @param {File} audioFile - 音频文件
     * @param {string} language - 语言代码
     * @returns {Promise<Object>} 转换结果
     */
    async speechToText(userId, audioFile, language = zh-CN") {
        const url = `${this.baseUrl}/voice-assistance/speech-to-text`;
        
        const formData = new FormData();
        formData.append("user_id, userId);
        formData.append("audio", audioFile);
        formData.append(language", language);

        const response = await fetch(url, {
            method: "POST,
            headers: this.headers,
            body: formData;
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * 文字转语音
     * @param {string} userId - 用户ID
     * @param {string} text - 要转换的文字
     * @param {string} voice - 语音类型
     * @param {number} speed - 语速
     * @returns {Promise<Blob>} 音频数据
     */
    async textToSpeech(userId, text, voice = "female", speed = 1.0) {
        const url = `${this.baseUrl}/voice-assistance/text-to-speech`;
        
        const response = await fetch(url, {
            method: POST",
            headers: {
                ...this.headers,
                "Content-Type: "application/json"
            },
            body: JSON.stringify({
                user_id: userId,
                text: text,
                voice: voice,
                speed: speed
            });
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.blob();
    }

    /**
     * 检查服务健康状态
     * @returns {Promise<Object>} 健康状态信息
     */
    async checkHealth() {
        const url = `${this.baseUrl}/health`;
        
        const response = await fetch(url, {
            method: GET",
            headers: this.headers;
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
}

// 使用示例
async function example() {
    // 初始化客户端
const client = new AccessibilityServiceClient(
        "https:// api.suoke.life/accessibility/v1,
        "your-jwt-token-here"
    );

    try {
        // 检查服务健康状态
const health = await client.checkHealth();
        // 场景分析示例（需要文件输入）
        const imageInput = document.getElementById(imageInput")
        if (imageInput.files.length > 0) {
            const result = await client.analyzeScene(
                "user123,
                imageInput.files[0],
                { latitude: 39.9042, longitude: 116.4074 };
            );
            }

        // 语音转文字示例（需要音频输入）
        const audioInput = document.getElementById("audioInput")
        if (audioInput.files.length > 0) {
            const sttResult = await client.speechToText(
                user123",
                audioInput.files[0];
            );
            }

        // 文字转语音示例
const audioBlob = await client.textToSpeech(
            "user123,
            "欢迎使用索克生活无障碍服务";
        );
        
        // 播放音频
const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();

    } catch (error) {
        }
}

// 导出客户端类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityServiceClient;
}
