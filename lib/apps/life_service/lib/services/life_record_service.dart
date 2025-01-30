import 'package:suoke_life/lib/core/network/life_service_client.dart';

class LifeRecordService {
  final LifeServiceClient _lifeServiceClient;

  LifeRecordService(this._lifeServiceClient);

  Future<String> getLifeRecords(String userId) async {
    final response = await _lifeServiceClient.getLifeRecords(userId);
    return 'Life records: ${response.data}';
  }
} 