import 'package:get/get.dart';
import '../core/config/app_config.dart';
import 'doubao_service.dart';

class AiService extends GetxService {
  final DouBaoService _douBaoService = Get.find();

  // AI助手类型
  static const assistantTypes = {
    'xiaoi': '生活管家',
    'laoke': '知识顾问', 
    'xiaoke': '商务助手'
  };

  Future<AiService> init() async {
    return this;
  }

  Future<String> chatWithAssistant(String message, String assistantType) async {
    if (!assistantTypes.containsKey(assistantType)) {
      throw Exception('Invalid assistant type');
    }

    try {
      return await _douBaoService.chat(message, assistantType);
    } catch (e) {
      print('Error chatting with assistant: $e');
      return '抱歉，我现在无法回答您的问题';
    }
  }

  Future<List<double>> getEmbeddings(String text) async {
    try {
      return await _douBaoService.getEmbeddings(text);
    } catch (e) {
      print('Error getting embeddings: $e');
      return [];
    }
  }
} 