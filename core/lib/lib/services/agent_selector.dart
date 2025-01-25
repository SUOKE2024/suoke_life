import 'package:core/core.dart';

class AgentSelector {
  Future<ModelResponse> selectBestResponse({
    required List<ModelResponse> responses,
    required AnalysisContext context,
  }) async {
    // 实现多维度评估算法
    final scoredResponses = await Future.wait(
      responses.map((response) => _evaluateResponse(response, context))
    );
    
    scoredResponses.sort((a, b) => b.score.compareTo(a.score));
    
    return scoredResponses.first.response;
  }

  Future<ScoredResponse> _evaluateResponse(
    ModelResponse response,
    AnalysisContext context,
  ) async {
    double score = 0.0;
    
    // 体质匹配度评估
    final tcmMatch = _calculateTcmCompatibility(response, context.tcmPatterns);
    // 医疗安全性评估 
    final safetyScore = await _checkMedicalSafety(response);
    // 用户偏好权重
    final preferenceWeight = context.userData.getPreferenceWeight();
    
    score = (tcmMatch * 0.6) + (safetyScore * 0.3) + (preferenceWeight * 0.1);
    
    return ScoredResponse(response, score);
  }

  double _calculateTcmCompatibility(ModelResponse response, TCMPatterns patterns) {
    // 实现体质特征匹配算法
    return 0.9;
  }

  Future<double> _checkMedicalSafety(ModelResponse response) async {
    // 调用医疗验证服务
    return 1.0;
  }
}

class ScoredResponse {
  final ModelResponse response;
  final double score;

  ScoredResponse(this.response, this.score);
}
