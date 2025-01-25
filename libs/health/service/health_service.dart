abstract class HealthAdviceService {
  Future<HealthRecommendation> getRecommendations(UserHealthProfile profile);
  Future<HealthAssessment> assessHealthData(HealthData data);
}
