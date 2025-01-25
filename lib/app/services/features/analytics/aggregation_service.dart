import 'package:injectable/injectable.dart';
import '../../../core/network/network_service.dart';

@lazySingleton
class AggregationService {
  final NetworkService _network;

  AggregationService(this._network);

  Future<Map<String, dynamic>> analyzeBehaviorPatterns() async {
    return (await _network.get('/analytics/aggregate/behavior')).data;
  }

  Future<Map<String, dynamic>> analyzeKnowledgeGraph() async {
    return (await _network.get('/analytics/aggregate/knowledge')).data;
  }

  Future<Map<String, dynamic>> analyzeSystemPerformance() async {
    return (await _network.get('/analytics/aggregate/system')).data;
  }

  Future<List<Map<String, dynamic>>> getOptimizationSuggestions() async {
    return (await _network.get('/analytics/suggestions')).data;
  }
} 