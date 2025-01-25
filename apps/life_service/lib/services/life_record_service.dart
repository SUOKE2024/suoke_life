import 'package:injectable/injectable.dart';
import 'package:suoke_life/core/network/life_service_client.dart';

@injectable
class LifeRecordService {
  final LifeServiceClient _lifeServiceClient;

  LifeRecordService(this._lifeServiceClient);

  Future<String> getLifeRecords(String userId) async {
    final response = await _lifeServiceClient.getLifeRecords(userId);
    return 'Life records: ${response.data}';
  }
} 