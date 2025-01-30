abstract class AiService {
  Future<String> generateText(String prompt);
  Future<List<double>> getEmbeddings(String text);
}
