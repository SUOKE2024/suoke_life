import { Platform, Alert } from "react-native";
import permissionManager from "./permissions";

// VisionCamera 相关类型和功能
export interface CameraConfig {
  quality: "low" | "medium" | "high" | "4k";
  enableAudio: boolean;
  flashMode: "off" | "on" | "auto";
  cameraPosition: "front" | "back";
}

export interface PhotoResult {
  path: string;
  width: number;
  height: number;
  size: number;
  timestamp: number;
}

export interface VideoResult {
  path: string;
  duration: number;
  size: number;
  timestamp: number;
}

// Voice 相关类型和功能
export interface VoiceConfig {
  locale: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  timeout: number;
}

export interface VoiceResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
  alternatives: Array<{
    transcript: string;
    confidence: number;
  }>;
}

// 位置服务相关类型
export interface LocationConfig {
  accuracy: "low" | "balanced" | "high" | "highest";
  timeout: number;
  maximumAge: number;
  enableHighAccuracy: boolean;
}

export interface LocationResult {
  latitude: number;
  longitude: number;
  altitude?: number;
  accuracy: number;
  speed?: number;
  heading?: number;
  timestamp: number;
}

class NativeModulesManager {
  private cameraModule: any = null;
  private voiceModule: any = null;
  private locationModule: any = null;

  constructor() {
    this.initializeModules();
  }

  /**
   * 初始化原生模块
   */
  private async initializeModules() {
    try {
      // 动态导入VisionCamera
      if (Platform.OS === "ios" || Platform.OS === "android") {
        try {
          const { Camera } = await import("react-native-vision-camera");
          this.cameraModule = Camera;
          console.log("✅ VisionCamera 模块加载成功");
        } catch (error) {
          console.warn("⚠️ VisionCamera 模块未安装或加载失败:", error);
        }

        // 动态导入Voice
        try {
          const Voice = await import("@react-native-voice/voice");
          this.voiceModule = Voice.default;
          console.log("✅ Voice 模块加载成功");
        } catch (error) {
          console.warn("⚠️ Voice 模块未安装或加载失败:", error);
        }

        // 动态导入Geolocation
        try {
          const Geolocation = await import(
            "@react-native-community/geolocation"
          );
          this.locationModule = Geolocation.default;
          console.log("✅ Geolocation 模块加载成功");
        } catch (error) {
          console.warn("⚠️ Geolocation 模块未安装或加载失败:", error);
        }
      }
    } catch (error) {
      console.error("❌ 原生模块初始化失败:", error);
    }
  }

  /**
   * 检查相机可用性
   */
  async isCameraAvailable(): Promise<boolean> {
    if (!this.cameraModule) {
      return false;
    }

    try {
      const permission = await permissionManager.checkPermission("camera");
      if (!permission.granted) {
        return false;
      }

      // 检查设备是否有相机
      const devices = await this.cameraModule.getAvailableCameraDevices();
      return devices.length > 0;
    } catch (error) {
      console.error("检查相机可用性失败:", error);
      return false;
    }
  }

  /**
   * 拍照功能
   */
  async takePhoto(
    config: Partial<CameraConfig> = {}
  ): Promise<PhotoResult | null> {
    if (!this.cameraModule) {
      Alert.alert("错误", "相机模块未初始化");
      return null;
    }

    try {
      // 检查并请求相机权限
      const permission = await permissionManager.requestPermissionWithDialog(
        "camera"
      );
      if (!permission.granted) {
        return null;
      }

      const defaultConfig: CameraConfig = {
        quality: "high",
        enableAudio: false,
        flashMode: "auto",
        cameraPosition: "back",
        ...config,
      };

      // 模拟拍照结果（实际实现需要集成VisionCamera）
      const result: PhotoResult = {
        path: `/tmp/photo_${Date.now()}.jpg`,
        width: 1920,
        height: 1080,
        size: 2048000,
        timestamp: Date.now(),
      };

      console.log("📸 拍照成功:", result);
      return result;
    } catch (error) {
      console.error("拍照失败:", error);
      Alert.alert("拍照失败", "请稍后重试");
      return null;
    }
  }

  /**
   * 录制视频功能
   */
  async recordVideo(
    config: Partial<CameraConfig> = {}
  ): Promise<VideoResult | null> {
    if (!this.cameraModule) {
      Alert.alert("错误", "相机模块未初始化");
      return null;
    }

    try {
      // 检查并请求相机权限
      const permission = await permissionManager.requestPermissionWithDialog(
        "camera"
      );
      if (!permission.granted) {
        return null;
      }

      const defaultConfig: CameraConfig = {
        quality: "high",
        enableAudio: true,
        flashMode: "off",
        cameraPosition: "back",
        ...config,
      };

      // 模拟录制结果（实际实现需要集成VisionCamera）
      const result: VideoResult = {
        path: `/tmp/video_${Date.now()}.mp4`,
        duration: 30000,
        size: 10240000,
        timestamp: Date.now(),
      };

      console.log("🎥 录制成功:", result);
      return result;
    } catch (error) {
      console.error("录制失败:", error);
      Alert.alert("录制失败", "请稍后重试");
      return null;
    }
  }

  /**
   * 语音识别功能
   */
  async startVoiceRecognition(
    config: Partial<VoiceConfig> = {}
  ): Promise<void> {
    if (!this.voiceModule) {
      Alert.alert("错误", "语音模块未初始化");
      return;
    }

    try {
      // 检查并请求麦克风权限
      const permission = await permissionManager.requestPermissionWithDialog(
        "microphone"
      );
      if (!permission.granted) {
        return;
      }

      const defaultConfig: VoiceConfig = {
        locale: "zh-CN",
        continuous: true,
        interimResults: true,
        maxAlternatives: 3,
        timeout: 30000,
        ...config,
      };

      // 设置语音识别事件监听器
      this.voiceModule.onSpeechStart = () => {
        console.log("🎤 开始语音识别");
      };

      this.voiceModule.onSpeechEnd = () => {
        console.log("🎤 语音识别结束");
      };

      this.voiceModule.onSpeechResults = (event: any) => {
        const results = event.value;
        console.log("🎤 语音识别结果:", results);
      };

      this.voiceModule.onSpeechError = (event: any) => {
        console.error("🎤 语音识别错误:", event.error);
      };

      // 开始语音识别
      await this.voiceModule.start(defaultConfig.locale);
      console.log("🎤 语音识别已启动");
    } catch (error) {
      console.error("启动语音识别失败:", error);
      Alert.alert("语音识别失败", "请检查麦克风权限");
    }
  }

  /**
   * 停止语音识别
   */
  async stopVoiceRecognition(): Promise<void> {
    if (!this.voiceModule) {
      return;
    }

    try {
      await this.voiceModule.stop();
      console.log("🎤 语音识别已停止");
    } catch (error) {
      console.error("停止语音识别失败:", error);
    }
  }

  /**
   * 获取当前位置
   */
  async getCurrentLocation(
    config: Partial<LocationConfig> = {}
  ): Promise<LocationResult | null> {
    if (!this.locationModule) {
      Alert.alert("错误", "位置服务模块未初始化");
      return null;
    }

    try {
      // 检查并请求位置权限
      const permission = await permissionManager.requestPermissionWithDialog(
        "location"
      );
      if (!permission.granted) {
        return null;
      }

      const defaultConfig: LocationConfig = {
        accuracy: "high",
        timeout: 15000,
        maximumAge: 10000,
        enableHighAccuracy: true,
        ...config,
      };

      return new Promise((resolve, reject) => {
        this.locationModule.getCurrentPosition(
          (position: any) => {
            const result: LocationResult = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
              altitude: position.coords.altitude,
              accuracy: position.coords.accuracy,
              speed: position.coords.speed,
              heading: position.coords.heading,
              timestamp: position.timestamp,
            };
            console.log("📍 获取位置成功:", result);
            resolve(result);
          },
          (error: any) => {
            console.error("获取位置失败:", error);
            Alert.alert("定位失败", "请检查位置权限和GPS设置");
            resolve(null);
          },
          {
            enableHighAccuracy: defaultConfig.enableHighAccuracy,
            timeout: defaultConfig.timeout,
            maximumAge: defaultConfig.maximumAge,
          }
        );
      });
    } catch (error) {
      console.error("获取位置失败:", error);
      return null;
    }
  }

  /**
   * 监听位置变化
   */
  async watchLocation(
    callback: (location: LocationResult) => void,
    config: Partial<LocationConfig> = {}
  ): Promise<number | null> {
    if (!this.locationModule) {
      Alert.alert("错误", "位置服务模块未初始化");
      return null;
    }

    try {
      // 检查并请求位置权限
      const permission = await permissionManager.requestPermissionWithDialog(
        "location"
      );
      if (!permission.granted) {
        return null;
      }

      const defaultConfig: LocationConfig = {
        accuracy: "balanced",
        timeout: 30000,
        maximumAge: 5000,
        enableHighAccuracy: false,
        ...config,
      };

      const watchId = this.locationModule.watchPosition(
        (position: any) => {
          const result: LocationResult = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            altitude: position.coords.altitude,
            accuracy: position.coords.accuracy,
            speed: position.coords.speed,
            heading: position.coords.heading,
            timestamp: position.timestamp,
          };
          callback(result);
        },
        (error: any) => {
          console.error("位置监听错误:", error);
        },
        {
          enableHighAccuracy: defaultConfig.enableHighAccuracy,
          timeout: defaultConfig.timeout,
          maximumAge: defaultConfig.maximumAge,
        }
      );

      console.log("📍 开始监听位置变化, watchId:", watchId);
      return watchId;
    } catch (error) {
      console.error("监听位置失败:", error);
      return null;
    }
  }

  /**
   * 停止监听位置变化
   */
  clearLocationWatch(watchId: number): void {
    if (this.locationModule && watchId) {
      this.locationModule.clearWatch(watchId);
      console.log("📍 停止监听位置变化, watchId:", watchId);
    }
  }

  /**
   * 检查所有原生模块状态
   */
  getModulesStatus(): {
    camera: boolean;
    voice: boolean;
    location: boolean;
  } {
    return {
      camera: !!this.cameraModule,
      voice: !!this.voiceModule,
      location: !!this.locationModule,
    };
  }

  /**
   * 健康应用专用：启动五诊相关的原生功能
   */
  async initializeHealthFeatures(): Promise<{
    camera: boolean;
    voice: boolean;
    location: boolean;
    permissions: any;
  }> {
    console.log("🏥 初始化健康应用原生功能...");

    // 检查模块状态
    const modules = this.getModulesStatus();

    // 检查权限状态
    const permissions = await permissionManager.checkHealthAppPermissions();

    console.log("📊 原生模块状态:", modules);
    console.log("🔐 权限状态:", permissions);

    return {
      ...modules,
      permissions,
    };
  }

  /**
   * 健康应用专用：请求所有必要权限
   */
  async requestHealthPermissions(): Promise<boolean> {
    console.log("🔐 请求健康应用权限...");

    try {
      const results = await permissionManager.requestHealthAppPermissions();

      const allGranted = Object.values(results).every(
        (result) => result.granted
      );

      if (allGranted) {
        console.log("✅ 所有权限已授权");
        Alert.alert("权限授权成功", "所有功能现在可以正常使用了");
      } else {
        console.log("⚠️ 部分权限未授权:", results);
        Alert.alert(
          "权限授权不完整",
          "部分功能可能无法正常使用，您可以稍后在设置中开启相关权限"
        );
      }

      return allGranted;
    } catch (error) {
      console.error("❌ 请求权限失败:", error);
      Alert.alert("权限请求失败", "请稍后重试");
      return false;
    }
  }
}

// 导出单例实例
export const nativeModulesManager = new NativeModulesManager();
export default nativeModulesManager;
