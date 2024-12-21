import 'package:flutter_tts/flutter_tts.dart';

class TextToSpeechService {
  final FlutterTts _tts;
  bool _isInitialized = false;

  TextToSpeechService() : _tts = FlutterTts();

  Future<void> init() async {
    await _tts.setLanguage('zh-CN');
    await _tts.setSpeechRate(1.0);
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);
    
    _isInitialized = true;
  }

  Future<void> speak(String text) async {
    if (!_isInitialized) {
      throw Exception('语音合成未初始化');
    }

    await _tts.speak(text);
  }

  Future<void> stop() async {
    await _tts.stop();
  }

  Future<void> pause() async {
    await _tts.pause();
  }

  Future<void> resume() async {
    await _tts.resume();
  }

  Future<void> setLanguage(String language) async {
    await _tts.setLanguage(language);
  }

  Future<void> setVolume(double volume) async {
    await _tts.setVolume(volume);
  }

  Future<void> setSpeechRate(double rate) async {
    await _tts.setSpeechRate(rate);
  }

  Future<void> setPitch(double pitch) async {
    await _tts.setPitch(pitch);
  }
} 