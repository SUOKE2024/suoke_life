import 'package:suoke_life/core/services/rag/context_compression_strategy.dart';

class NoCompressionStrategy implements ContextCompressionStrategy {
  @override
  Future<List<String>> compressContext(List<String> contextTexts) async {
    return contextTexts; //  不进行任何压缩，直接返回原始上下文
  }
} 