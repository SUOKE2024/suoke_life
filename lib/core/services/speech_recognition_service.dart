import 'package:get/get.dart';
import 'package:speech_to_text/speech_to_text.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class SpeechRecognitionService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final _speechToText = SpeechToText();

  final isListening = false.obs;
  final recognizedText = ''.obs;
  final confidence = 0.0.obs;

  @override
  void onInit() {
    super.onInit();
    _initSpeechRecognition();
  }

  Future<void> _initSpeechRecognition() async {
    try {
      final available = await _speechToText.initialize(
        onError: (error) => _handleError(error),
        onStatus: (status) => _handleStatus(status),
      );

      if (!available) {
        throw Exception('Speech recognition not available');
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize speech recognition', data: {'error': e.toString()});
    }
  }

  // 开始语音识别
  Future<void> startListening() async {
    if (isListening.value) return;

    try {
      await _speechToText.listen(
        onResult: _handleResult,
        listenFor: const Duration(seconds: 30),
        pauseFor: const Duration(seconds: 3),
        partialResults: true,
        cancelOnError: true,
        listenMode: ListenMode.confirmation,
      );
      
      isListening.value = true;
    } catch (e) {
      await _loggingService.log('error', 'Failed to start listening', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 停止语音识别
  Future<void> stopListening() async {
    if (!isListening.value) return;

    try {
      await _speechToText.stop();
      isListening.value = false;
      
      // 保存识别结果
      if (recognizedText.value.isNotEmpty) {
        await _saveRecognitionResult();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to stop listening', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 取消语音识别
  Future<void> cancelListening() async {
    if (!isListening.value) return;

    try {
      await _speechToText.cancel();
      isListening.value = false;
      recognizedText.value = '';
      confidence.value = 0.0;
    } catch (e) {
      await _loggingService.log('error', 'Failed to cancel listening', data: {'error': e.toString()});
      rethrow;
    }
  }

  void _handleResult(SpeechRecognitionResult result) {
    try {
      recognizedText.value = result.recognizedWords;
      confidence.value = result.confidence;
      
      // 记录识别结果
      _logRecognitionResult(result);
    } catch (e) {
      _loggingService.log('error', 'Failed to handle recognition result', data: {'error': e.toString()});
    }
  }

  void _handleError(dynamic error) {
    _loggingService.log('error', 'Speech recognition error', data: {'error': error.toString()});
  }

  void _handleStatus(String status) {
    _loggingService.log('info', 'Speech recognition status', data: {'status': status});
  }

  Future<void> _saveRecognitionResult() async {
    try {
      final results = await _getRecognitionHistory();
      results.insert(0, {
        'text': recognizedText.value,
        'confidence': confidence.value,
        'timestamp': DateTime.now().toIso8601String(),
      });

      // 只保留最近100条记录
      if (results.length > 100) {
        results.removeRange(100, results.length);
      }

      await _storageService.saveLocal('recognition_history', results);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getRecognitionHistory() async {
    try {
      final data = await _storageService.getLocal('recognition_history');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  Future<void> _logRecognitionResult(SpeechRecognitionResult result) async {
    try {
      await _loggingService.log('info', 'Speech recognition result', data: {
        'text': result.recognizedWords,
        'confidence': result.confidence,
        'hasConfidence': result.hasConfidence,
        'finalResult': result.finalResult,
      });
    } catch (e) {
      // 忽略日志错误
    }
  }
} 