import 'dart:async';
import 'package:shared_preferences.dart';
import '../models/voice_record.dart';
import 'voice_service.dart';
import 'nas_storage_service.dart';

class VoiceDataCollectionService {
  final VoiceService _voiceService;
  final NasStorageService _nasService;
  final StreamController<Map<String, dynamic>> _analysisController = 
      StreamController<Map<String, dynamic>>.broadcast();
  
  bool _isCollecting = false;
  List<VoiceStreamData> _collectedData = [];
  Timer? _analysisTimer;

  VoiceDataCollectionService({
    required String nasBasePath,
    required SharedPreferences prefs,
  }) : _voiceService = VoiceService(nasBasePath: nasBasePath, prefs: prefs),
       _nasService = NasStorageService(nasBasePath: nasBasePath) {
    _initializeCollection();
  }

  void _initializeCollection() {
    // 订阅语音流
    _voiceService.voiceStream.listen((data) {
      if (_isCollecting) {
        _collectedData.add(data);
        _analyzeData(data);
      }
    });
  }

  void _analyzeData(VoiceStreamData data) {
    // 实时分析数据
    final analysis = {
      'timestamp': data.timestamp.toIso8601String(),
      'metrics': {
        'volume': data.volume,
        'duration': data.metadata?['duration'] ?? 0,
        'confidence': data.metadata?['confidence'] ?? 0.0,
      },
      'text': data.text,
      'isFinal': data.isFinal,
    };

    // 发送分析结果
    _analysisController.add(analysis);

    // 如果是最终结果，保存到存储
    if (data.isFinal) {
      _saveAnalysis(analysis);
    }
  }

  Future<void> _saveAnalysis(Map<String, dynamic> analysis) async {
    try {
      await _nasService.saveVoiceRecord(
        content: analysis,
        timestamp: DateTime.now(),
        type: 'voice_analysis',
      );
    } catch (e) {
      print('保存语音分析数据失败: $e');
    }
  }

  void startCollection() {
    _isCollecting = true;
    _collectedData.clear();
    
    // 启动定期分析
    _analysisTimer?.cancel();
    _analysisTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      if (_collectedData.isNotEmpty) {
        _performBatchAnalysis();
      }
    });
  }

  void stopCollection() {
    _isCollecting = false;
    _analysisTimer?.cancel();
    _analysisTimer = null;
    
    // 执行最终分析
    if (_collectedData.isNotEmpty) {
      _performBatchAnalysis();
      _collectedData.clear();
    }
  }

  void _performBatchAnalysis() {
    if (_collectedData.isEmpty) return;

    // 计算汇总指标
    final averageVolume = _collectedData
        .map((d) => d.volume)
        .reduce((a, b) => a + b) / _collectedData.length;

    final confidenceValues = _collectedData
        .where((d) => d.metadata?['confidence'] != null)
        .map((d) => d.metadata!['confidence'] as double);
    
    final averageConfidence = confidenceValues.isEmpty ? 0.0 :
        confidenceValues.reduce((a, b) => a + b) / confidenceValues.length;

    // 创建批次分析结果
    final batchAnalysis = {
      'timestamp': DateTime.now().toIso8601String(),
      'type': 'batch_analysis',
      'metrics': {
        'averageVolume': averageVolume,
        'averageConfidence': averageConfidence,
        'sampleCount': _collectedData.length,
        'duration': _collectedData.last.metadata?['duration'] ?? 0,
      },
      'samples': _collectedData.map((d) => d.toJson()).toList(),
    };

    // 保存批次分析结果
    _saveAnalysis(batchAnalysis);
  }

  Future<List<Map<String, dynamic>>> getAnalysisHistory() async {
    final records = await _nasService.getVoiceRecords();
    return records
        .where((record) => record['type'] == 'voice_analysis')
        .map((record) => record['content'] as Map<String, dynamic>)
        .toList();
  }

  void dispose() {
    _analysisController.close();
    _analysisTimer?.cancel();
    _voiceService.dispose();
  }

  // Getters
  bool get isCollecting => _isCollecting;
  Stream<Map<String, dynamic>> get analysisStream => _analysisController.stream;
  VoiceService get voiceService => _voiceService;
} 