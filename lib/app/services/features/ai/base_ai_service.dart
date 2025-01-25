import 'package:get/get.dart';
import '../../base_service.dart';

abstract class BaseAIService {
  Future<String> chat(String input);
  Future<bool> handleVoiceInput(String audioPath);
  Future<String?> generateVoiceOutput(String text);
} 