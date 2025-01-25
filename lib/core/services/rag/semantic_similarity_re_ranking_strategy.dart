import 'package:suoke_life/core/services/rag/re_ranking_strategy.dart';

class SemanticSimilarityReRankingStrategy implements ReRankingStrategy {
  @override
  Future<List<String>> reRankContext(String query, List<String> contextTexts) async {
    // TODO:  集成语义相似度模型或服务，计算 query 和 contextTexts 中每段文本的语义相似度
    //       并根据相似度进行重排序
    //       这里只是一个示例，简单地将文本长度较短的排在前面
    contextTexts.sort((a, b) => a.length.compareTo(b.length)); //  按文本长度升序排序
    return contextTexts;
  }
} 