class SecurityMonitorService extends GetxService {
  final _eventStream = StreamController<SecurityEvent>.broadcast();
  
  void reportEvent(SecurityEvent event) {
    _eventStream.add(event);
    
    // 根据事件类型和严重程度采取相应措施
    switch (event.severity) {
      case Severity.high:
        _handleHighSeverityEvent(event);
        break;
      case Severity.medium:
        _handleMediumSeverityEvent(event);
        break;
      case Severity.low:
        _handleLowSeverityEvent(event);
        break;
    }
  }
  
  Future<void> _handleHighSeverityEvent(SecurityEvent event) async {
    // 1. 记录日志
    await _logEvent(event);
    
    // 2. 发送通知
    await _sendNotification(event);
    
    // 3. 可能需要采取自动防护措施
    if (event.requiresAction) {
      await _takeProtectiveAction(event);
    }
  }

  Future<void> _logEvent(SecurityEvent event) async {
    final logEntry = {
      'timestamp': DateTime.now().toIso8601String(),
      'type': event.type,
      'severity': event.severity.toString(),
      'details': event.details,
      'userId': event.userId,
      'deviceId': event.deviceId,
    };
    
    await _storage.appendToList('security_logs', logEntry);
  }

  Future<void> _sendNotification(SecurityEvent event) async {
    final notification = SecurityNotification(
      title: '安全警告',
      body: _getNotificationBody(event),
      data: event.toJson(),
    );
    
    // 根据事件严重程度选择通知方式
    if (event.severity == Severity.high) {
      await _notificationService.sendUrgentNotification(notification);
    } else {
      await _notificationService.sendNotification(notification);
    }
  }

  Future<void> _takeProtectiveAction(SecurityEvent event) async {
    switch (event.type) {
      case SecurityEventType.bruteForceAttempt:
        await _lockAccount(event.userId);
        break;
      case SecurityEventType.suspiciousAccess:
        await _requireAdditionalVerification(event.userId);
        break;
      case SecurityEventType.maliciousActivity:
        await _blockDevice(event.deviceId);
        break;
    }
  }
} 