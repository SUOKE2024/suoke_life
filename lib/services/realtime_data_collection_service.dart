import 'dart:async';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import '../core/network/http_client.dart';
import '../core/network/websocket_client.dart';
import 'multimedia_service.dart';
import 'voice_service.dart';

enum BiometricType {
  face,
  voice,
  gesture,
  expression,
  emotion
}

class BiometricData {
  final String id;
  final BiometricType type;
  final DateTime timestamp;
  final Map<String, dynamic> data;
  final Map<String, dynamic>? metadata;

  BiometricData({
    required this.id,
    required this.type,
    required this.timestamp,
    required this.data,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type.toString(),
    'timestamp': timestamp.toIso8601String(),
    'data': data,
    'metadata': metadata,
  };
}

class RealtimeDataCollectionService {
  final HttpClient _httpClient;
  final WebSocketClient _wsClient;
  final MultimediaService _multimediaService;
  final VoiceService _voiceService;
  
  RTCPeerConnection? _peerConnection;
  MediaStream? _localStream;
  Timer? _sampleTimer;
  bool _isCollecting = false;

  final StreamController<BiometricData> _biometricController = 
      StreamController<BiometricData>.broadcast();

  RealtimeDataCollectionService({
    required HttpClient httpClient,
    required WebSocketClient wsClient,
    required MultimediaService multimediaService,
    required VoiceService voiceService,
  }) : _httpClient = httpClient,
       _wsClient = wsClient,
       _multimediaService = multimediaService,
       _voiceService = voiceService;

  Future<void> initializeWebRTC() async {
    final config = {
      'iceServers': [
        {'urls': ['stun:stun.l.google.com:19302']}
      ]
    };

    _peerConnection = await createPeerConnection(config);

    // 设置本地媒体流
    _localStream = await navigator.mediaDevices.getUserMedia({
      'audio': true,
      'video': {
        'facingMode': 'user',
        'width': {'ideal': 1280},
        'height': {'ideal': 720}
      }
    });

    _localStream!.getTracks().forEach((track) {
      _peerConnection!.addTrack(track, _localStream!);
    });

    // 监听远程流
    _peerConnection!.onTrack = (event) {
      if (event.track.kind == 'video') {
        _startVideoAnalysis(event.streams[0]);
      } else if (event.track.kind == 'audio') {
        _startAudioAnalysis(event.streams[0]);
      }
    };
  }

  Future<void> startCollection({
    Duration sampleInterval = const Duration(seconds: 1),
    List<BiometricType> types = const [
      BiometricType.face,
      BiometricType.voice,
      BiometricType.emotion
    ],
  }) async {
    if (_isCollecting) return;
    _isCollecting = true;

    // 初始化WebRTC
    await initializeWebRTC();

    // 启动定时采样
    _sampleTimer = Timer.periodic(sampleInterval, (_) {
      if (_localStream != null) {
        for (var type in types) {
          _collectSample(type);
        }
      }
    });
  }

  Future<void> _collectSample(BiometricType type) async {
    try {
      switch (type) {
        case BiometricType.face:
          await _collectFaceSample();
          break;
        case BiometricType.voice:
          await _collectVoiceSample();
          break;
        case BiometricType.emotion:
          await _collectEmotionSample();
          break;
        default:
          break;
      }
    } catch (e) {
      print('采集样本失败: $e');
    }
  }

  Future<void> _collectFaceSample() async {
    if (_localStream == null) return;

    // 获取视频帧
    final videoTrack = _localStream!.getVideoTracks().first;
    final frame = await videoTrack.captureFrame();
    
    // 调用人脸分析API
    final response = await _httpClient.post(
      Uri.parse('YOUR_API_ENDPOINT/analyze-face'),
      body: {
        'image': frame.asUint8List(),
        'timestamp': DateTime.now().toIso8601String(),
      },
    );

    if (response.statusCode == 200) {
      final biometricData = BiometricData(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: BiometricType.face,
        timestamp: DateTime.now(),
        data: response.body,
        metadata: {
          'frameWidth': frame.width,
          'frameHeight': frame.height,
        },
      );

      _biometricController.add(biometricData);
      _sendToServer(biometricData);
    }
  }

  Future<void> _collectVoiceSample() async {
    if (_localStream == null) return;

    // 获取音频数据
    final audioTrack = _localStream!.getAudioTracks().first;
    final audioData = await audioTrack.getSampleData();
    
    // 调用声纹分析API
    final response = await _httpClient.post(
      Uri.parse('YOUR_API_ENDPOINT/analyze-voice'),
      body: {
        'audio': audioData,
        'timestamp': DateTime.now().toIso8601String(),
      },
    );

    if (response.statusCode == 200) {
      final biometricData = BiometricData(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: BiometricType.voice,
        timestamp: DateTime.now(),
        data: response.body,
        metadata: {
          'sampleRate': 44100,
          'channels': 1,
        },
      );

      _biometricController.add(biometricData);
      _sendToServer(biometricData);
    }
  }

  Future<void> _collectEmotionSample() async {
    if (_localStream == null) return;

    // 获取视频帧
    final videoTrack = _localStream!.getVideoTracks().first;
    final frame = await videoTrack.captureFrame();
    
    // 调用情绪分析API
    final response = await _httpClient.post(
      Uri.parse('YOUR_API_ENDPOINT/analyze-emotion'),
      body: {
        'image': frame.asUint8List(),
        'timestamp': DateTime.now().toIso8601String(),
      },
    );

    if (response.statusCode == 200) {
      final biometricData = BiometricData(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: BiometricType.emotion,
        timestamp: DateTime.now(),
        data: response.body,
        metadata: {
          'frameWidth': frame.width,
          'frameHeight': frame.height,
        },
      );

      _biometricController.add(biometricData);
      _sendToServer(biometricData);
    }
  }

  void _startVideoAnalysis(MediaStream stream) {
    stream.getVideoTracks().first.onEnded = () {
      print('视频流结束');
      stopCollection();
    };
  }

  void _startAudioAnalysis(MediaStream stream) {
    stream.getAudioTracks().first.onEnded = () {
      print('音频流结束');
      stopCollection();
    };
  }

  Future<void> _sendToServer(BiometricData data) async {
    try {
      await _wsClient.send(data.toJson());
    } catch (e) {
      print('发送数据到服务器失败: $e');
    }
  }

  void stopCollection() {
    _isCollecting = false;
    _sampleTimer?.cancel();
    _sampleTimer = null;
    
    _localStream?.getTracks().forEach((track) => track.stop());
    _localStream?.dispose();
    _localStream = null;
    
    _peerConnection?.close();
    _peerConnection = null;
  }

  void dispose() {
    stopCollection();
    _biometricController.close();
  }

  // Getters
  bool get isCollecting => _isCollecting;
  Stream<BiometricData> get biometricStream => _biometricController.stream;
  MediaStream? get localStream => _localStream;
} 