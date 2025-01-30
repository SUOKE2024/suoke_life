class AppLifecycleManager with WidgetsBindingObserver {
  static final instance = AppLifecycleManager._();
  AppLifecycleManager._();

  final _eventBus = Get.find<EventBus>();
  final _currentState = Rx<AppLifecycleState>(AppLifecycleState.resumed);
  DateTime? _lastPausedTime;
  
  void initialize() {
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    _currentState.value = state;
    
    switch (state) {
      case AppLifecycleState.resumed:
        _handleResumed();
        break;
      case AppLifecycleState.paused:
        _handlePaused();
        break;
      case AppLifecycleState.inactive:
        _handleInactive();
        break;
      case AppLifecycleState.detached:
        _handleDetached();
        break;
    }
  }

  void _handleResumed() {
    if (_lastPausedTime != null) {
      final pauseDuration = DateTime.now().difference(_lastPausedTime!);
      _eventBus.fire(AppResumedEvent(pauseDuration: pauseDuration));
    }
    _lastPausedTime = null;
  }

  void _handlePaused() {
    _lastPausedTime = DateTime.now();
    _eventBus.fire(AppPausedEvent());
  }

  void _handleInactive() {
    _eventBus.fire(AppInactiveEvent());
  }

  void _handleDetached() {
    _eventBus.fire(AppDetachedEvent());
  }

  AppLifecycleState get currentState => _currentState.value;
  Stream<AppLifecycleState> get stateStream => _currentState.stream;

  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
  }
}

// 生命周期事件
class AppResumedEvent extends AppEvent {
  final Duration pauseDuration;
  AppResumedEvent({required this.pauseDuration});
}

class AppPausedEvent extends AppEvent {}
class AppInactiveEvent extends AppEvent {}
class AppDetachedEvent extends AppEvent {} 