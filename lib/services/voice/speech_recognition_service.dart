import 'package:speech_to_text/speech_to_text.dart';
import 'package:permission_handler/permission_handler.dart';

class SpeechRecognitionService {
  final SpeechToText _speech;
  bool _isInitialized = false;

  SpeechRecognitionService() : _speech = SpeechToText();

  Future<void> init() async {
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      throw Exception('需要麦克风权限');
    }

    _isInitialized = await _speech.initialize(
      onError: (error) => print('Speech recognition error: $error'),
      onStatus: (status) => print('Speech recognition status: $status'),
    );
  }

  Future<void> startListening({
    required Function(String) onResult,
    String? locale,
  }) async {
    if (!_isInitialized) {
      throw Exception('语音识别未初始化');
    }

    await _speech.listen(
      onResult: (result) {
        if (result.finalResult) {
          onResult(result.recognizedWords);
        }
      },
      localeId: locale,
      listenMode: ListenMode.confirmation,
      cancelOnError: true,
      partialResults: false,
    );
  }

  Future<void> stopListening() async {
    await _speech.stop();
  }

  bool get isListening => _speech.isListening;
  bool get isAvailable => _speech.isAvailable;
} 