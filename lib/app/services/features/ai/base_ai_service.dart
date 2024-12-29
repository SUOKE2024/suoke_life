import 'package:get/get.dart';
import '../../base_service.dart';

abstract class BaseAiService extends BaseService {
  String get name;
  String get description;
  String get model;
  
  Future<String> chat(String input);
  Future<bool> handleVoiceInput(String audioPath);
  Future<String?> generateVoiceOutput(String text);
} 