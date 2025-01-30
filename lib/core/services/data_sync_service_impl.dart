import 'package:suoke_life/lib/core/models/health_data.dart';
import 'package:suoke_life/lib/core/models/life_activity_data.dart';
import 'package:suoke_life/lib/core/models/user.dart';
import 'package:suoke_life/lib/core/repositories/health_data_repository.dart';
import 'package:suoke_life/lib/core/repositories/life_activity_data_repository.dart';
import 'package:suoke_life/lib/core/repositories/user_repository.dart';
import 'package:suoke_life/lib/core/services/data_sync_service.dart';
import 'package:suoke_life/lib/core/services/network_service.dart';
import 'package:suoke_life/lib/core/services/privacy_service.dart';
import 'package:suoke_life/lib/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/lib/core/services/infrastructure/database_service.dart';
import 'package:suoke_life/lib/core/services/infrastructure/redis_service.dart';

class DataSyncServiceImpl implements DataSyncService {
  final UserRepository _userRepository;
  final HealthDataRepository _healthDataRepository;
  final LifeActivityDataRepository _lifeActivityDataRepository;
  final NetworkService _networkService;
  final PrivacyService _privacyService;
  final LocalStorageService _localStorageService;
  final DatabaseService _databaseService;
  final RedisService _redisService;

  DataSyncServiceImpl(
    this._userRepository,
    this._healthDataRepository,
    this._lifeActivityDataRepository,
    this._networkService,
    this._privacyService,
    this._localStorageService,
    this._databaseService,
    this._redisService,
  );

  @override
  Future<void> syncUserData() async {
    final userId = await _privacyService.getUserId();
    // Sync user profile data if needed
    await _syncHealthData(userId);
    await _syncLifeActivityData(userId);
  }

  Future<void> _syncHealthData(String userId) async {
    try {
      final localHealthDataList =
          await _healthDataRepository.getHealthData(userId);
      final remoteHealthDataList = await _networkService.getHealthData(userId);
      final mergedHealthDataList = _mergeHealthData(localHealthDataList, remoteHealthDataList);
      await _healthDataRepository.saveHealthData(mergedHealthDataList);
      print('Health data synced successfully');
    } catch (e) {
      print('Error syncing health data: $e');
    }
  }

  Future<void> _syncLifeActivityData(String userId) async {
    try {
      final lifeActivityDataList =
          await _lifeActivityDataRepository.getLifeActivityData(userId);
      final remoteLifeActivityDataList = await _networkService.getLifeActivityData(userId);
      final mergedLifeActivityDataList = _mergeLifeActivityData(lifeActivityDataList, remoteLifeActivityDataList);
      await _lifeActivityDataRepository.saveLifeActivityData(mergedLifeActivityDataList);
      print('Life activity data synced successfully');
    } catch (e) {
      print('Error syncing life activity data: $e');
    }
  }

  List<HealthData> _mergeHealthData(List<HealthData> localData, List<HealthData> remoteData) {
    // 示例：实现冲突解决和数据合并逻辑
    // 这里简单地返回本地数据，实际实现中需要根据业务逻辑合并数据
    return localData;
  }

  List<LifeActivityData> _mergeLifeActivityData(List<LifeActivityData> localData, List<LifeActivityData> remoteData) {
    // 示例：实现冲突解决和数据合并逻辑
    // 这里简单地返回本地数据，实际实现中需要根据业务逻辑合并数据
    return localData;
  }

  @override
  Future<void> addToList(dynamic data) async {
    if (data is User) {
      await _userRepository.addUser(data);
    } else if (data is HealthData) {
      await _healthDataRepository.addHealthData(data);
    } else if (data is LifeActivityData) {
      await _lifeActivityDataRepository.addLifeActivityData(data);
    }
  }

  @override
  Future<void> syncData() async {
    await syncUserData(); // 直接调用现有的用户数据同步方法
    // 可以根据需要添加其他类型数据的同步逻辑
    print('All data sync processes initiated.');
  }
}
