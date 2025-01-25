class EventBus {
  static final instance = EventBus._();
  EventBus._();

  final _eventController = StreamController<AppEvent>.broadcast();
  final _subscriptions = <Type, List<StreamSubscription>>{};

  void fire(AppEvent event) {
    _eventController.add(event);
  }

  StreamSubscription<T> on<T extends AppEvent>(void Function(T event) handler) {
    final subscription = _eventController.stream
        .where((event) => event is T)
        .cast<T>()
        .listen(handler);

    _subscriptions.putIfAbsent(T, () => []).add(subscription);
    return subscription;
  }

  void off<T extends AppEvent>() {
    final subscriptions = _subscriptions[T];
    if (subscriptions != null) {
      for (final subscription in subscriptions) {
        subscription.cancel();
      }
      _subscriptions.remove(T);
    }
  }

  void dispose() {
    for (final subscriptions in _subscriptions.values) {
      for (final subscription in subscriptions) {
        subscription.cancel();
      }
    }
    _subscriptions.clear();
    _eventController.close();
  }
}

abstract class AppEvent {
  final DateTime timestamp = DateTime.now();
} 