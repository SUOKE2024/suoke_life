import { Platform, Alert, Linking } from "react-native";
import {
  request,
  check,
  PERMISSIONS,
  RESULTS,
  Permission,
  PermissionStatus,
} from "react-native-permissions";

export type PermissionType =
  | "camera"
  | "microphone"
  | "location"
  | "locationWhenInUse"
  | "locationAlways"
  | "photoLibrary"
  | "mediaLibrary"
  | "contacts"
  | "calendar"
  | "reminders"
  | "notifications";

export interface PermissionResult {
  granted: boolean;
  status: PermissionStatus;
  canAskAgain: boolean;
}

class PermissionManager {
  /**
   * 获取平台特定的权限
   */
  private getPermission(type: PermissionType): Permission | null {
    if (Platform.OS === "ios") {
      switch (type) {
        case "camera":
          return PERMISSIONS.IOS.CAMERA;
        case "microphone":
          return PERMISSIONS.IOS.MICROPHONE;
        case "location":
        case "locationWhenInUse":
          return PERMISSIONS.IOS.LOCATION_WHEN_IN_USE;
        case "locationAlways":
          return PERMISSIONS.IOS.LOCATION_ALWAYS;
        case "photoLibrary":
          return PERMISSIONS.IOS.PHOTO_LIBRARY;
        case "mediaLibrary":
          return PERMISSIONS.IOS.MEDIA_LIBRARY;
        case "contacts":
          return PERMISSIONS.IOS.CONTACTS;
        case "calendar":
          return PERMISSIONS.IOS.CALENDARS;
        case "reminders":
          return PERMISSIONS.IOS.REMINDERS;
        default:
          return null;
      }
    } else if (Platform.OS === "android") {
      switch (type) {
        case "camera":
          return PERMISSIONS.ANDROID.CAMERA;
        case "microphone":
          return PERMISSIONS.ANDROID.RECORD_AUDIO;
        case "location":
        case "locationWhenInUse":
          return PERMISSIONS.ANDROID.ACCESS_FINE_LOCATION;
        case "locationAlways":
          return PERMISSIONS.ANDROID.ACCESS_BACKGROUND_LOCATION;
        case "photoLibrary":
        case "mediaLibrary":
          return PERMISSIONS.ANDROID.READ_EXTERNAL_STORAGE;
        case "contacts":
          return PERMISSIONS.ANDROID.READ_CONTACTS;
        case "calendar":
          return PERMISSIONS.ANDROID.READ_CALENDAR;
        default:
          return null;
      }
    }
    return null;
  }

  /**
   * 检查权限状态
   */
  async checkPermission(type: PermissionType): Promise<PermissionResult> {
    const permission = this.getPermission(type);

    if (!permission) {
      return {
        granted: false,
        status: RESULTS.UNAVAILABLE,
        canAskAgain: false,
      };
    }

    try {
      const status = await check(permission);

      return {
        granted: status === RESULTS.GRANTED,
        status,
        canAskAgain: status === RESULTS.DENIED,
      };
    } catch (error) {
      console.error(`检查权限失败 (${type}):`, error);
      return {
        granted: false,
        status: RESULTS.UNAVAILABLE,
        canAskAgain: false,
      };
    }
  }

  /**
   * 请求权限
   */
  async requestPermission(type: PermissionType): Promise<PermissionResult> {
    const permission = this.getPermission(type);

    if (!permission) {
      return {
        granted: false,
        status: RESULTS.UNAVAILABLE,
        canAskAgain: false,
      };
    }

    try {
      const status = await request(permission);

      return {
        granted: status === RESULTS.GRANTED,
        status,
        canAskAgain: status === RESULTS.DENIED,
      };
    } catch (error) {
      console.error(`请求权限失败 (${type}):`, error);
      return {
        granted: false,
        status: RESULTS.UNAVAILABLE,
        canAskAgain: false,
      };
    }
  }

  /**
   * 请求多个权限
   */
  async requestMultiplePermissions(
    types: PermissionType[]
  ): Promise<Record<PermissionType, PermissionResult>> {
    const results: Record<string, PermissionResult> = {};

    for (const type of types) {
      results[type] = await this.requestPermission(type);
    }

    return results as Record<PermissionType, PermissionResult>;
  }

  /**
   * 获取权限描述文本
   */
  getPermissionDescription(type: PermissionType): string {
    switch (type) {
      case "camera":
        return "相机权限用于拍照、录像和AR功能";
      case "microphone":
        return "麦克风权限用于语音识别和录音功能";
      case "location":
      case "locationWhenInUse":
        return "位置权限用于提供基于位置的健康服务";
      case "locationAlways":
        return "后台位置权限用于持续的健康监测";
      case "photoLibrary":
        return "相册权限用于选择和保存图片";
      case "mediaLibrary":
        return "媒体库权限用于访问音视频文件";
      case "contacts":
        return "通讯录权限用于紧急联系人功能";
      case "calendar":
        return "日历权限用于健康提醒和预约管理";
      case "reminders":
        return "提醒权限用于健康计划提醒";
      case "notifications":
        return "通知权限用于健康提醒和消息推送";
      default:
        return "该权限用于应用正常功能";
    }
  }

  /**
   * 显示权限说明对话框
   */
  showPermissionDialog(
    type: PermissionType,
    onConfirm: () => void,
    onCancel?: () => void
  ): void {
    const description = this.getPermissionDescription(type);
    const title = this.getPermissionTitle(type);

    Alert.alert(`需要${title}`, description, [
      {
        text: "取消",
        style: "cancel",
        onPress: onCancel,
      },
      {
        text: "授权",
        onPress: onConfirm,
      },
    ]);
  }

  /**
   * 显示设置页面对话框
   */
  showSettingsDialog(type: PermissionType): void {
    const title = this.getPermissionTitle(type);

    Alert.alert(`${title}被拒绝`, `请在设置中开启${title}以使用相关功能`, [
      {
        text: "取消",
        style: "cancel",
      },
      {
        text: "去设置",
        onPress: () => Linking.openSettings(),
      },
    ]);
  }

  /**
   * 获取权限标题
   */
  private getPermissionTitle(type: PermissionType): string {
    switch (type) {
      case "camera":
        return "相机权限";
      case "microphone":
        return "麦克风权限";
      case "location":
      case "locationWhenInUse":
      case "locationAlways":
        return "位置权限";
      case "photoLibrary":
        return "相册权限";
      case "mediaLibrary":
        return "媒体库权限";
      case "contacts":
        return "通讯录权限";
      case "calendar":
        return "日历权限";
      case "reminders":
        return "提醒权限";
      case "notifications":
        return "通知权限";
      default:
        return "权限";
    }
  }

  /**
   * 智能权限请求 - 包含说明和设置引导
   */
  async requestPermissionWithDialog(
    type: PermissionType
  ): Promise<PermissionResult> {
    // 首先检查当前状态
    const currentStatus = await this.checkPermission(type);

    if (currentStatus.granted) {
      return currentStatus;
    }

    // 如果是第一次请求或可以再次请求
    if (currentStatus.canAskAgain) {
      return new Promise((resolve) => {
        this.showPermissionDialog(
          type,
          async () => {
            const result = await this.requestPermission(type);
            if (!result.granted && !result.canAskAgain) {
              // 用户永久拒绝，显示设置对话框
              this.showSettingsDialog(type);
            }
            resolve(result);
          },
          () => {
            resolve(currentStatus);
          }
        );
      });
    } else {
      // 权限被永久拒绝，显示设置对话框
      this.showSettingsDialog(type);
      return currentStatus;
    }
  }

  /**
   * 检查健康应用所需的核心权限
   */
  async checkHealthAppPermissions(): Promise<{
    camera: PermissionResult;
    microphone: PermissionResult;
    location: PermissionResult;
    photoLibrary: PermissionResult;
  }> {
    const [camera, microphone, location, photoLibrary] = await Promise.all([
      this.checkPermission("camera"),
      this.checkPermission("microphone"),
      this.checkPermission("location"),
      this.checkPermission("photoLibrary"),
    ]);

    return {
      camera,
      microphone,
      location,
      photoLibrary,
    };
  }

  /**
   * 请求健康应用所需的核心权限
   */
  async requestHealthAppPermissions(): Promise<{
    camera: PermissionResult;
    microphone: PermissionResult;
    location: PermissionResult;
    photoLibrary: PermissionResult;
  }> {
    const results = await this.requestMultiplePermissions([
      "camera",
      "microphone",
      "location",
      "photoLibrary",
    ]);

    return {
      camera: results.camera,
      microphone: results.microphone,
      location: results.location,
      photoLibrary: results.photoLibrary,
    };
  }
}

// 导出单例实例
export const permissionManager = new PermissionManager();
export default permissionManager;
