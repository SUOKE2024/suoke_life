import 'package:injectable/injectable.dart';
import '../network/network_service.dart';
import '../logger/logger.dart';

@singleton
class GraphRAGService {
  final NetworkService _network;
  final AppLogger _logger;

  GraphRAGService(this._network, this._logger);

  Future<Map<String, dynamic>> queryKnowledgeGraph(String query) async {
    try {
      final response = await _network.post('/graph/query', {'query': query});
      return response;
    } catch (e, stack) {
      _logger.error('Error querying knowledge graph', e, stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getGraphData(String topic) async {
    try {
      final response = await _network.get('/graph/data/$topic');
      return response;
    } catch (e, stack) {
      _logger.error('Error getting graph data', e, stack);
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getRecommendations(String userId) async {
    try {
      final response = await _network.get('/graph/recommendations/$userId');
      return List<Map<String, dynamic>>.from(response['recommendations']);
    } catch (e, stack) {
      _logger.error('Error getting recommendations', e, stack);
      rethrow;
    }
  }
} 