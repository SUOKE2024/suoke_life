// import 'package:injectable/injectable.dart';
import '../../../core/network/network_service.dart';
import 'package:logger/logger.dart';

class AggregationService {
  final NetworkService _network;
  final Logger _logger = Logger();

  AggregationService(this._network);

  Future<Map<String, dynamic>> analyzeBehaviorPatterns() async {
    _logger.i('Analyzing behavior patterns');
    final data = (await _network.get('/analytics/aggregate/behavior')).data;
    _logger.i('Behavior patterns analysis result: $data');
    return data;
  }

  Future<Map<String, dynamic>> analyzeKnowledgeGraph() async {
    _logger.i('Analyzing knowledge graph');
    final data = (await _network.get('/analytics/aggregate/knowledge')).data;
    _logger.i('Knowledge graph analysis result: $data');
    return data;
  }

  Future<Map<String, dynamic>> analyzeSystemPerformance() async {
    _logger.i('Analyzing system performance');
    final data = (await _network.get('/analytics/aggregate/system')).data;
    _logger.i('System performance analysis result: $data');
    return data;
  }

  Future<List<Map<String, dynamic>>> getOptimizationSuggestions() async {
    _logger.i('Getting optimization suggestions');
    final data = (await _network.get('/analytics/suggestions')).data;
    _logger.i('Optimization suggestions: $data');
    return data;
  }
} 