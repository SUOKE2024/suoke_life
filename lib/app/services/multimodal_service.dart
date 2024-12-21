import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'ai_service.dart';
import 'speech_recognition_service.dart';
import 'text_to_speech_service.dart';

class MultimodalService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final AiService _aiService = Get.find();
  final SpeechRecognitionService _speechService = Get.find();
  final TextToSpeechService _ttsService = Get.find();

  final currentMode = 'text'.obs;
  final isProcessing = false.obs;
  final lastInteraction = Rx<DateTime?>(null);

  // 处理多模态输入
  Future<Map<String, dynamic>> processInput(
    dynamic input,
    String mode, {
    Map<String, dynamic>? options,
  }) async {
    if (isProcessing.value) {
      return {'error': '正在处理上一个输入,请稍候...'};
    }

    try {
      isProcessing.value = true;
      currentMode.value = mode;

      final result = await _processInputByMode(input, mode, options);
      await _saveInteraction(input, result, mode);

      return result;
    } catch (e) {
      await _loggingService.log('error', 'Failed to process input', data: {'error': e.toString()});
      return {'error': '处理输入时出现错误'};
    } finally {
      isProcessing.value = false;
      lastInteraction.value = DateTime.now();
    }
  }

  // 生成多模态输出
  Future<Map<String, dynamic>> generateOutput(
    Map<String, dynamic> data,
    List<String> modes,
  ) async {
    try {
      final outputs = <String, dynamic>{};

      for (final mode in modes) {
        outputs[mode] = await _generateOutputByMode(data, mode);
      }

      return outputs;
    } catch (e) {
      await _loggingService.log('error', 'Failed to generate output', data: {'error': e.toString()});
      return {'error': '生成输出时出现错误'};
    }
  }

  Future<Map<String, dynamic>> _processInputByMode(
    dynamic input,
    String mode,
    Map<String, dynamic>? options,
  ) async {
    switch (mode) {
      case 'text':
        return await _processTextInput(input as String);
      case 'voice':
        return await _processVoiceInput(input as List<int>);
      case 'image':
        return await _processImageInput(input as List<int>);
      case 'video':
        return await _processVideoInput(input as List<int>);
      case 'gesture':
        return await _processGestureInput(input as Map<String, dynamic>);
      default:
        throw Exception('Unsupported input mode: $mode');
    }
  }

  Future<dynamic> _generateOutputByMode(
    Map<String, dynamic> data,
    String mode,
  ) async {
    switch (mode) {
      case 'text':
        return await _generateTextOutput(data);
      case 'voice':
        return await _generateVoiceOutput(data);
      case 'image':
        return await _generateImageOutput(data);
      case 'animation':
        return await _generateAnimationOutput(data);
      default:
        throw Exception('Unsupported output mode: $mode');
    }
  }

  Future<Map<String, dynamic>> _processTextInput(String text) async {
    try {
      return await _aiService.queryKnowledge(
        'process_text',
        parameters: {'text': text},
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _processVoiceInput(List<int> audioData) async {
    try {
      // 语音识别
      await _speechService.startListening();
      // TODO: 处理音频数据
      await _speechService.stopListening();
      
      return {
        'text': _speechService.recognizedText.value,
        'confidence': _speechService.confidence.value,
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _processImageInput(List<int> imageData) async {
    try {
      return await _aiService.queryKnowledge(
        'process_image',
        parameters: {'image_data': imageData},
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _processVideoInput(List<int> videoData) async {
    try {
      return await _aiService.queryKnowledge(
        'process_video',
        parameters: {'video_data': videoData},
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _processGestureInput(Map<String, dynamic> gestureData) async {
    try {
      return await _aiService.queryKnowledge(
        'process_gesture',
        parameters: gestureData,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<String> _generateTextOutput(Map<String, dynamic> data) async {
    try {
      final response = await _aiService.queryKnowledge(
        'generate_text',
        parameters: data,
      );
      return response['text'] ?? '';
    } catch (e) {
      rethrow;
    }
  }

  Future<List<int>> _generateVoiceOutput(Map<String, dynamic> data) async {
    try {
      final text = data['text'] as String;
      await _ttsService.speak(text);
      // TODO: 返回音频数据
      return [];
    } catch (e) {
      rethrow;
    }
  }

  Future<List<int>> _generateImageOutput(Map<String, dynamic> data) async {
    try {
      final response = await _aiService.queryKnowledge(
        'generate_image',
        parameters: data,
      );
      return List<int>.from(response['image_data']);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<int>> _generateAnimationOutput(Map<String, dynamic> data) async {
    try {
      final response = await _aiService.queryKnowledge(
        'generate_animation',
        parameters: data,
      );
      return List<int>.from(response['animation_data']);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveInteraction(
    dynamic input,
    Map<String, dynamic> output,
    String mode,
  ) async {
    try {
      final interaction = {
        'input': input,
        'output': output,
        'mode': mode,
        'timestamp': DateTime.now().toIso8601String(),
      };

      final history = await _getInteractionHistory();
      history.insert(0, interaction);

      // 只保留最近100条记录
      if (history.length > 100) {
        history.removeRange(100, history.length);
      }

      await _storageService.saveLocal('multimodal_history', history);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getInteractionHistory() async {
    try {
      final data = await _storageService.getLocal('multimodal_history');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }
} 