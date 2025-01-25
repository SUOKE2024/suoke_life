import 'package:core/core.dart';
import 'package:injectable/injectable.dart';

@Injectable(as: HealthAnalysisService)
class HealthAnalysisServiceImpl implements HealthAnalysisService {
  final LLMServiceClient _llmClient;
  final MultimodalServiceClient _multimodalClient;
  final AgentSelector _agentSelector;

  HealthAnalysisServiceImpl(
    this._llmClient,
    this._multimodalClient,
    this._agentSelector,
  );

  @override
  Future<HealthAnalysisResult> analyzeHealthData({
    required MultimodalInput input,
    required TCMPatterns tcmPatterns,
  }) async {
    final processedData = await _multimodalClient.processInput(input);
    
    final responses = await Future.wait([
      _llmClient.query('claude-3', _buildAnalysisPrompt(processedData)),
      _llmClient.query('gpt-4-med', _buildMedicalPrompt(tcmPatterns)),
      _llmClient.query('ernie-health', _buildTCMPrompt(tcmPatterns)),
    ]);

    final selectedResponse = await _agentSelector.selectBestResponse(
      responses: responses,
      context: AnalysisContext(
        userData: processedData.userProfile,
        tcmPatterns: tcmPatterns,
      ),
    );

    return HealthAnalysisResult(
      dietPlan: selectedResponse.dietAdvice,
      exercisePlan: selectedResponse.exerciseRecommendation,
      tcmAdjustments: selectedResponse.tcmSuggestions,
      riskFactors: selectedResponse.healthRisks,
    );
  }

  // ...prompt构建方法
}
