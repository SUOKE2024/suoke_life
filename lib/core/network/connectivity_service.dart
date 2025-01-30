import 'package:injectable/injectable.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:rxdart/rxdart.dart';
import '../logger/logger.dart';

@singleton
class ConnectivityService {
  final Connectivity _connectivity;
  final AppLogger _logger;
  final BehaviorSubject<ConnectivityResult> _connectionStatus;

  ConnectivityService(this._connectivity, this._logger)
      : _connectionStatus = BehaviorSubject<ConnectivityResult>();

  Stream<ConnectivityResult> get connectionStream => _connectionStatus.stream;
  ConnectivityResult get currentStatus => _connectionStatus.value;

  Future<void> init() async {
    try {
      final initialResult = await _connectivity.checkConnectivity();
      _connectionStatus.add(initialResult);

      _connectivity.onConnectivityChanged.listen((result) {
        _connectionStatus.add(result);
        _logger.info('Connectivity changed: $result');
      });
    } catch (e, stack) {
      _logger.error('Error initializing connectivity service', e, stack);
    }
  }

  bool get isConnected => 
      currentStatus != ConnectivityResult.none;

  bool get isWifi =>
      currentStatus == ConnectivityResult.wifi;

  bool get isMobile =>
      currentStatus == ConnectivityResult.mobile;

  Future<bool> checkConnectivity() async {
    try {
      final result = await _connectivity.checkConnectivity();
      return result != ConnectivityResult.none;
    } catch (e, stack) {
      _logger.error('Error checking connectivity', e, stack);
      return false;
    }
  }

  void dispose() {
    _connectionStatus.close();
  }
} 