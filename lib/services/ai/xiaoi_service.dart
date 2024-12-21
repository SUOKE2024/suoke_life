import 'package:dio/dio.dart';
import 'ai_service.dart';
import '../../models/health_analysis.dart';

class XiaoiService implements AIService {
  final AIServiceImpl _aiService;
  final Dio _dio;

  XiaoiService(this._aiService) : _dio = Dio(BaseOptions(
    baseUrl: 'https://api.suoke.life/v1',
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
  ));

  @override
  Future<String> getResponse(String text) async {
    try {
      // 1. 分析文本是否包含健康相关内容
      final healthAnalysis = await analyzeHealth(text);
      
      // 2. 如果包含健康内容,使用健康模式回复
      if (healthAnalysis['isHealthRelated']) {
        final advice = await generateHealthAdvice(healthAnalysis);
        return advice;
      }
      
      // 3. 否则使用通用对话模式
      return _aiService.chat(
        model: AIModel.xiaoAi,
        message: text,
      );
    } catch (e) {
      print('Error in getResponse: $e');
      return '抱歉,我现在无法回答您的问题。请稍后再试。';
    }
  }

  @override
  Future<String> speechToText(String audioPath) async {
    try {
      final formData = FormData.fromMap({
        'audio': await MultipartFile.fromFile(audioPath),
      });

      final response = await _dio.post(
        '/speech/recognize',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data['text'];
      }
      throw Exception('语音识别失败');
    } catch (e) {
      print('Error in speechToText: $e');
      throw Exception('语音识别服务异常');
    }
  }

  @override
  Future<Map<String, dynamic>> analyzeImage(String imagePath) async {
    try {
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(imagePath),
      });

      final response = await _dio.post(
        '/vision/analyze',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data;
      }
      throw Exception('图像分析失败');
    } catch (e) {
      print('Error in analyzeImage: $e');
      throw Exception('图像分析服务异常');
    }
  }

  @override
  Future<String> getImageResponse(Map<String, dynamic> analysis) async {
    try {
      // 根据图像分析结果生成回复
      final response = await _dio.post(
        '/vision/interpret',
        data: analysis,
      );

      if (response.statusCode == 200) {
        return response.data['response'];
      }
      throw Exception('生成回复失败');
    } catch (e) {
      print('Error in getImageResponse: $e');
      return '抱歉,我无法理解这张图片。';
    }
  }

  // 健康相关功能
  Future<Map<String, dynamic>> analyzeHealth(String text) async {
    try {
      final response = await _dio.post(
        '/health/analyze',
        data: {'text': text},
      );

      if (response.statusCode == 200) {
        return response.data;
      }
      throw Exception('健康分析失败');
    } catch (e) {
      print('Error in analyzeHealth: $e');
      return {'isHealthRelated': false};
    }
  }

  Future<String> generateHealthAdvice(Map<String, dynamic> analysis) async {
    try {
      final response = await _dio.post(
        '/health/advice',
        data: analysis,
      );

      if (response.statusCode == 200) {
        return response.data['advice'];
      }
      throw Exception('生成建议失败');
    } catch (e) {
      print('Error in generateHealthAdvice: $e');
      return '抱歉,我现在无法给出健康建议。建议您咨询专业医生。';
    }
  }

  // 健康报告相关
  Future<HealthReport> generateHealthReport() async {
    try {
      final response = await _dio.get('/health/report');
      
      if (response.statusCode == 200) {
        return HealthReport.fromJson(response.data);
      }
      throw Exception('生成报告失败');
    } catch (e) {
      print('Error in generateHealthReport: $e');
      throw Exception('健康报告生成失败');
    }
  }

  // 提醒功能
  Future<void> setReminder(DateTime time, String content) async {
    try {
      await _dio.post(
        '/reminder/set',
        data: {
          'time': time.toIso8601String(),
          'content': content,
        },
      );
    } catch (e) {
      print('Error in setReminder: $e');
      throw Exception('设置提醒失败');
    }
  }
} 