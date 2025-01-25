import 'package:injectable/injectable.dart';
import 'base_ai_service.dart';

@injectable
class EmbeddingService extends BaseAiService {
  EmbeddingService(super.network);

  Future<List<double>> getEmbeddings(String text) async {
    final response = await post('/embeddings', data: {
      'model': 'ep-20241207124339-rh46z', // 老克
      'input': [text],
    });
    
    return List<double>.from(response['data'][0]['embedding']);
  }
} 