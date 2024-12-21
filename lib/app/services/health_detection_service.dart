import 'package:get/get.dart';
import '../data/models/health_record.dart';
import 'ai_service.dart';

class HealthDetectionService extends GetxService {
  final AiService _aiService = Get.find();

  Future<Map<String, dynamic>> detectHealthStatus(HealthRecord record) async {
    try {
      // 使用 AI 分析健康数据
      final analysis = await _aiService.queryKnowledge(
        'analyze_health_data',
        parameters: record.data,
      );

      // 生成健康建议
      final advice = await _generateHealthAdvice(analysis);

      return {
        'status': analysis['status'],
        'risk_level': analysis['risk_level'],
        'advice': advice,
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _generateHealthAdvice(Map<String, dynamic> analysis) async {
    try {
      final prompt = _buildHealthAdvicePrompt(analysis);
      final response = await _aiService.chatWithAssistant(prompt, 'xiaoi');
      
      return response.split('\n').where((line) => line.isNotEmpty).toList();
    } catch (e) {
      return ['暂时无法生成健康建议'];
    }
  }

  String _buildHealthAdvicePrompt(Map<String, dynamic> analysis) {
    return '''
    基于以下健康分析数据生成具体的健康建议:
    - 健康状态: ${analysis['status']}
    - 风险等级: ${analysis['risk_level']}
    - 异常指标: ${analysis['abnormal_indicators']}
    
    请给出3-5条具体可行的建议。
    ''';
  }
} 