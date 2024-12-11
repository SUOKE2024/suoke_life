import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../core/network/websocket_client.dart';
import 'error_handler_service.dart';

enum ConnectionState {
  connecting,
  connected,
  disconnected,
  reconnecting,
  failed
}

class ConnectionStats {
  final int latency;
  final int packetLoss;
  final int bitrate;
  final DateTime timestamp;

  ConnectionStats({
    required this.latency,
    required this.packetLoss,
    required this.bitrate,
    required this.timestamp,
  });
}

class ConnectionManagerService {
  final WebSocketClient _wsClient;
  final ErrorHandlerService _errorHandler;
  final Connectivity _connectivity = Connectivity();
  
  late StreamSubscription<ConnectivityResult> _connectivitySubscription;
  final _connectionStateController = StreamController<ConnectionState>.broadcast();
  final _connectionStatsController = StreamController<ConnectionStats>.broadcast();
  
  Timer? _heartbeatTimer;
  Timer? _reconnectTimer;
  DateTime? _lastHeartbeatResponse;
  
  bool _isConnected = false;
  int _reconnectAttempts = 0;
  static const int maxReconnectAttempts = 5;
  static const Duration reconnectDelay = Duration(seconds: 3);
  static const Duration heartbeatInterval = Duration(seconds: 5);

  ConnectionManagerService({
    required WebSocketClient wsClient,
    required ErrorHandlerService errorHandler,
  }) : _wsClient = wsClient,
       _errorHandler = errorHandler {
    _initializeConnectivityMonitoring();
    _initializeHeartbeat();
  }

  void _initializeConnectivityMonitoring() {
    _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
      (ConnectivityResult result) {
        if (result == ConnectivityResult.none) {
          _handleDisconnection();
        } else if (!_isConnected) {
          _attemptReconnection();
        }
      }
    );
  }

  void _initializeHeartbeat() {
    _heartbeatTimer = Timer.periodic(heartbeatInterval, (_) {
      _sendHeartbeat();
    });
  }

  Future<void> _sendHeartbeat() async {
    try {
      if (_isConnected) {
        await _wsClient.send({'type': 'heartbeat'});
        _lastHeartbeatResponse = DateTime.now();
      }
    } catch (e) {
      _errorHandler.handleNetworkError(e, StackTrace.current);
      _handleDisconnection();
    }
  }

  void _handleDisconnection() {
    _isConnected = false;
    _connectionStateController.add(ConnectionState.disconnected);
    _attemptReconnection();
  }

  Future<void> _attemptReconnection() async {
    if (_reconnectAttempts >= maxReconnectAttempts) {
      _connectionStateController.add(ConnectionState.failed);
      _errorHandler.handleError(
        'RECONNECTION_FAILED',
        '重连失败: 已达到最大重试次数',
        ErrorSeverity.high,
      );
      return;
    }

    _connectionStateController.add(ConnectionState.reconnecting);
    _reconnectAttempts++;

    try {
      final connectivityResult = await _connectivity.checkConnectivity();
      if (connectivityResult != ConnectivityResult.none) {
        await _wsClient.reconnect();
        _isConnected = true;
        _reconnectAttempts = 0;
        _connectionStateController.add(ConnectionState.connected);
      }
    } catch (e) {
      _errorHandler.handleNetworkError(e, StackTrace.current);
      _reconnectTimer = Timer(reconnectDelay, _attemptReconnection);
    }
  }

  Future<void> connect() async {
    try {
      _connectionStateController.add(ConnectionState.connecting);
      await _wsClient.connect();
      _isConnected = true;
      _connectionStateController.add(ConnectionState.connected);
      _initializeHeartbeat();
    } catch (e) {
      _errorHandler.handleNetworkError(e, StackTrace.current);
      _handleDisconnection();
    }
  }

  Future<void> disconnect() async {
    _heartbeatTimer?.cancel();
    _reconnectTimer?.cancel();
    _isConnected = false;
    await _wsClient.disconnect();
    _connectionStateController.add(ConnectionState.disconnected);
  }

  void updateConnectionStats() {
    if (!_isConnected) return;

    // 这里应该实现实际的网络状态检测逻辑
    // 以下是示例数据
    final stats = ConnectionStats(
      latency: 50, // 毫秒
      packetLoss: 0, // 百分比
      bitrate: 1500, // kbps
      timestamp: DateTime.now(),
    );

    _connectionStatsController.add(stats);
  }

  bool get isConnected => _isConnected;
  Stream<ConnectionState> get connectionState => _connectionStateController.stream;
  Stream<ConnectionStats> get connectionStats => _connectionStatsController.stream;

  void dispose() {
    _connectivitySubscription.cancel();
    _heartbeatTimer?.cancel();
    _reconnectTimer?.cancel();
    _connectionStateController.close();
    _connectionStatsController.close();
  }
} 