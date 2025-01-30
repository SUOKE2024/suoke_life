import 'package:get/get.dart';

abstract class BaseAIService {
  Future<String> chat(String input);
  Future<bool> handleVoiceInput(String audioPath);
  Future<String?> generateVoiceOutput(String text);
}
