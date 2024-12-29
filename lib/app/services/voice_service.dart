import 'package:get/get.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

class VoiceService extends GetxService {
  final SpeechRecognition speechRecognition;
  final TextToSpeech textToSpeech;
  
  Future<void> processVoiceCommand(VoiceCommand command) async {
    try {
      final text = await speechRecognition.recognize(command);
      final response = await processText(text);
      await textToSpeech.speak(response);
    } catch (e) {
      // 错误处理
    }
  }
} 