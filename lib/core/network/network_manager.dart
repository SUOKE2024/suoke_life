import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:get/get.dart';

class NetworkManager extends GetxService {
  final _connectivity = Connectivity();
  final isConnected = true.obs;
  final connectionType = ConnectivityResult.none.obs;

  @override
  void onInit() {
    super.onInit();
    _initConnectivity();
    _setupConnectivityStream();
  }

  Future<void> _initConnectivity() async {
    try {
      final result = await _connectivity.checkConnectivity();
      _updateConnectionStatus(result);
    } catch (e) {
      isConnected.value = false;
    }
  }

  void _setupConnectivityStream() {
    _connectivity.onConnectivityChanged.listen(_updateConnectionStatus);
  }

  void _updateConnectionStatus(ConnectivityResult result) {
    connectionType.value = result;
    isConnected.value = result != ConnectivityResult.none;
  }

  bool get isOnline => isConnected.value;
  
  bool get isWifi => connectionType.value == ConnectivityResult.wifi;
  
  bool get isMobile => connectionType.value == ConnectivityResult.mobile;
} 