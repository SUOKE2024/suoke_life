import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:shared_preferences.dart';
import 'dart:io';
import 'dart:convert';
import 'package:path/path.dart' as path;
import '../models/voice_record.dart';
import 'nas_storage_service.dart';

enum VoiceLanguage {
  chinese('zh-CN', '中文'),
  english('en-US', 'English');

  final String code;
  final String label;
  const VoiceLanguage(this.code, this.label);
}

class VoiceSettings {
  final bool autoPlay;
  final double speechRate;
  final double pitch;
  final double volume;
  final VoiceLanguage language;
  final bool saveRecords;

  const VoiceSettings({
    this.autoPlay = true,
    this.speechRate = 0.5,
    this.pitch = 1.0,
    this.volume = 1.0,
    this.language = VoiceLanguage.chinese,
    this.saveRecords = true,
  });

  Map<String, dynamic> toJson() => {
    'autoPlay': autoPlay,
    'speechRate': speechRate,
    'pitch': pitch,
    'volume': volume,
    'language': language.code,
    'saveRecords': saveRecords,
  };

  factory VoiceSettings.fromJson(Map<String, dynamic> json) {
    return VoiceSettings(
      autoPlay: json['autoPlay'] as bool? ?? true,
      speechRate: json['speechRate'] as double? ?? 0.5,
      pitch: json['pitch'] as double? ?? 1.0,
      volume: json['volume'] as double? ?? 1.0,
      language: VoiceLanguage.values.firstWhere(
        (l) => l.code == json['language'],
        orElse: () => VoiceLanguage.chinese,
      ),
      saveRecords: json['saveRecords'] as bool? ?? true,
    );
  }
}

class VoiceService extends GetxController {
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  final NasStorageService _nasService;
  final SharedPreferences _prefs;
  
  bool _isInitialized = false;
  bool _isListening = false;
  bool _isSpeaking = false;
  VoiceSettings _settings;
  
  VoiceService({
    required String nasBasePath,
    required SharedPreferences prefs,
  })  : _nasService = NasStorageService(nasBasePath: nasBasePath),
        _prefs = prefs,
        _settings = VoiceSettings();

  bool get isListening => _isListening;
  bool get isSpeaking => _isSpeaking;
  VoiceSettings get settings => _settings;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // 初始化语音识别
    _isInitialized = await _speechToText.initialize(
      onError: (error) => print('Speech recognition error: $error'),
      debugLogging: kDebugMode,
    );

    // 初始化语音合成
    await _flutterTts.setLanguage(_settings.language.code);
    await _flutterTts.setSpeechRate(_settings.speechRate);
    await _flutterTts.setPitch(_settings.pitch);
    await _flutterTts.setVolume(_settings.volume);

    // 加载设置
    await loadSettings();

    // 设置语音合成状态回调
    _flutterTts.setStartHandler(() {
      _isSpeaking = true;
      update();
    });

    _flutterTts.setCompletionHandler(() {
      _isSpeaking = false;
      update();
    });

    _flutterTts.setErrorHandler((error) {
      _isSpeaking = false;
      update();
      print('TTS error: $error');
    });
  }

  Future<void> startListening({
    required Function(String) onResult,
    required Function() onComplete,
  }) async {
    if (!_isInitialized) await initialize();
    
    if (await _speechToText.hasPermission && _isInitialized) {
      _isListening = true;
      update();

      await _speechToText.listen(
        onResult: (result) async {
          final recognizedText = result.recognizedWords;
          onResult(recognizedText);
          
          if (result.finalResult && recognizedText.isNotEmpty) {
            if (_settings.saveRecords) {
              await _nasService.saveVoiceRecord(
                content: recognizedText,
                timestamp: DateTime.now(),
                type: 'voice_to_text',
              );
            }
            onComplete();
          }
        },
        localeId: _settings.language.code,
        listenMode: ListenMode.confirmation,
      );
    }
  }

  Future<void> stopListening() async {
    await _speechToText.stop();
    _isListening = false;
    update();
  }

  Future<void> speak(String text) async {
    if (!_isInitialized) await initialize();
    
    if (_isSpeaking) {
      await stop();
    }

    await _flutterTts.speak(text);
    
    if (_settings.saveRecords) {
      await _nasService.saveVoiceRecord(
        content: text,
        timestamp: DateTime.now(),
        type: 'text_to_voice',
      );
    }
  }

  Future<void> stop() async {
    await _flutterTts.stop();
    _isSpeaking = false;
    update();
  }

  Future<void> updateSettings(VoiceSettings newSettings) async {
    _settings = newSettings;
    
    // 更新TTS设置
    await _flutterTts.setLanguage(newSettings.language.code);
    await _flutterTts.setSpeechRate(newSettings.speechRate);
    await _flutterTts.setPitch(newSettings.pitch);
    await _flutterTts.setVolume(newSettings.volume);

    // 保存设置
    await _prefs.setString('voice_settings', jsonEncode(newSettings.toJson()));
    
    update();
  }

  Future<void> loadSettings() async {
    final settingsJson = _prefs.getString('voice_settings');
    if (settingsJson != null) {
      _settings = VoiceSettings.fromJson(jsonDecode(settingsJson));
      
      // 更新TTS设置
      await _flutterTts.setLanguage(_settings.language.code);
      await _flutterTts.setSpeechRate(_settings.speechRate);
      await _flutterTts.setPitch(_settings.pitch);
      await _flutterTts.setVolume(_settings.volume);
      
      update();
    }
  }

  Future<List<VoiceRecord>> getVoiceHistory() async {
    final records = await _nasService.getVoiceRecords();
    return records.map((record) {
      final Map<String, dynamic> jsonData = record['content'];
      return VoiceRecord.fromJson(jsonData);
    }).toList();
  }

  Future<void> clearVoiceHistory() async {
    try {
      final directory = Directory(path.join(_nasService.nasBasePath, 'voice_records'));
      if (await directory.exists()) {
        await directory.delete(recursive: true);
      }
      update();
    } catch (e) {
      print('清除语音记录失败: $e');
      rethrow;
    }
  }

  @override
  void dispose() {
    _speechToText.cancel();
    _flutterTts.stop();
    super.dispose();
  }
} 