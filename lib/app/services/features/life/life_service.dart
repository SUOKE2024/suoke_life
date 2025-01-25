import 'package:injectable/injectable.dart';
import '../../../core/network/network_service.dart';
import '../../../core/storage/storage_service.dart';
import '../../../data/models/life_record.dart';

@injectable
class LifeService {
  final NetworkService _network;
  final StorageService _storage;

  LifeService(this._network, this._storage);

  Future<Map<String, dynamic>> getUserProfile() async {
    final response = await _network.get('/life/profile');
    return response.data;
  }

  Future<List<Map<String, dynamic>>> getHealthAdvices() async {
    final response = await _network.get('/life/health-advices');
    return List<Map<String, dynamic>>.from(response.data);
  }

  Future<List<LifeRecord>> getLifeRecords() async {
    final response = await _network.get('/life/records');
    return (response.data as List)
        .map((json) => LifeRecord.fromJson(json))
        .toList();
  }

  Future<void> addLifeRecord(LifeRecord record) async {
    await _network.post(
      '/life/records',
      data: record.toJson(),
    );
  }

  Future<void> updateLifeRecord(LifeRecord record) async {
    await _network.post(
      '/life/records/${record.id}',
      data: record.toJson(),
    );
  }

  Future<void> deleteLifeRecord(String id) async {
    await _network.delete('/life/records/$id');
  }
} 