import 'package:injectable/injectable.dart';
import '../network/network_service.dart';
import '../logger/logger.dart';

@singleton
class AgricultureService {
  final NetworkService _network;
  final AppLogger _logger;

  AgricultureService(this._network, this._logger);

  Future<Map<String, dynamic>> getPlantingPlan(String userId) async {
    try {
      final response = await _network.get('/agriculture/plan/$userId');
      return response;
    } catch (e, stack) {
      _logger.error('Error getting planting plan', e, stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getWeatherForecast(
    double latitude,
    double longitude,
  ) async {
    try {
      final response = await _network.get(
        '/agriculture/weather',
        params: {
          'lat': latitude.toString(),
          'lon': longitude.toString(),
        },
      );
      return response;
    } catch (e, stack) {
      _logger.error('Error getting weather forecast', e, stack);
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getProducts() async {
    try {
      final response = await _network.get('/agriculture/products');
      return List<Map<String, dynamic>>.from(response['products']);
    } catch (e, stack) {
      _logger.error('Error getting products', e, stack);
      rethrow;
    }
  }

  Future<void> createOrder(Map<String, dynamic> orderData) async {
    try {
      await _network.post('/agriculture/orders', orderData);
    } catch (e, stack) {
      _logger.error('Error creating order', e, stack);
      rethrow;
    }
  }
} 