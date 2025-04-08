// 注意：该文件只在Web平台运行
import 'dart:html' as html;
import 'package:flutter/material.dart';

/// Web平台的权限工具类
class WebPermissionUtils {
  /// 请求相机权限
  static Future<bool> requestCameraPermission() async {
    try {
      final stream = await html.window.navigator.mediaDevices?.getUserMedia({
        'video': true,
      });

      // 如果成功获取到流，则释放它
      if (stream != null) {
        stream.getTracks().forEach((track) => track.stop());
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Web平台请求相机权限失败: $e');
      return false;
    }
  }

  /// 请求麦克风权限
  static Future<bool> requestMicrophonePermission() async {
    try {
      // 检查navigator.mediaDevices是否可用
      if (html.window.navigator.mediaDevices == null) {
        debugPrint('Web API: mediaDevices不可用，可能是非安全上下文或浏览器不支持');
        return false;
      }

      // 使用getUserMedia API请求麦克风权限
      final stream = await html.window.navigator.mediaDevices?.getUserMedia({
        'audio': true,
      });

      // 如果成功获取到流，则释放它并返回成功
      if (stream != null) {
        stream.getTracks().forEach((track) => track.stop());
        debugPrint('Web平台麦克风权限获取成功');
        return true;
      }

      debugPrint('Web平台麦克风权限获取失败：未获取到媒体流');
      return false;
    } catch (e) {
      // 捕获权限被拒绝或其他错误
      debugPrint('Web平台请求麦克风权限失败: $e');

      // 特殊处理NotAllowedError
      if (e.toString().contains('NotAllowedError')) {
        debugPrint('用户拒绝了麦克风权限请求');
      }
      // 特殊处理NotFoundError
      else if (e.toString().contains('NotFoundError')) {
        debugPrint('未找到麦克风设备');
      }

      return false;
    }
  }

  /// 请求位置权限
  static Future<bool> requestLocationPermission() async {
    try {
      final position =
          await html.window.navigator.geolocation.getCurrentPosition();
      return position != null;
    } catch (e) {
      debugPrint('Web平台请求位置权限失败: $e');
      return false;
    }
  }

  /// 检查相机权限
  static Future<bool> checkCameraPermission() async {
    // Web平台通过尝试获取权限来检查
    return requestCameraPermission();
  }

  /// 检查麦克风权限
  static Future<bool> checkMicrophonePermission() async {
    // Web平台通过尝试获取权限来检查
    return requestMicrophonePermission();
  }

  /// 检查位置权限
  static Future<bool> checkLocationPermission() async {
    // Web平台通过尝试获取权限来检查
    return requestLocationPermission();
  }

  /// 请求所有Web平台支持的权限
  static Future<void> requestAllPermissions() async {
    // 请求相机权限
    await requestCameraPermission();

    // 请求麦克风权限
    await requestMicrophonePermission();

    // 请求位置权限
    await requestLocationPermission();
  }
}
