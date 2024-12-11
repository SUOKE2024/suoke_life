import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../logging/app_logger.dart';

enum NetworkStatus {
  online,
  offline,
}

class NetworkMonitor {
  static final NetworkMonitor _instance = NetworkMonitor._internal();
  static NetworkMonitor get instance => _instance;

  final _connectivity = Connectivity();
  final _logger = AppLogger.instance;
  final _statusController = StreamController<NetworkStatus>.broadcast();
  StreamSubscription? _subscription;
  NetworkStatus _status = NetworkStatus.online;

  NetworkMonitor._internal();

  Stream<NetworkStatus> get statusStream => _statusController.stream;
  NetworkStatus get status => _status;

  Future<void> init() async {
    try {
      final result = await _connectivity.checkConnectivity();
      _updateStatus(result);

      _subscription = _connectivity.onConnectivityChanged.listen(_updateStatus);
    } catch (e) {
      _logger.error('初始化网络监听器失败', error: e);
    }
  }

  void _updateStatus(ConnectivityResult result) {
    final newStatus = result == ConnectivityResult.none
        ? NetworkStatus.offline
        : NetworkStatus.online;

    if (newStatus != _status) {
      _status = newStatus;
      _statusController.add(_status);
      _logger.info('网络状态变更: $_status');
    }
  }

  Future<bool> isOnline() async {
    final result = await _connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }

  void dispose() {
    _subscription?.cancel();
    _statusController.close();
  }
} 