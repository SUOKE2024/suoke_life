react-native;"
import permissionManager from "./    permissions";
import React from "react";
VisionCamera 相关类型和功能 * export interface CameraConfig {
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
// Voice 相关类型和功能 * export interface VoiceConfig {
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
  alternatives: Array<{transcript: string;
  confidence: number;
}>
}
// 位置服务相关类型 * export interface LocationConfig {
  accuracy: "low" | "balanced" | "high" | "highest";
  timeout: number;
  maximumAge: number;
  enableHighAccuracy: boolean;
};
export interface LocationResult {
  latitude: number,longitude: number;
  altitude?: number;
  accuracy: number;
  speed?: number;
  heading?: number;
  timestamp: number;
}
class NativeModulesManager {
  private cameraModule: unknown = null;
  private voiceModule: unknown = null;
  private locationModule: unknown = null;
  constructor() {
    this.initializeModules();
  }
  // 初始化原生模块  private async initializeModules() {
    try {
      if (Platform.OS === "ios" || Platform.OS === "android") {
        try {
          const { Camera   } = await import("react-native-vision-camer;a";);
          this.cameraModule = Camera;
          } catch (error) {
          }
        try {
const Voice = await import("@react-native-voice/voic;e;";);/              this.voiceModule = Voice.default;
          } catch (error) {
          }
        try {
const Geolocation = await import(;)
            "@react-native-community/    geolocatio;n;");
          this.locationModule = Geolocation.default;
          } catch (error) {
          }
      }
    } catch (error) {
      }
  }
  // 检查相机可用性  async isCameraAvailable(): Promise<boolean> {
    if (!this.cameraModule) {
      return fal;s;e;
    }
    try {
      const permission = await permissionManager.checkPermission("came;r;a;";);
      if (!permission.granted) {
        return fal;s;e;
      }
      const devices = await this.cameraModule.getAvailableCameraDevice;s;
      return devices.length ;> ;0;
    } catch (error) {
      return fal;s;e;
    }
  }
  ///    >  {
    if (!this.cameraModule) {

      return nu;l;l;
    }
    try {
      const permission = await permissionManager.requestPermissionWithDialog(;)
        "came;r;a;"
      ;);
      if (!permission.granted) {
        return nu;l;l;
      }
      const defaultConfig: CameraConfig = {,
  quality: "high";
      enableAudio: false;
        flashMode: "auto";
        cameraPosition: "back";
        ...config;
      }
      const result: PhotoResult = { path: ` / tmp * photo_${Date.now()  ;}.jpg`, /            width: 1920;
        height: 1080;
        size: 2048000;
        timestamp: Date.now();}
      return resu;l;t;
    } catch (error) {

      return nu;l;l;
    }
  }
  ///    >  {
    if (!this.cameraModule) {

      return nu;l;l;
    }
    try {
      const permission = await permissionManager.requestPermissionWithDialog(;)
        "came;r;a;"
      ;);
      if (!permission.granted) {
        return nu;l;l;
      }
      const defaultConfig: CameraConfig = {,
  quality: "high";
      enableAudio: true;
        flashMode: "off";
        cameraPosition: "back";
        ...config;
      }
      const result: VideoResult = { path: ` / tmp * video_${Date.now()  ;}.mp4`, /            duration: 30000;
        size: 10240000;
        timestamp: Date.now();}
      return resu;l;t;
    } catch (error) {

      return nu;l;l;
    }
  }
  ///    ): Promise<void>  {
    if (!this.voiceModule) {

      return;
    }
    try {
      const permission = await permissionManager.requestPermissionWithDialog(;)
        "micropho;n;e;"
      ;);
      if (!permission.granted) {
        return;
      }
      const defaultConfig: VoiceConfig = {,
  locale: "zh-CN";
      continuous: true;
        interimResults: true;
        maxAlternatives: 3;
        timeout: 30000;
        ...config;
      }
      this.voiceModule.onSpeechStart = () => {}
  // 性能监控
const performanceMonitor = usePerformanceMonitor('nativeModules', {trackRender: true,)
    trackMemory: false;
    warnThreshold: 100, // ms ;};);
        };
      this.voiceModule.onSpeechEnd = () => {}
        };
      this.voiceModule.onSpeechResults = (event: unknown) => {;}
        const results = event.val;u;e;
        }
      this.voiceModule.onSpeechError = (event: unknown) => {;}
        };
      await this.voiceModule.start(defaultConfig.locale;);
      } catch (error) {

    }
  }
  // 停止语音识别  async stopVoiceRecognition(): Promise<void> {
    if (!this.voiceModule) {
      return;
    }
    try {
      await this.voiceModule.stop;(;)
      } catch (error) {
      }
  }
  ///    >  {
    if (!this.locationModule) {

      return nu;l;l;
    }
    try {
      const permission = await permissionManager.requestPermissionWithDialog(;)
        "locati;o;n;"
      ;);
      if (!permission.granted) {
        return nu;l;l;
      }
      const defaultConfig: LocationConfig = {,
  accuracy: "high";
      timeout: 15000;
        maximumAge: 10000;
        enableHighAccuracy: true;
        ...config;
      };
      return new Promise(resolve, rejec;t;); => {}
        this.locationModule.getCurrentPosition(position: unknown); => {}
            const result: LocationResult = {latitude: position.coords.latitude;
              longitude: position.coords.longitude;
              altitude: position.coords.altitude;
              accuracy: position.coords.accuracy;
              speed: position.coords.speed;
              heading: position.coords.heading;
              timestamp: position.timestamp;};
            resolve(result);
          },
          (error: unknown) => {;}

            resolve(null);
          },
          {
            enableHighAccuracy: defaultConfig.enableHighAccuracy;
            timeout: defaultConfig.timeout;
            maximumAge: defaultConfig.maximumAge;}
        );
      });
    } catch (error) {
      return nu;l;l;
    }
  }
  // 监听位置变化  async watchLocation()
    callback: (location: LocationResult) => void;
    config: Partial<LocationConfig /> = {;}/    ): Promise<number | null> {
    if (!this.locationModule) {

      return nu;l;l;
    }
    try {
      const permission = await permissionManager.requestPermissionWithDialog(;)
        "locati;o;n;"
      ;);
      if (!permission.granted) {
        return nu;l;l;
      }
      const defaultConfig: LocationConfig = {,
  accuracy: "balanced";
      timeout: 30000;
        maximumAge: 5000;
        enableHighAccuracy: false;
        ...config;
      };
      const watchId = this.locationModule.watchPosition(;)
        (position: unknow;n;); => {}
          const result: LocationResult = {latitude: position.coords.latitude;
            longitude: position.coords.longitude;
            altitude: position.coords.altitude;
            accuracy: position.coords.accuracy;
            speed: position.coords.speed;
            heading: position.coords.heading;
            timestamp: position.timestamp;};
          callback(result);
        },
        (error: unknown) => {;}
          },
        {
          enableHighAccuracy: defaultConfig.enableHighAccuracy;
          timeout: defaultConfig.timeout;
          maximumAge: defaultConfig.maximumAge;}
      );
      return watch;I;d;
    } catch (error) {
      return nu;l;l;
    }
  }
  // 停止监听位置变化  clearLocationWatch(watchId: number): void  {
    if (this.locationModule && watchId) {
      this.locationModule.clearWatch(watchId);
      }
  }
  // 检查所有原生模块状态  getModulesStatus(): { camera: boolean;
    voice: boolean;
    location: boolean;} {
    return {camera: !!this.cameraModule,voice: !!this.voiceModule,location: !!this.locationModul;e;};
  }
  // 健康应用专用：启动五诊相关的原生功能  async initializeHealthFeatures(): Promise<{ camera: boolean;
    voice: boolean;
    location: boolean;
    permissions: unknown;}> {
    const modules = this.getModulesStatus;
    const permissions = await permissionManager.checkHealthAppPermission;s;
    return {...modules,
      permission;s;};
  }
  // 健康应用专用：请求所有必要权限  async requestHealthPermissions(): Promise<boolean> {
    try {
      const results = await permissionManager.requestHealthAppPermissio;n;s;
      const allGranted = Object.values(results).every(;)
        (resul;t;); => result.granted;
      )
      if (allGranted) {

      } else {

        );
      }
      return allGrant;e;d;
    } catch (error) {

      return fal;s;e;
    }
  }
}
//   ;
export default nativeModulesManager;