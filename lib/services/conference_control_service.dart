import 'dart:async';
import 'package:camera/camera.dart';
import '../core/network/websocket_client.dart';
import 'error_handler_service.dart';

enum MediaState {
  enabled,
  disabled,
  unavailable
}

class ParticipantMedia {
  final String userId;
  final String userName;
  final MediaState video;
  final MediaState audio;

  ParticipantMedia({
    required this.userId,
    required this.userName,
    required this.video,
    required this.audio,
  });

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'userName': userName,
      'video': video.toString(),
      'audio': audio.toString(),
    };
  }

  factory ParticipantMedia.fromJson(Map<String, dynamic> json) {
    return ParticipantMedia(
      userId: json['userId'],
      userName: json['userName'],
      video: MediaState.values.firstWhere(
        (e) => e.toString() == json['video'],
        orElse: () => MediaState.unavailable,
      ),
      audio: MediaState.values.firstWhere(
        (e) => e.toString() == json['audio'],
        orElse: () => MediaState.unavailable,
      ),
    );
  }
}

class ConferenceControlService {
  final WebSocketClient _wsClient;
  final ErrorHandlerService _errorHandler;
  final String _userId;
  final String _userName;
  
  final _mediaStateController = StreamController<Map<String, ParticipantMedia>>.broadcast();
  final _participantsController = StreamController<List<ParticipantMedia>>.broadcast();
  
  final Map<String, ParticipantMedia> _participantStates = {};
  bool _isVideoEnabled = true;
  bool _isAudioEnabled = true;
  CameraController? _cameraController;

  ConferenceControlService({
    required WebSocketClient wsClient,
    required ErrorHandlerService errorHandler,
    required String userId,
    required String userName,
  }) : _wsClient = wsClient,
       _errorHandler = errorHandler,
       _userId = userId,
       _userName = userName {
    _initializeMessageHandling();
  }

  void _initializeMessageHandling() {
    _wsClient.messages.listen(
      (message) {
        try {
          if (message is Map<String, dynamic>) {
            if (message['type'] == 'mediaState') {
              final userId = message['userId'];
              final mediaState = ParticipantMedia.fromJson(message['data']);
              _updateParticipantState(userId, mediaState);
            } else if (message['type'] == 'participantList') {
              final List<dynamic> participants = message['data'];
              _updateParticipantList(participants);
            }
          }
        } catch (e, stackTrace) {
          _errorHandler.handleError(
            'CONTROL_MESSAGE_PARSE_ERROR',
            '解析控制消息失败: ${e.toString()}',
            ErrorSeverity.low,
            originalError: e,
            stackTrace: stackTrace,
          );
        }
      },
      onError: (error, stackTrace) {
        _errorHandler.handleError(
          'CONTROL_WEBSOCKET_ERROR',
          '控制连接错误: ${error.toString()}',
          ErrorSeverity.medium,
          originalError: error,
          stackTrace: stackTrace,
        );
      },
    );
  }

  void setCameraController(CameraController controller) {
    _cameraController = controller;
  }

  Future<void> toggleVideo() async {
    if (_cameraController == null) {
      _errorHandler.handleError(
        'CAMERA_NOT_INITIALIZED',
        '相机未初始化',
        ErrorSeverity.medium,
      );
      return;
    }

    try {
      if (_isVideoEnabled) {
        await _cameraController!.stopImageStream();
      } else {
        await _cameraController!.startImageStream((_) {});
      }

      _isVideoEnabled = !_isVideoEnabled;
      await _broadcastMediaState();
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'VIDEO_TOGGLE_ERROR',
        '切换视频状态失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> toggleAudio() async {
    try {
      _isAudioEnabled = !_isAudioEnabled;
      // TODO: 实现实际的音频开关逻辑
      await _broadcastMediaState();
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'AUDIO_TOGGLE_ERROR',
        '切换音频状态失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> _broadcastMediaState() async {
    final mediaState = ParticipantMedia(
      userId: _userId,
      userName: _userName,
      video: _isVideoEnabled ? MediaState.enabled : MediaState.disabled,
      audio: _isAudioEnabled ? MediaState.enabled : MediaState.disabled,
    );

    try {
      await _wsClient.send({
        'type': 'mediaState',
        'userId': _userId,
        'data': mediaState.toJson(),
      });

      _updateParticipantState(_userId, mediaState);
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'MEDIA_STATE_BROADCAST_ERROR',
        '广播媒体状态失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  void _updateParticipantState(String userId, ParticipantMedia mediaState) {
    _participantStates[userId] = mediaState;
    _mediaStateController.add(Map.from(_participantStates));
  }

  void _updateParticipantList(List<dynamic> participants) {
    final participantList = participants
        .map((p) => ParticipantMedia.fromJson(p))
        .toList();
    _participantsController.add(participantList);

    // 更新状态映射
    for (final participant in participantList) {
      _participantStates[participant.userId] = participant;
    }
    _mediaStateController.add(Map.from(_participantStates));
  }

  // Getters
  bool get isVideoEnabled => _isVideoEnabled;
  bool get isAudioEnabled => _isAudioEnabled;
  Stream<Map<String, ParticipantMedia>> get mediaStates => _mediaStateController.stream;
  Stream<List<ParticipantMedia>> get participants => _participantsController.stream;

  void dispose() {
    _mediaStateController.close();
    _participantsController.close();
  }
} 