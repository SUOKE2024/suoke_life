import 'dart:async';
import 'dart:io';

import 'package:camera/camera.dart';
import 'error_handler_service.dart';

enum RecordingState {
  idle,
  recording,
  paused,
  processing,
  completed,
  error
}

class RecordingInfo {
  final String id;
  final String filePath;
  final DateTime startTime;
  final DateTime? endTime;
  final Duration duration;
  final int fileSize;

  RecordingInfo({
    required this.id,
    required this.filePath,
    required this.startTime,
    this.endTime,
    required this.duration,
    required this.fileSize,
  });
}

class RecordingService {
  final ErrorHandlerService _errorHandler;
  
  final _recordingStateController = StreamController<RecordingState>.broadcast();
  final _recordingInfoController = StreamController<RecordingInfo>.broadcast();
  
  RecordingState _currentState = RecordingState.idle;
  String? _currentRecordingPath;
  DateTime? _recordingStartTime;
  Timer? _durationTimer;
  Duration _currentDuration = Duration.zero;

  RecordingService({
    required ErrorHandlerService errorHandler,
  }) : _errorHandler = errorHandler;

  Future<void> startRecording(CameraController cameraController) async {
    if (_currentState == RecordingState.recording) {
      return;
    }

    try {
      _currentState = RecordingState.recording;
      _recordingStateController.add(_currentState);

      // 创建录制文件路径
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      _currentRecordingPath = '${directory.path}/recording_$timestamp.mp4';
      
      // 开始录制
      await cameraController.startVideoRecording();
      
      // 记录开始时间
      _recordingStartTime = DateTime.now();
      
      // 启动计时器
      _startDurationTimer();
      
    } catch (e, stackTrace) {
      _currentState = RecordingState.error;
      _recordingStateController.add(_currentState);
      _errorHandler.handleError(
        'RECORDING_START_ERROR',
        '开始录制失败: ${e.toString()}',
        ErrorSeverity.high,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> stopRecording(CameraController cameraController) async {
    if (_currentState != RecordingState.recording) {
      return;
    }

    try {
      _currentState = RecordingState.processing;
      _recordingStateController.add(_currentState);

      // 停止录制
      final videoFile = await cameraController.stopVideoRecording();
      
      // 停止计时器
      _stopDurationTimer();

      // 获取文件信息
      final file = File(videoFile.path);
      final fileSize = await file.length();
      
      // 创建录制信息
      final recordingInfo = RecordingInfo(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        filePath: videoFile.path,
        startTime: _recordingStartTime!,
        endTime: DateTime.now(),
        duration: _currentDuration,
        fileSize: fileSize,
      );

      // 重置状态
      _currentState = RecordingState.completed;
      _recordingStateController.add(_currentState);
      _recordingInfoController.add(recordingInfo);
      
      // 重置变量
      _resetRecording();

    } catch (e, stackTrace) {
      _currentState = RecordingState.error;
      _recordingStateController.add(_currentState);
      _errorHandler.handleError(
        'RECORDING_STOP_ERROR',
        '停止录制失败: ${e.toString()}',
        ErrorSeverity.high,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> pauseRecording(CameraController cameraController) async {
    if (_currentState != RecordingState.recording) {
      return;
    }

    try {
      await cameraController.pauseVideoRecording();
      _currentState = RecordingState.paused;
      _recordingStateController.add(_currentState);
      _stopDurationTimer();
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'RECORDING_PAUSE_ERROR',
        '暂停录制失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> resumeRecording(CameraController cameraController) async {
    if (_currentState != RecordingState.paused) {
      return;
    }

    try {
      await cameraController.resumeVideoRecording();
      _currentState = RecordingState.recording;
      _recordingStateController.add(_currentState);
      _startDurationTimer();
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'RECORDING_RESUME_ERROR',
        '恢复录制失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  void _startDurationTimer() {
    _durationTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      _currentDuration += const Duration(seconds: 1);
    });
  }

  void _stopDurationTimer() {
    _durationTimer?.cancel();
    _durationTimer = null;
  }

  void _resetRecording() {
    _currentRecordingPath = null;
    _recordingStartTime = null;
    _currentDuration = Duration.zero;
    _stopDurationTimer();
  }

  Future<List<RecordingInfo>> getRecordings() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final recordingsDir = Directory(directory.path);
      
      if (!await recordingsDir.exists()) {
        return [];
      }

      final recordings = <RecordingInfo>[];
      await for (final file in recordingsDir.list()) {
        if (file is File && file.path.endsWith('.mp4')) {
          final stat = await file.stat();
          recordings.add(RecordingInfo(
            id: file.path.split('/').last.split('.').first,
            filePath: file.path,
            startTime: stat.modified,
            duration: Duration.zero, // 实际应用中需要获取视频时长
            fileSize: stat.size,
          ));
        }
      }

      return recordings;
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'RECORDING_LIST_ERROR',
        '获取录制列表失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
      return [];
    }
  }

  Future<void> deleteRecording(String recordingId) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/recording_$recordingId.mp4');
      
      if (await file.exists()) {
        await file.delete();
      }
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'RECORDING_DELETE_ERROR',
        '删除录制失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  // Getters
  RecordingState get currentState => _currentState;
  Stream<RecordingState> get recordingState => _recordingStateController.stream;
  Stream<RecordingInfo> get recordingInfo => _recordingInfoController.stream;
  Duration get currentDuration => _currentDuration;

  void dispose() {
    _recordingStateController.close();
    _recordingInfoController.close();
    _stopDurationTimer();
  }
} 