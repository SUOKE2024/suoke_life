import 'package:suoke_life/core/services/rag/context_compression_strategy.dart';

class SummaryCompressionStrategy implements ContextCompressionStrategy {
  @override
  Future<List<String>> compressContext(List<String> contextTexts) async {
    // TODO:  集成摘要生成模型或服务，对 contextTexts 进行摘要压缩
    //       这里只是一个示例，简单地返回前两段文本作为摘要
    if (contextTexts.length <= 2) {
      return contextTexts;
    } else {
      return contextTexts.sublist(0, 2); //  返回前两段文本作为摘要
    }
  }
} 