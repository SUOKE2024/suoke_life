class CircuitBreaker {
  final int failureThreshold;
  final Duration resetTimeout;
  
  CircuitBreakerState _state = CircuitBreakerState.closed;
  int _failureCount = 0;
  DateTime? _lastFailure;
  DateTime? _lastStateChange;

  CircuitBreaker({
    required this.failureThreshold,
    required this.resetTimeout,
  });

  bool isOpen() => _state == CircuitBreakerState.open;
  bool isClosed() => _state == CircuitBreakerState.closed;
  bool isHalfOpen() => _state == CircuitBreakerState.halfOpen;

  void open() {
    _state = CircuitBreakerState.open;
    _lastStateChange = DateTime.now();
  }

  void close() {
    _state = CircuitBreakerState.closed;
    _failureCount = 0;
    _lastStateChange = DateTime.now();
  }

  void halfOpen() {
    _state = CircuitBreakerState.halfOpen;
    _lastStateChange = DateTime.now();
  }

  void recordSuccess() {
    if (isHalfOpen()) {
      close();
    }
    _failureCount = 0;
  }

  void recordFailure() {
    _failureCount++;
    _lastFailure = DateTime.now();
  }

  bool shouldOpen() {
    return _failureCount >= failureThreshold;
  }

  bool shouldAttemptReset() {
    if (!isOpen()) return false;
    
    final lastChange = _lastStateChange;
    if (lastChange == null) return true;
    
    return DateTime.now().difference(lastChange) >= resetTimeout;
  }

  Map<String, dynamic> getStatus() => {
    'state': _state.toString(),
    'failure_count': _failureCount,
    'last_failure': _lastFailure?.toIso8601String(),
    'last_state_change': _lastStateChange?.toIso8601String(),
  };
}

enum CircuitBreakerState {
  open,
  closed,
  halfOpen,
} 