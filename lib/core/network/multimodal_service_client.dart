import 'package:suoke_life/lib/core/services/network_service.dart';

class MultimodalServiceClient {
  final NetworkService _networkService;

  MultimodalServiceClient(this._networkService);

  Future<dynamic> processMultimodalData(dynamic data) async {
    final response = await _networkService.post('/multimodal/process', data);
    return response;
  }
} 