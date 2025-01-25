import 'package:injectable/injectable.dart';

@injectable
class SpeechService {
  Future<String> recognizeSpeech() async {
    // 实现语音识别逻辑
    return 'Recognized speech';
  }
} 