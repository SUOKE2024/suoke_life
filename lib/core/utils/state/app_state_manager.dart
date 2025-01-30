class AppStateManager {
  static final instance = AppStateManager._();
  AppStateManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  // 全局状态
  final appState = AppState();
  final _stateHistory = <StateSnapshot>[];
  
  // 状态监听器
  final _stateListeners = <String, List<StateChangeCallback>>{};
  
  static const _config = {
    'max_history_size': 50,
    'persist_keys': ['theme', 'language', 'notifications'],
  };

  Future<void> initialize() async {
    // 恢复持久化的状态
    await _restorePersistedState();
    
    // 设置状态变更监听
    _setupStateListeners();
    
    // 初始化完成事件
    _eventBus.fire(AppStateInitializedEvent());
  }

  Future<void> _restorePersistedState() async {
    final persistedState = await _storage.getObject<Map<String, dynamic>>(
      'app_state',
      (json) => json,
    );

    if (persistedState != null) {
      for (final key in _config['persist_keys']) {
        if (persistedState.containsKey(key)) {
          appState.setValue(key, persistedState[key]);
        }
      }
    }
  }

  void _setupStateListeners() {
    appState.addListener(_handleStateChange);
  }

  void _handleStateChange(String key, dynamic oldValue, dynamic newValue) {
    // 记录状态变更
    _stateHistory.add(StateSnapshot(
      key: key,
      oldValue: oldValue,
      newValue: newValue,
      timestamp: DateTime.now(),
    ));

    // 限制历史记录大小
    while (_stateHistory.length > _config['max_history_size']) {
      _stateHistory.removeAt(0);
    }

    // 触发监听器
    final listeners = _stateListeners[key] ?? [];
    for (final listener in listeners) {
      listener(oldValue, newValue);
    }

    // 持久化需要保存的状态
    if (_config['persist_keys'].contains(key)) {
      _persistState();
    }

    // 发送状态变更事件
    _eventBus.fire(StateChangedEvent(
      key: key,
      oldValue: oldValue,
      newValue: newValue,
    ));
  }

  Future<void> _persistState() async {
    final stateToSave = <String, dynamic>{};
    for (final key in _config['persist_keys']) {
      stateToSave[key] = appState.getValue(key);
    }
    await _storage.setObject('app_state', stateToSave);
  }

  void addListener(String key, StateChangeCallback listener) {
    _stateListeners.putIfAbsent(key, () => []).add(listener);
  }

  void removeListener(String key, StateChangeCallback listener) {
    _stateListeners[key]?.remove(listener);
    if (_stateListeners[key]?.isEmpty ?? false) {
      _stateListeners.remove(key);
    }
  }

  List<StateSnapshot> getStateHistory() => List.unmodifiable(_stateHistory);

  void resetState() {
    appState.reset();
    _stateHistory.clear();
    _storage.remove('app_state');
    _eventBus.fire(AppStateResetEvent());
  }
}

class AppState extends ChangeNotifier {
  final _values = <String, dynamic>{};
  
  T? getValue<T>(String key) => _values[key] as T?;
  
  void setValue(String key, dynamic value) {
    final oldValue = _values[key];
    if (oldValue != value) {
      _values[key] = value;
      notifyListeners();
    }
  }

  void reset() {
    _values.clear();
    notifyListeners();
  }
}

class StateSnapshot {
  final String key;
  final dynamic oldValue;
  final dynamic newValue;
  final DateTime timestamp;

  StateSnapshot({
    required this.key,
    required this.oldValue,
    required this.newValue,
    required this.timestamp,
  });
}

typedef StateChangeCallback = void Function(dynamic oldValue, dynamic newValue);

// 状态相关事件
class AppStateInitializedEvent extends AppEvent {}

class StateChangedEvent extends AppEvent {
  final String key;
  final dynamic oldValue;
  final dynamic newValue;

  StateChangedEvent({
    required this.key,
    required this.oldValue,
    required this.newValue,
  });
}

class AppStateResetEvent extends AppEvent {} 