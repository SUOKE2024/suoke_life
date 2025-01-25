class SessionManager {
  static final instance = SessionManager._();
  SessionManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _currentSession = Rxn<UserSession>();
  final _isActive = true.obs;
  
  Timer? _inactivityTimer;
  Timer? _heartbeatTimer;

  // 配置
  static const _config = {
    'session_timeout': 1800000,    // 会话超时时间（30分钟）
    'heartbeat_interval': 300000,  // 心跳间隔（5分钟）
    'inactivity_threshold': 300000,// 不活动阈值（5分钟）
  };

  Future<void> initialize() async {
    // 恢复上次会话
    await _restoreSession();
    
    // 启动心跳
    _startHeartbeat();
    
    // 监听应用生命周期
    final lifecycleManager = Get.find<AppLifecycleManager>();
    ever(lifecycleManager.state, _handleLifecycleChange);
  }

  Future<void> _restoreSession() async {
    final sessionData = await _storage.getObject<Map<String, dynamic>>(
      'current_session',
      (json) => json,
    );

    if (sessionData != null) {
      _currentSession.value = UserSession.fromJson(sessionData);
      _eventBus.fire(SessionRestoredEvent(_currentSession.value!));
    }
  }

  Future<void> startSession(User user) async {
    final session = UserSession(
      id: const Uuid().v4(),
      userId: user.id,
      startTime: DateTime.now(),
      deviceInfo: Get.find<DeviceManager>().metadata,
    );

    _currentSession.value = session;
    _isActive.value = true;
    
    await _storage.setObject('current_session', session.toJson());
    _eventBus.fire(SessionStartedEvent(session));
    
    _resetInactivityTimer();
  }

  Future<void> endSession() async {
    if (_currentSession.value != null) {
      _currentSession.value!.end();
      _eventBus.fire(SessionEndedEvent(_currentSession.value!));
      
      await _storage.remove('current_session');
      _currentSession.value = null;
    }

    _inactivityTimer?.cancel();
    _heartbeatTimer?.cancel();
  }

  void recordActivity() {
    if (_currentSession.value == null) return;
    
    _isActive.value = true;
    _resetInactivityTimer();
    _currentSession.value!.recordActivity();
  }

  void _resetInactivityTimer() {
    _inactivityTimer?.cancel();
    _inactivityTimer = Timer(
      Duration(milliseconds: _config['inactivity_threshold']!),
      _handleInactivity,
    );
  }

  void _handleInactivity() {
    _isActive.value = false;
    _eventBus.fire(SessionInactiveEvent());
  }

  void _startHeartbeat() {
    _heartbeatTimer = Timer.periodic(
      Duration(milliseconds: _config['heartbeat_interval']!),
      (_) => _sendHeartbeat(),
    );
  }

  Future<void> _sendHeartbeat() async {
    if (_currentSession.value == null) return;

    try {
      final apiClient = Get.find<ApiClient>();
      await apiClient.post(
        '/api/sessions/heartbeat',
        data: {
          'session_id': _currentSession.value!.id,
          'timestamp': DateTime.now().toIso8601String(),
          'is_active': _isActive.value,
        },
      );
    } catch (e) {
      LoggerManager.instance.error('Session heartbeat failed', e);
    }
  }

  void _handleLifecycleChange(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.resumed:
        _isActive.value = true;
        _resetInactivityTimer();
        break;
      case AppLifecycleState.paused:
        _isActive.value = false;
        break;
      default:
        break;
    }
  }

  bool get hasActiveSession => _currentSession.value != null;
  bool get isActive => _isActive.value;
  UserSession? get currentSession => _currentSession.value;
}

class UserSession {
  final String id;
  final String userId;
  final DateTime startTime;
  final Map<String, dynamic> deviceInfo;
  DateTime? endTime;
  
  final _activities = <SessionActivity>[];

  UserSession({
    required this.id,
    required this.userId,
    required this.startTime,
    required this.deviceInfo,
  });

  void end() {
    endTime = DateTime.now();
  }

  void recordActivity() {
    _activities.add(SessionActivity(timestamp: DateTime.now()));
  }

  Duration get duration {
    final end = endTime ?? DateTime.now();
    return end.difference(startTime);
  }

  factory UserSession.fromJson(Map<String, dynamic> json) => UserSession(
    id: json['id'],
    userId: json['userId'],
    startTime: DateTime.parse(json['startTime']),
    deviceInfo: Map<String, dynamic>.from(json['deviceInfo']),
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'userId': userId,
    'startTime': startTime.toIso8601String(),
    'endTime': endTime?.toIso8601String(),
    'deviceInfo': deviceInfo,
    'activities': _activities.map((a) => a.toJson()).toList(),
  };
}

class SessionActivity {
  final DateTime timestamp;
  final String? type;
  final Map<String, dynamic>? data;

  SessionActivity({
    required this.timestamp,
    this.type,
    this.data,
  });

  Map<String, dynamic> toJson() => {
    'timestamp': timestamp.toIso8601String(),
    'type': type,
    'data': data,
  };
}

// 会话相关事件
class SessionStartedEvent extends AppEvent {
  final UserSession session;
  SessionStartedEvent(this.session);
}

class SessionEndedEvent extends AppEvent {
  final UserSession session;
  SessionEndedEvent(this.session);
}

class SessionRestoredEvent extends AppEvent {
  final UserSession session;
  SessionRestoredEvent(this.session);
}

class SessionInactiveEvent extends AppEvent {} 