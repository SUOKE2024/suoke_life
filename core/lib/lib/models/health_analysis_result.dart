class HealthAnalysisResult {
  final String dietPlan;
  final String exercisePlan;
  final String tcmAdjustments;
  final List<String> riskFactors;

  HealthAnalysisResult({
    required this.dietPlan,
    required this.exercisePlan,
    required this.tcmAdjustments,
    required this.riskFactors,
  });
}
