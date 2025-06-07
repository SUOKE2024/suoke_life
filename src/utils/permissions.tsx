import { Platform, Alert, Linking } from 'react-native';
import {
  PERMISSIONS,
  RESULTS,
  check,
  request,
  PermissionStatus;
} from 'react-native-permissions';
export type PermissionType =
  | "camera"
  | "microphone"
  | "location"
  | "photoLibrary"
  | "notifications";
export interface PermissionResult {
  granted: boolean;
  status: PermissionStatus;
  canAskAgain: boolean;
}
class PermissionManager {
  private getPermission(type: PermissionType) {
    if (Platform.OS === "ios") {
      switch (type) {
        case "camera":
          return PERMISSIONS.IOS.CAMERA;
        case "microphone":
          return PERMISSIONS.IOS.MICROPHONE;
        case "location":
          return PERMISSIONS.IOS.LOCATION_WHEN_IN_USE;
        case "photoLibrary":
          return PERMISSIONS.IOS.PHOTO_LIBRARY;
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
          return PERMISSIONS.ANDROID.ACCESS_FINE_LOCATION;
        case "photoLibrary":
          return PERMISSIONS.ANDROID.READ_EXTERNAL_STORAGE;
        default:
          return null;
      }
    }
    return null;
  }
  async checkPermission(type: PermissionType): Promise<PermissionResult> {
    const permission = this.getPermission(type);
    if (!permission) {
      return {
        granted: false,
        status: RESULTS.UNAVAILABLE,
        canAskAgain: false;
      };
    }
    try {
      const status = await check(permission);
      return {
        granted: status === RESULTS.GRANTED,
        status,
        canAskAgain: status === RESULTS.DENIED;
      };
    } catch (error) {
      return {
        granted: false,
        status: RESULTS.UNAVAILABLE,
        canAskAgain: false;
      };
    }
  }
  async requestPermission(type: PermissionType): Promise<PermissionResult> {
    const permission = this.getPermission(type);
    if (!permission) {
      return {
        granted: false,
        status: RESULTS.UNAVAILABLE,
        canAskAgain: false;
      };
    }
    try {
      const status = await request(permission);
      return {
        granted: status === RESULTS.GRANTED,
        status,
        canAskAgain: status === RESULTS.DENIED;
      };
    } catch (error) {
      return {
        granted: false,
        status: RESULTS.UNAVAILABLE,
        canAskAgain: false;
      };
    }
  }
  getPermissionDescription(type: PermissionType): string {
    switch (type) {
      case "camera":
        return "相机权限用于拍照和录像功能";
      case "microphone":
        return "麦克风权限用于语音识别功能";
      case "location":
        return "位置权限用于提供基于位置的服务";
      case "photoLibrary":
        return "相册权限用于选择和保存图片";
      case "notifications":
        return "通知权限用于健康提醒";
      default:
        return "该权限用于应用正常功能";
    }
  }
  showSettingsDialog(type: PermissionType): void {
    Alert.alert(
      "权限被拒绝",请在设置中开启权限以使用相关功能",
      [
        {
      text: "取消",
      style: "cancel" },
        {
      text: "去设置",
      onPress: () => Linking.openSettings() }
      ]
    );
  }
}
export const permissionManager = new PermissionManager();
export default permissionManager;