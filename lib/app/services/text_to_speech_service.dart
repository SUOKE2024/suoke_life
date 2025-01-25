import 'package:get/get.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class TextToSpeechService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final _flutterTts = FlutterTts();

  final isSpeaking = false.obs;
  final isPaused = false.obs;
  final currentText = ''.obs;
  final progress = 0.0.obs;

  @override
  void onInit() {
    super.onInit();
    _initTextToSpeech();
  }

  Future<void> _initTextToSpeech() async {
    try {
      await _loadSettings();
      await _configureTextToSpeech();
      await _setCallbacks();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize text to speech', data: {'error': e.toString()});
    }
  }

  // 开始语音合成
  Future<void> speak(String text) async {
    if (isSpeaking.value) {
      await stop();
    }

    try {
      currentText.value = text;
      await _flutterTts.speak(text);
      isSpeaking.value = true;
      isPaused.value = false;
      progress.value = 0.0;
      
      // 记录合成历史
      await _saveToHistory(text);
    } catch (e) {
      await _loggingService.log('error', 'Failed to speak text', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 暂停语音合成
  Future<void> pause() async {
    if (!isSpeaking.value || isPaused.value) return;

    try {
      await _flutterTts.pause();
      isPaused.value = true;
    } catch (e) {
      await _loggingService.log('error', 'Failed to pause speech', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 继续语音合成
  Future<void> resume() async {
    if (!isPaused.value) return;

    try {
      await _flutterTts.speak(currentText.value);
      isPaused.value = false;
    } catch (e) {
      await _loggingService.log('error', 'Failed to resume speech', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 停止语音合成
  Future<void> stop() async {
    if (!isSpeaking.value) return;

    try {
      await _flutterTts.stop();
      isSpeaking.value = false;
      isPaused.value = false;
      progress.value = 0.0;
    } catch (e) {
      await _loggingService.log('error', 'Failed to stop speech', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 更新设置
  Future<void> updateSettings(Map<String, dynamic> settings) async {
    try {
      await _storageService.saveLocal('tts_settings', settings);
      await _configureTextToSpeech();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update TTS settings', data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadSettings() async {
    try {
      final settings = await _storageService.getLocal('tts_settings');
      if (settings == null) {
        await _saveDefaultSettings();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveDefaultSettings() async {
    try {
      final settings = {
        'language': 'zh-CN',
        'pitch': 1.0,
        'rate': 0.5,
        'volume': 1.0,
      };
      await _storageService.saveLocal('tts_settings', settings);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _configureTextToSpeech() async {
    try {
      final settings = await _storageService.getLocal('tts_settings');
      if (settings != null) {
        await _flutterTts.setLanguage(settings['language']);
        await _flutterTts.setPitch(settings['pitch']);
        await _flutterTts.setSpeechRate(settings['rate']);
        await _flutterTts.setVolume(settings['volume']);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _setCallbacks() async {
    _flutterTts.setStartHandler(() {
      isSpeaking.value = true;
      _logEvent('Started speaking');
    });

    _flutterTts.setCompletionHandler(() {
      isSpeaking.value = false;
      isPaused.value = false;
      progress.value = 1.0;
      _logEvent('Completed speaking');
    });

    _flutterTts.setProgressHandler((text, start, end, word) {
      progress.value = start / end;
      _logEvent('Speaking progress', {'word': word, 'progress': progress.value});
    });

    _flutterTts.setErrorHandler((msg) {
      isSpeaking.value = false;
      isPaused.value = false;
      _logEvent('Error speaking', {'error': msg});
    });
  }

  Future<void> _saveToHistory(String text) async {
    try {
      final history = await _getHistory();
      history.insert(0, {
        'text': text,
        'timestamp': DateTime.now().toIso8601String(),
      });

      // 只保留最近100条记录
      if (history.length > 100) {
        history.removeRange(100, history.length);
      }

      await _storageService.saveLocal('tts_history', history);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getHistory() async {
    try {
      final data = await _storageService.getLocal('tts_history');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  Future<void> _logEvent(String event, [Map<String, dynamic>? data]) async {
    try {
      await _loggingService.log('info', 'TTS event: $event', data: data);
    } catch (e) {
      // 忽略日志错误
    }
  }
} 