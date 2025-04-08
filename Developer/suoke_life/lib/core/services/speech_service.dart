import 'dart:async';
import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/utils/permission_utils.dart';

/// 语音识别状态
enum SpeechRecognitionStatus {
  /// 初始状态
  notInitialized,

  /// 初始化中
  initializing,

  /// 就绪状态
  ready,

  /// 正在识别中
  listening,

  /// 已结束
  stopped,

  /// 发生错误
  error,
}

/// 语音服务状态提供者
final speechServiceProvider =
    StateNotifierProvider<SpeechService, SpeechRecognitionStatus>((ref) {
  return SpeechService();
});

/// 语音识别结果提供者
final speechResultProvider = StateProvider<String>((ref) => '');

/// 语音服务类，用于处理语音识别相关功能
class SpeechService extends StateNotifier<SpeechRecognitionStatus> {
  SpeechService() : super(SpeechRecognitionStatus.notInitialized) {
    _initialize();
  }

  /// 语音识别引擎
  final SpeechToText _speech = SpeechToText();

  /// 最后识别的文本
  String _lastRecognizedText = '';

  /// 获取最后识别的文本
  String get lastRecognizedText => _lastRecognizedText;

  /// 初始化尝试次数
  int _initAttempts = 0;

  /// 最大初始化尝试次数
  static const int _maxInitAttempts = 3;

  /// 初始化语音识别引擎
  Future<void> _initialize() async {
    try {
      debugPrint('开始初始化语音识别服务...');
      state = SpeechRecognitionStatus.initializing;

      // 检查是否已经初始化成功
      if (_speech.isAvailable) {
        debugPrint('语音识别服务已经初始化');
        state = SpeechRecognitionStatus.ready;
        return;
      }

      // 暂时不检查权限，仅尝试初始化语音服务
      // 实际的权限检查会在startListening时进行
      final isInitialized = await _speech.initialize(
        onStatus: _onStatusChange,
        onError: _onErrorListener,
        debugLogging: true,
      );

      if (isInitialized) {
        debugPrint('语音识别服务初始化成功');
        state = SpeechRecognitionStatus.ready;
        _initAttempts = 0; // 重置初始化尝试次数
      } else {
        debugPrint('语音识别服务初始化失败');
        _handleInitFailure();
      }
    } catch (e) {
      debugPrint('语音识别服务初始化错误: $e');
      _handleInitFailure();
    }
  }

  /// 处理初始化失败
  void _handleInitFailure() {
    _initAttempts++;

    if (_initAttempts < _maxInitAttempts) {
      debugPrint('尝试重新初始化语音识别服务 (${_initAttempts}/${_maxInitAttempts})');

      // 延迟500毫秒后重试
      Future.delayed(const Duration(milliseconds: 500), () {
        _initialize();
      });
    } else {
      debugPrint('语音识别服务初始化失败，已达到最大尝试次数');
      state = SpeechRecognitionStatus.error;
      _initAttempts = 0; // 重置尝试次数，允许未来重试
    }
  }

  /// 状态变化回调
  void _onStatusChange(String status) {
    debugPrint('语音识别状态变化: $status');
    if (status == 'listening') {
      state = SpeechRecognitionStatus.listening;
    } else if (status == 'notListening') {
      state = SpeechRecognitionStatus.stopped;
    } else if (status == 'available') {
      state = SpeechRecognitionStatus.ready;
    }
  }

  /// 错误回调
  void _onErrorListener(dynamic error) {
    debugPrint('语音识别错误: $error');

    // 检查错误类型和信息
    bool isPermanentError = false;

    // 尝试从错误对象中提取信息
    if (error is Map) {
      isPermanentError = error['permanent'] == true;
    } else if (error.toString().contains('permanent')) {
      isPermanentError = true;
    }

    // 只有在永久性错误时才更改状态
    if (isPermanentError) {
      state = SpeechRecognitionStatus.error;
    }
  }

  /// 开始语音识别
  Future<bool> startListening({
    Function(String text)? onResult,
    Locale? locale,
  }) async {
    try {
      debugPrint('准备开始语音识别...');
      _lastRecognizedText = '';

      // 检查和请求麦克风权限
      final hasMicrophonePermission =
          await PermissionUtils.requestMicrophonePermission();
      if (!hasMicrophonePermission) {
        debugPrint('麦克风权限被拒绝，无法开始语音识别');
        state = SpeechRecognitionStatus.error;
        return false;
      }

      // 如果语音识别引擎未初始化或出错，尝试重新初始化
      if (state == SpeechRecognitionStatus.notInitialized ||
          state == SpeechRecognitionStatus.error) {
        debugPrint('语音服务需要初始化，正在尝试初始化...');
        await _initialize();

        // 等待初始化完成（最多等待2秒）
        int waitCount = 0;
        while (
            state == SpeechRecognitionStatus.initializing && waitCount < 20) {
          await Future.delayed(const Duration(milliseconds: 100));
          waitCount++;
        }

        // 如果初始化后仍然是错误状态，则返回失败
        if (state == SpeechRecognitionStatus.error) {
          debugPrint('语音识别服务初始化失败，无法开始识别');
          return false;
        }
      }

      // 确保不是已经在识别状态
      if (_speech.isListening) {
        debugPrint('语音识别服务已在运行中');
        return true;
      }

      // 开始识别
      debugPrint('正在启动语音识别...');
      final result = await _speech.listen(
        onResult: (result) {
          _lastRecognizedText = result.recognizedWords;
          debugPrint('识别结果: ${_lastRecognizedText}');
          if (onResult != null) {
            onResult(_lastRecognizedText);
          }
        },
        localeId: locale?.toLanguageTag(),
        listenMode: ListenMode.dictation,
        partialResults: true,
        pauseFor: const Duration(seconds: 3),
        cancelOnError: false,
        listenFor: const Duration(seconds: 30), // 最长识别30秒
      );

      if (result) {
        debugPrint('语音识别开始成功');
        state = SpeechRecognitionStatus.listening;
      } else {
        debugPrint('语音识别开始失败，可能是权限问题或语音引擎未准备好');
        // 如果是因为没有初始化，尝试强制初始化后再次开始
        if (!_speech.isAvailable) {
          debugPrint('尝试强制初始化后再次启动语音识别');
          await _initialize();
          if (state == SpeechRecognitionStatus.ready) {
            return startListening(onResult: onResult, locale: locale);
          }
        }
        state = SpeechRecognitionStatus.error;
      }

      return result;
    } catch (e) {
      debugPrint('启动语音识别失败: $e');
      state = SpeechRecognitionStatus.error;
      return false;
    }
  }

  /// 停止语音识别
  Future<void> stopListening() async {
    debugPrint('停止语音识别');
    if (_speech.isListening) {
      await _speech.stop();
    }
    state = SpeechRecognitionStatus.stopped;
  }

  /// 取消语音识别
  Future<void> cancelListening() async {
    debugPrint('取消语音识别');
    if (_speech.isListening) {
      await _speech.cancel();
    }
    state = SpeechRecognitionStatus.ready;
  }

  /// 检查是否正在识别
  bool get isListening => _speech.isListening;

  /// 检查是否可用
  bool get isAvailable => _speech.isAvailable;

  /// 强制重新初始化
  Future<bool> forceReInitialize() async {
    debugPrint('强制重新初始化语音识别服务');

    // 先确保停止任何进行中的语音识别
    if (_speech.isListening) {
      await _speech.stop();
    }

    // 重置状态
    state = SpeechRecognitionStatus.notInitialized;
    _initAttempts = 0;

    // 尝试初始化
    await _initialize();

    // 等待初始化完成
    int count = 0;
    while (state == SpeechRecognitionStatus.initializing && count < 20) {
      await Future.delayed(const Duration(milliseconds: 100));
      count++;
    }

    return state == SpeechRecognitionStatus.ready;
  }

  @override
  void dispose() {
    if (_speech.isListening) {
      _speech.cancel();
    }
    super.dispose();
  }
}
