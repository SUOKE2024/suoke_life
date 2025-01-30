import 'package:suoke_life/lib/core/services/rag/context_compression_strategy.dart';

class KeywordExtractionCompressionStrategy
    implements ContextCompressionStrategy {
  @override
  Future<List<String>> compressContext(List<String> contextTexts) async {
    // TODO:  集成关键词提取算法或服务，从 contextTexts 中提取关键词
    //       这里只是一个示例，简单地返回每段文本的前几个词作为关键词
    List<String> compressedContexts = [];
    for (final text in contextTexts) {
      final words = text.split(' ');
      if (words.length <= 10) {
        compressedContexts.add(text); //  如果文本长度小于等于 10 个词，则不压缩
      } else {
        compressedContexts
            .add('${words.sublist(0, 10).join(' ')}...'); //  提取前 10 个词作为关键词
      }
    }
    return compressedContexts;
  }
}
