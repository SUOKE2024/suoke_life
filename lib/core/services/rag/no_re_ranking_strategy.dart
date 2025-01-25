import 'package:suoke_life/core/services/rag/re_ranking_strategy.dart';

class NoReRankingStrategy implements ReRankingStrategy {
  @override
  Future<List<String>> reRankContext(String query, List<String> contextTexts) async {
    return contextTexts; //  不进行任何重排序，直接返回原始顺序
  }
} 