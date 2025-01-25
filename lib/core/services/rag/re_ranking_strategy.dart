abstract class ReRankingStrategy {
  Future<List<String>> reRankContext(String query, List<String> contextTexts);
} 