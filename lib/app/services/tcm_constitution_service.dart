import 'package:get/get.dart';
import '../data/models/health_record.dart';
import 'ai_service.dart';

class TcmConstitutionService extends GetxService {
  final AiService _aiService = Get.find();

  Future<Map<String, dynamic>> analyzeConstitution(Map<String, dynamic> data) async {
    try {
      // 分析体质特征
      final analysis = await _aiService.queryKnowledge(
        'analyze_tcm_constitution',
        parameters: data,
      );

      // 生成养生建议
      final advice = await _generateTcmAdvice(analysis);

      return {
        'constitution_type': analysis['type'],
        'characteristics': analysis['characteristics'],
        'advice': advice,
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, List<String>>> _generateTcmAdvice(Map<String, dynamic> analysis) async {
    try {
      final prompt = _buildTcmAdvicePrompt(analysis);
      final response = await _aiService.chatWithAssistant(prompt, 'xiaoi');
      
      // 解析建议内容
      return {
        'diet': _extractAdvice(response, '饮食建议'),
        'lifestyle': _extractAdvice(response, '起居建议'),
        'exercise': _extractAdvice(response, '运动建议'),
        'prevention': _extractAdvice(response, '调养建议'),
      };
    } catch (e) {
      return {
        'diet': ['暂无建议'],
        'lifestyle': ['暂无建议'],
        'exercise': ['暂无建议'],
        'prevention': ['暂无建议'],
      };
    }
  }

  String _buildTcmAdvicePrompt(Map<String, dynamic> analysis) {
    return '''
    基于以下中医体质分析结果生成养生建议:
    - 体质类型: ${analysis['type']}
    - 主要特征: ${analysis['characteristics'].join('、')}
    
    请分别从饮食、起居、运动、调养四个方面给出具体建议。
    ''';
  }

  List<String> _extractAdvice(String response, String category) {
    final regex = RegExp('$category：(.*?)(?=\\n|$)');
    final match = regex.firstMatch(response);
    if (match != null) {
      return match.group(1)?.split('；').where((s) => s.isNotEmpty).toList() ?? ['暂无建议'];
    }
    return ['暂无建议'];
  }
} 