import 'package:injectable/injectable.dart';
import '../../domain/services/life_service.dart';
import '../../core/network/network_service.dart';
import '../providers/database_provider.dart';

@Injectable(as: LifeService)
class LifeServiceImpl implements LifeService {
  final NetworkService _network;
  final DatabaseProvider _db;

  const LifeServiceImpl(this._network, this._db);

  @override
  Future<Map<String, dynamic>> getData() async {
    try {
      final localData = await _db.query('life_data');
      if (localData.isNotEmpty) {
        return localData.first;
      }
      
      final remoteData = await _network.get('/life/data');
      await _db.insert('life_data', remoteData);
      return remoteData;
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<void> updateData(Map<String, dynamic> data) async {
    await _db.update('life_data', data);
    await _network.post('/life/data', data);
  }
} 