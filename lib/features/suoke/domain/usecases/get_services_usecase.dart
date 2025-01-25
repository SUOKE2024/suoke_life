import 'package:suoke_life_app_app/core/network/network_service.dart';
import 'package:suoke_life_app_app/features/suoke/domain/entities/service_item.dart';

abstract class GetServicesUseCase {
  Future<List<ServiceItem>> execute();
}

class GetServicesUseCaseImpl implements GetServicesUseCase {
  final NetworkService _networkService;

  GetServicesUseCaseImpl(this._networkService);

  @override
  Future<List<ServiceItem>> execute() async {
    try {
      final response = await _networkService.get('/api/v1/services');
      final data = response.data as Map<String, dynamic>;
      
      return (data['items'] as List).map((item) => ServiceItem(
        id: item['serviceId'] as String,
        title: item['displayName'] as String,
        imagePath: item['thumbnailUrl'] as String,
        routePath: '/service/${item['serviceId']}',
        isVerified: (item['isApproved'] as bool?) ?? false,
      )).toList();
    } catch (e) {
      throw ServiceLoadException(
        message: '服务加载失败: ${e is DioException ? e.response?.statusCode ?? e.message : e}'
      );
    }
  }
}

class ServiceLoadException implements Exception {
  final String message;
  ServiceLoadException({required this.message});
  
  @override
  String toString() => message;
}
