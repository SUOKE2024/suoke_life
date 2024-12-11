# SUOKE-LIFE 错误处理指南

## 错误类型

### 基础错误类型
```dart
abstract class AppException implements Exception {
  final String message;
  final String? code;
  final dynamic details;
  final StackTrace? stackTrace;
  
  const AppException({
    required this.message,
    this.code,
    this.details,
    this.stackTrace,
  });
  
  @override
  String toString() => 'AppException: $message (Code: $code)';
  
  Map<String, dynamic> toJson() => {
    'message': message,
    'code': code,
    'details': details,
    'stackTrace': stackTrace?.toString(),
  };
}

class NetworkException extends AppException {
  final int? statusCode;
  final String? url;
  
  const NetworkException({
    required String message,
    String? code,
    this.statusCode,
    this.url,
    dynamic details,
    StackTrace? stackTrace,
  }) : super(
    message: message,
    code: code ?? 'NETWORK_ERROR',
    details: details,
    stackTrace: stackTrace,
  );
}

class ValidationException extends AppException {
  final Map<String, List<String>> errors;
  
  const ValidationException({
    required String message,
    required this.errors,
    String? code,
    StackTrace? stackTrace,
  }) : super(
    message: message,
    code: code ?? 'VALIDATION_ERROR',
    details: errors,
    stackTrace: stackTrace,
  );
}
```

### 业务错误类型
```dart
class BusinessException extends AppException {
  const BusinessException({
    required String message,
    String? code,
    dynamic details,
    StackTrace? stackTrace,
  }) : super(
    message: message,
    code: code ?? 'BUSINESS_ERROR',
    details: details,
    stackTrace: stackTrace,
  );
}

class AuthException extends AppException {
  const AuthException({
    required String message,
    String? code,
    dynamic details,
    StackTrace? stackTrace,
  }) : super(
    message: message,
    code: code ?? 'AUTH_ERROR',
    details: details,
    stackTrace: stackTrace,
  );
}
```

## 错误处理

### 全局错误处理
```dart
class ErrorHandler {
  static final _instance = ErrorHandler._();
  factory ErrorHandler() => _instance;
  ErrorHandler._();
  
  void initialize() {
    FlutterError.onError = _handleFlutterError;
    PlatformDispatcher.instance.onError = _handlePlatformError;
    
    runZonedGuarded(
      () => runApp(const MyApp()),
      _handleZoneError,
    );
  }
  
  void _handleFlutterError(FlutterErrorDetails details) {
    log.error(
      'Flutter Error',
      error: details.exception,
      stackTrace: details.stack,
    );
    
    _reportError(
      details.exception,
      details.stack,
      errorType: 'Flutter Error',
    );
  }
  
  bool _handlePlatformError(Object error, StackTrace stack) {
    log.error(
      'Platform Error',
      error: error,
      stackTrace: stack,
    );
    
    _reportError(
      error,
      stack,
      errorType: 'Platform Error',
    );
    
    return true; // 错误已处理
  }
  
  void _handleZoneError(Object error, StackTrace stack) {
    log.error(
      'Zone Error',
      error: error,
      stackTrace: stack,
    );
    
    _reportError(
      error,
      stack,
      errorType: 'Zone Error',
    );
  }
  
  Future<void> _reportError(
    Object error,
    StackTrace? stack, {
    String? errorType,
  }) async {
    // 发送到错误追踪服务
    await Sentry.captureException(
      error,
      stackTrace: stack,
      hint: Hint.withMap({
        'error_type': errorType,
      }),
    );
    
    // 本地存储错误日志
    await ErrorLogger.logError(
      error,
      stack,
      type: errorType,
    );
  }
}
```

### 错误恢复
```dart
class ErrorRecovery {
  static Future<T> retry<T>({
    required Future<T> Function() operation,
    int maxAttempts = 3,
    Duration delay = const Duration(seconds: 1),
    bool Function(Exception)? shouldRetry,
  }) async {
    int attempts = 0;
    
    while (true) {
      try {
        attempts++;
        return await operation();
      } on Exception catch (e) {
        if (attempts >= maxAttempts ||
            (shouldRetry != null && !shouldRetry(e))) {
          rethrow;
        }
        
        await Future.delayed(delay * attempts);
      }
    }
  }
  
  static Future<T> withFallback<T>({
    required Future<T> Function() primary,
    required Future<T> Function() fallback,
    bool Function(Exception)? shouldUseFallback,
  }) async {
    try {
      return await primary();
    } on Exception catch (e) {
      if (shouldUseFallback != null && !shouldUseFallback(e)) {
        rethrow;
      }
      return await fallback();
    }
  }
}
```

## 错误展示

### 错误提示组件
```dart
class ErrorDisplay extends StatelessWidget {
  final AppException error;
  final VoidCallback? onRetry;
  
  const ErrorDisplay({
    Key? key,
    required this.error,
    this.onRetry,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _getErrorIcon(),
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              _getErrorMessage(),
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('重试'),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  IconData _getErrorIcon() {
    if (error is NetworkException) {
      return Icons.cloud_off;
    } else if (error is AuthException) {
      return Icons.lock;
    } else if (error is ValidationException) {
      return Icons.error_outline;
    } else {
      return Icons.warning;
    }
  }
  
  String _getErrorMessage() {
    if (error is NetworkException) {
      return '网络连接失败，请检查网络设置后重试';
    } else if (error is AuthException) {
      return '认证失败，请重新登录';
    } else if (error is ValidationException) {
      return '输入有误，请检查后重试';
    } else {
      return error.message;
    }
  }
}
```

### 错误对话框
```dart
class ErrorDialog extends StatelessWidget {
  final AppException error;
  final VoidCallback? onRetry;
  final VoidCallback? onClose;
  
  const ErrorDialog({
    Key? key,
    required this.error,
    this.onRetry,
    this.onClose,
  }) : super(key: key);
  
  static Future<void> show(
    BuildContext context,
    AppException error, {
    VoidCallback? onRetry,
    VoidCallback? onClose,
  }) {
    return showDialog(
      context: context,
      builder: (context) => ErrorDialog(
        error: error,
        onRetry: onRetry,
        onClose: onClose,
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(
            _getErrorIcon(),
            color: Theme.of(context).colorScheme.error,
          ),
          const SizedBox(width: 8),
          const Text('错误'),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(_getErrorMessage()),
          if (error.details != null) ...[
            const SizedBox(height: 8),
            Text(
              error.details.toString(),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ],
      ),
      actions: [
        if (onRetry != null)
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              onRetry?.call();
            },
            child: const Text('重试'),
          ),
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
            onClose?.call();
          },
          child: const Text('关闭'),
        ),
      ],
    );
  }
  
  IconData _getErrorIcon() {
    // 同上
  }
  
  String _getErrorMessage() {
    // 同上
  }
}
``` 