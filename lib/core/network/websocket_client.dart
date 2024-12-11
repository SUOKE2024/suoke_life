import 'dart:async';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../logging/app_logger.dart';

enum ConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
}

class WebSocketClient {
  static final WebSocketClient _instance = WebSocketClient._internal();
  static WebSocketClient get instance => _instance;

  WebSocketChannel? _channel;
  final _logger = AppLogger.instance;
  final _messageController = StreamController<dynamic>.broadcast();
  final _stateController = StreamController<ConnectionState>.broadcast();
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  ConnectionState _state = ConnectionState.disconnected;
  String? _authToken;

  WebSocketClient._internal();

  Stream<dynamic> get messageStream => _messageController.stream;
  Stream<ConnectionState> get stateStream => _stateController.stream;
  ConnectionState get state => _state;

  Future<void> connect(String url) async {
    if (_state == ConnectionState.connected || 
        _state == ConnectionState.connecting) {
      return;
    }

    _updateState(ConnectionState.connecting);

    try {
      final uri = Uri.parse(url);
      _channel = WebSocketChannel.connect(uri);
      
      _channel!.stream.listen(
        _onMessage,
        onError: _onError,
        onDone: _onDone,
        cancelOnError: true,
      );

      _updateState(ConnectionState.connected);
      _startPingTimer();
      
      _logger.info('WebSocket连接成功');
    } catch (e) {
      _logger.error('WebSocket连接失败', error: e);
      _onError(e);
    }
  }

  void _onMessage(dynamic message) {
    _logger.debug('收到WebSocket消息: $message');
    _messageController.add(message);
  }

  void _onError(dynamic error) {
    _logger.error('WebSocket错误', error: error);
    _updateState(ConnectionState.disconnected);
    _startReconnectTimer();
  }

  void _onDone() {
    _logger.info('WebSocket连接关闭');
    _updateState(ConnectionState.disconnected);
    _startReconnectTimer();
  }

  void _updateState(ConnectionState newState) {
    _state = newState;
    _stateController.add(newState);
  }

  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (_state == ConnectionState.connected) {
        send('ping');
      }
    });
  }

  void _startReconnectTimer() {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (_state == ConnectionState.disconnected) {
        _updateState(ConnectionState.reconnecting);
        connect('wss://ws.suoke.life');
      }
    });
  }

  void send(dynamic message) {
    if (_state != ConnectionState.connected) {
      _logger.warning('WebSocket未连接,无法发送消息');
      return;
    }

    try {
      _channel?.sink.add(message);
      _logger.debug('发送WebSocket消息: $message');
    } catch (e) {
      _logger.error('发送WebSocket消息失败', error: e);
    }
  }

  void setAuthToken(String token) {
    _authToken = token;
    // 如果已连接,需要重新连接以使用新token
    if (_state == ConnectionState.connected) {
      disconnect();
      connect('wss://ws.suoke.life');
    }
  }

  Future<void> disconnect() async {
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    await _channel?.sink.close(status.goingAway);
    _updateState(ConnectionState.disconnected);
  }

  void dispose() {
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    _messageController.close();
    _stateController.close();
    _channel?.sink.close(status.goingAway);
  }
} 