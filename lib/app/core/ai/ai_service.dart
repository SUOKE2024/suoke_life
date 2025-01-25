import 'package:injectable/injectable.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';
import '../logger/logger.dart';
import '../network/network_service.dart';

@singleton
class AIService {
  final NetworkService _network;
  final AppLogger _logger;
  final FlutterTts _tts;
  final SpeechToText _stt;

  AIService(this._network, this._logger)
      : _tts = FlutterTts(),
        _stt = SpeechToText();

  Future<void> init() async {
    try {
      await _initTTS();
      await _initSTT();
    } catch (e, stack) {
      _logger.error('Error initializing AI service', e, stack);
    }
  }

  Future<void> _initTTS() async {
    await _tts.setLanguage('zh-CN');
    await _tts.setPitch(1.0);
    await _tts.setSpeechRate(0.5);
  }

  Future<void> _initSTT() async {
    await _stt.initialize();
  }

  Future<void> speak(String text) async {
    try {
      await _tts.speak(text);
    } catch (e, stack) {
      _logger.error('Error in text-to-speech', e, stack);
    }
  }

  Future<void> startListening(Function(String) onResult) async {
    try {
      await _stt.listen(
        onResult: (result) {
          if (result.finalResult) {
            onResult(result.recognizedWords);
          }
        },
        localeId: 'zh_CN',
      );
    } catch (e, stack) {
      _logger.error('Error in speech-to-text', e, stack);
    }
  }

  Future<void> stopListening() async {
    await _stt.stop();
  }

  Future<Map<String, dynamic>> analyze(String text) async {
    try {
      final response = await _network.post('/ai/analyze', {'text': text});
      return response;
    } catch (e, stack) {
      _logger.error('Error analyzing text', e, stack);
      rethrow;
    }
  }
} 