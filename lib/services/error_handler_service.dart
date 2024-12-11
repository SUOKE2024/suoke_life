import 'dart:async';
import 'package:flutter/foundation.dart';

enum ErrorSeverity {
  low,
  medium,
  high,
  critical
}

class VideoConferenceError {
  final String code;
  final String message;
  final ErrorSeverity severity;
  final dynamic originalError;
  final StackTrace? stackTrace;

  VideoConferenceError({
    required this.code,
    required this.message,
    required this.severity,
    this.originalError,
    this.stackTrace,
  });
}

class ErrorHandlerService {
  final _errorController = StreamController<VideoConferenceError>.broadcast();

  // 预定义错误代码
  static const String cameraInitError = 'CAMERA_INIT_ERROR';
  static const String networkError = 'NETWORK_ERROR';
  static const String permissionError = 'PERMISSION_ERROR';
  static const String dataProcessingError = 'DATA_PROCESSING_ERROR';
  static const String encryptionError = 'ENCRYPTION_ERROR';

  void handleError(
    String code,
    String message,
    ErrorSeverity severity, {
    dynamic originalError,
    StackTrace? stackTrace,
  }) {
    final error = VideoConferenceError(
      code: code,
      message: message,
      severity: severity,
      originalError: originalError,
      stackTrace: stackTrace,
    );

    // 记录错误
    _logError(error);

    // 发送错误到流
    _errorController.add(error);

    // 对于严重错误，可能需要额外处理
    if (severity == ErrorSeverity.critical) {
      _handleCriticalError(error);
    }
  }

  void _logError(VideoConferenceError error) {
    if (kDebugMode) {
      print('视频会议错误: ${error.code}');
      print('消息: ${error.message}');
      print('严重程度: ${error.severity}');
      if (error.originalError != null) {
        print('原始错误: ${error.originalError}');
      }
      if (error.stackTrace != null) {
        print('堆栈跟踪: ${error.stackTrace}');
      }
    }
    
    // TODO: 实现正式的日志记录逻辑
  }

  void _handleCriticalError(VideoConferenceError error) {
    // TODO: 实现关键错误处理逻辑
    // 例如：强制关闭视频会议、通知用户、尝试恢复等
  }

  // 处理相机初始化错误
  void handleCameraError(dynamic error, StackTrace stackTrace) {
    handleError(
      cameraInitError,
      '相机初始化失败: ${error.toString()}',
      ErrorSeverity.high,
      originalError: error,
      stackTrace: stackTrace,
    );
  }

  // 处理网络错误
  void handleNetworkError(dynamic error, StackTrace stackTrace) {
    handleError(
      networkError,
      '网络连接错误: ${error.toString()}',
      ErrorSeverity.medium,
      originalError: error,
      stackTrace: stackTrace,
    );
  }

  // 处理权限错误
  void handlePermissionError(String permission) {
    handleError(
      permissionError,
      '缺少必要权限: $permission',
      ErrorSeverity.high,
    );
  }

  // 处理数据处理错误
  void handleDataProcessingError(dynamic error, StackTrace stackTrace) {
    handleError(
      dataProcessingError,
      '数据处理错误: ${error.toString()}',
      ErrorSeverity.medium,
      originalError: error,
      stackTrace: stackTrace,
    );
  }

  // 处理加密错误
  void handleEncryptionError(dynamic error, StackTrace stackTrace) {
    handleError(
      encryptionError,
      '数据加密错误: ${error.toString()}',
      ErrorSeverity.high,
      originalError: error,
      stackTrace: stackTrace,
    );
  }

  // 获取错误流
  Stream<VideoConferenceError> get errorStream => _errorController.stream;

  void dispose() {
    _errorController.close();
  }
} 