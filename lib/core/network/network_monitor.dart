class NetworkMonitor {
  static final instance = NetworkMonitor._();
  NetworkMonitor._();

  final _connectivity = Connectivity();
  final _connectionStatus = Rx<ConnectivityResult>(ConnectivityResult.none);
  final _isOnline = true.obs;
  final _eventBus = Get.find<EventBus>();
  
  StreamSubscription? _subscription;
  Timer? _pingTimer;

  Future<void> initialize() async {
    // 初始化连接状态
    _connectionStatus.value = await _connectivity.checkConnectivity();
    
    // 监听连接变化
    _subscription = _connectivity.onConnectivityChanged.listen((result) {
      _handleConnectivityChange(result);
    });

    // 定期检查网络连接
    _startPeriodicCheck();
  }

  void _handleConnectivityChange(ConnectivityResult result) {
    _connectionStatus.value = result;
    _checkConnection();
  }

  void _startPeriodicCheck() {
    _pingTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _checkConnection(),
    );
  }

  Future<void> _checkConnection() async {
    try {
      final result = await InternetAddress.lookup('google.com');
      final wasOnline = _isOnline.value;
      _isOnline.value = result.isNotEmpty && result[0].rawAddress.isNotEmpty;
      
      if (wasOnline != _isOnline.value) {
        _eventBus.fire(NetworkStatusChangedEvent(isOnline: _isOnline.value));
      }
    } on SocketException catch (_) {
      _isOnline.value = false;
      _eventBus.fire(NetworkStatusChangedEvent(isOnline: false));
    }
  }

  bool get isOnline => _isOnline.value;
  ConnectivityResult get connectionStatus => _connectionStatus.value;

  Stream<bool> get onlineStream => _isOnline.stream;
  Stream<ConnectivityResult> get connectionStream => _connectionStatus.stream;

  void dispose() {
    _subscription?.cancel();
    _pingTimer?.cancel();
  }
}

class NetworkStatusChangedEvent extends AppEvent {
  final bool isOnline;
  NetworkStatusChangedEvent({required this.isOnline});
} 