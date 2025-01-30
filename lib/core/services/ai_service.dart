abstract class AiService {
  Future<String> generateText(String prompt);
  Future<List<double>> getEmbeddings(String text);
  Future<String> generateResponse(String message) async {
    // 实现生成响应的逻辑
    return 'Response to $message';
  }
}
