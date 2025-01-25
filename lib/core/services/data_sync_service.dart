abstract class DataSyncService {
  Future<void> syncUserData();
  Future<void> addToList(dynamic data);
  Future<void> syncData();
} 