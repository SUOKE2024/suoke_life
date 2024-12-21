class NetworkService extends GetxService {
  final _connectivity = Get.find<ConnectivityService>();
  final _syncService = Get.find<SyncService>();
  
  // 监听网络状态
  @override
  void onInit() {
    super.onInit();
    ever(_connectivity.status, _handleConnectivityChange);
  }
  
  void _handleConnectivityChange(ConnectivityResult result) {
    if (result != ConnectivityResult.none) {
      // 网络恢复时自动同步
      _syncService.syncData();
    }
  }
} 