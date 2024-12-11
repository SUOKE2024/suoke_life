import 'dart:async';
import '../core/network/http_client.dart';
import '../core/network/websocket_client.dart';
import 'realtime_data_collection_service.dart';

class BiometricAnalysisResult {
  final String id;
  final BiometricType type;
  final DateTime timestamp;
  final Map<String, dynamic> analysis;
  final double confidence;
  final Map<String, dynamic>? metadata;

  BiometricAnalysisResult({
    required this.id,
    required this.type,
    required this.timestamp,
    required this.analysis,
    required this.confidence,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type.toString(),
    'timestamp': timestamp.toIso8601String(),
    'analysis': analysis,
    'confidence': confidence,
    'metadata': metadata,
  };
}

class BiometricAnalysisService {
  final HttpClient _httpClient;
  final WebSocketClient _wsClient;
  final RealtimeDataCollectionService _dataCollectionService;
  
  final StreamController<BiometricAnalysisResult> _analysisController = 
      StreamController<BiometricAnalysisResult>.broadcast();
  
  bool _isAnalyzing = false;
  Map<BiometricType, List<BiometricData>> _dataBuffer = {};
  Timer? _analysisTimer;

  BiometricAnalysisService({
    required HttpClient httpClient,
    required WebSocketClient wsClient,
    required RealtimeDataCollectionService dataCollectionService,
  }) : _httpClient = httpClient,
       _wsClient = wsClient,
       _dataCollectionService = dataCollectionService {
    _initializeAnalysis();
  }

  void _initializeAnalysis() {
    // 订阅实时数据流
    _dataCollectionService.biometricStream.listen((data) {
      if (_isAnalyzing) {
        _bufferData(data);
        _analyzeData(data);
      }
    });
  }

  void _bufferData(BiometricData data) {
    _dataBuffer.putIfAbsent(data.type, () => []).add(data);
    
    // 保持缓冲区大小
    const maxBufferSize = 100;
    if (_dataBuffer[data.type]!.length > maxBufferSize) {
      _dataBuffer[data.type]!.removeAt(0);
    }
  }

  Future<void> _analyzeData(BiometricData data) async {
    try {
      switch (data.type) {
        case BiometricType.face:
          await _analyzeFaceData(data);
          break;
        case BiometricType.voice:
          await _analyzeVoiceData(data);
          break;
        case BiometricType.emotion:
          await _analyzeEmotionData(data);
          break;
        default:
          break;
      }
    } catch (e) {
      print('分析数据失败: $e');
    }
  }

  Future<void> _analyzeFaceData(BiometricData data) async {
    // 调用深度学习API进行人脸分析
    final response = await _httpClient.post(
      Uri.parse('YOUR_API_ENDPOINT/deep-face-analysis'),
      body: {
        'faceData': data.data,
        'metadata': data.metadata,
        'timestamp': data.timestamp.toIso8601String(),
      },
    );

    if (response.statusCode == 200) {
      final result = BiometricAnalysisResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: BiometricType.face,
        timestamp: DateTime.now(),
        analysis: response.body,
        confidence: response.body['confidence'] ?? 0.0,
        metadata: {
          'features': response.body['features'],
          'landmarks': response.body['landmarks'],
        },
      );

      _analysisController.add(result);
      await _sendAnalysisResult(result);
    }
  }

  Future<void> _analyzeVoiceData(BiometricData data) async {
    // 调用声纹分析API
    final response = await _httpClient.post(
      Uri.parse('YOUR_API_ENDPOINT/voice-analysis'),
      body: {
        'voiceData': data.data,
        'metadata': data.metadata,
        'timestamp': data.timestamp.toIso8601String(),
      },
    );

    if (response.statusCode == 200) {
      final result = BiometricAnalysisResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: BiometricType.voice,
        timestamp: DateTime.now(),
        analysis: response.body,
        confidence: response.body['confidence'] ?? 0.0,
        metadata: {
          'features': response.body['features'],
          'spectrum': response.body['spectrum'],
        },
      );

      _analysisController.add(result);
      await _sendAnalysisResult(result);
    }
  }

  Future<void> _analyzeEmotionData(BiometricData data) async {
    // 调用情绪分析API
    final response = await _httpClient.post(
      Uri.parse('YOUR_API_ENDPOINT/emotion-analysis'),
      body: {
        'imageData': data.data,
        'metadata': data.metadata,
        'timestamp': data.timestamp.toIso8601String(),
      },
    );

    if (response.statusCode == 200) {
      final result = BiometricAnalysisResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: BiometricType.emotion,
        timestamp: DateTime.now(),
        analysis: response.body,
        confidence: response.body['confidence'] ?? 0.0,
        metadata: {
          'emotions': response.body['emotions'],
          'intensity': response.body['intensity'],
        },
      );

      _analysisController.add(result);
      await _sendAnalysisResult(result);
    }
  }

  Future<void> _sendAnalysisResult(BiometricAnalysisResult result) async {
    try {
      await _wsClient.send(result.toJson());
    } catch (e) {
      print('发送分析结果失败: $e');
    }
  }

  void startAnalysis({
    Duration analysisInterval = const Duration(seconds: 5),
  }) {
    if (_isAnalyzing) return;
    _isAnalyzing = true;

    // 启动定期批量分析
    _analysisTimer = Timer.periodic(analysisInterval, (_) {
      _performBatchAnalysis();
    });
  }

  Future<void> _performBatchAnalysis() async {
    if (_dataBuffer.isEmpty) return;

    try {
      // 对每种生物特征类型进行批量分析
      for (var entry in _dataBuffer.entries) {
        final type = entry.key;
        final data = entry.value;

        if (data.isEmpty) continue;

        // 调用批量分析API
        final response = await _httpClient.post(
          Uri.parse('YOUR_API_ENDPOINT/batch-analysis'),
          body: {
            'type': type.toString(),
            'data': data.map((d) => d.toJson()).toList(),
            'timestamp': DateTime.now().toIso8601String(),
          },
        );

        if (response.statusCode == 200) {
          final result = BiometricAnalysisResult(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            type: type,
            timestamp: DateTime.now(),
            analysis: response.body,
            confidence: response.body['confidence'] ?? 0.0,
            metadata: {
              'sampleCount': data.length,
              'timeRange': {
                'start': data.first.timestamp.toIso8601String(),
                'end': data.last.timestamp.toIso8601String(),
              },
            },
          );

          _analysisController.add(result);
          await _sendAnalysisResult(result);
        }
      }
    } catch (e) {
      print('批量分析失败: $e');
    }
  }

  void stopAnalysis() {
    _isAnalyzing = false;
    _analysisTimer?.cancel();
    _analysisTimer = null;
    _dataBuffer.clear();
  }

  void dispose() {
    stopAnalysis();
    _analysisController.close();
  }

  // Getters
  bool get isAnalyzing => _isAnalyzing;
  Stream<BiometricAnalysisResult> get analysisStream => _analysisController.stream;
} 