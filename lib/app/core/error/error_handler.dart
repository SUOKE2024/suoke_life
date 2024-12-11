/// 统一错误处理器
class ErrorHandler {
  static final instance = ErrorHandler._();
  ErrorHandler._();

  /// 错误处理策略
  final _strategies = <Type, ErrorStrategy>{};
  
  /// 默认错误处理策略
  late final ErrorStrategy _defaultStrategy;

  /// 初始化错误处理器
  void initialize() {
    // 注册默认策略
    _defaultStrategy = DefaultErrorStrategy();

    // 注册内置策略
    registerStrategy<NetworkException>(NetworkErrorStrategy());
    registerStrategy<StorageException>(StorageErrorStrategy());
    registerStrategy<ServiceException>(ServiceErrorStrategy());
    registerStrategy<ValidationException>(ValidationErrorStrategy());
  }

  /// 注册错误处理策略
  void registerStrategy<T extends Exception>(ErrorStrategy strategy) {
    _strategies[T] = strategy;
  }

  /// 处理错误
  void handleError(dynamic error) {
    try {
      // 获取对应的处理策略
      final strategy = _getStrategy(error);
      
      // 执行错误处理
      strategy.handleError(error);
      
      // 记录错误日志
      LoggerService.error(
        'Error handled by ${strategy.runtimeType}',
        error: error,
      );
    } catch (e) {
      // 处理错误时发生异常
      LoggerService.error(
        'Error handler failed',
        error: e,
      );
    }
  }

  /// 获取错误消息
  String getErrorMessage(dynamic error) {
    final strategy = _getStrategy(error);
    return strategy.getErrorMessage(error);
  }

  /// 获取错误处理策略
  ErrorStrategy _getStrategy(dynamic error) {
    if (error is Exception) {
      return _strategies[error.runtimeType] ?? _defaultStrategy;
    }
    return _defaultStrategy;
  }

  /// 重置错误处理器
  void reset() {
    _strategies.clear();
    initialize();
  }
}

/// 错误处理策略接口
abstract class ErrorStrategy {
  /// 处理错误
  void handleError(dynamic error);
  
  /// 获取错误消息
  String getErrorMessage(dynamic error);
}

/// 默认错误处理策略
class DefaultErrorStrategy implements ErrorStrategy {
  @override
  void handleError(dynamic error) {
    // 默认错误处理逻辑
  }

  @override
  String getErrorMessage(dynamic error) {
    return error?.toString() ?? '未知错误';
  }
}

/// 网络错误处理策略
class NetworkErrorStrategy implements ErrorStrategy {
  @override
  void handleError(dynamic error) {
    if (error is NetworkException) {
      // 处理网络错误
      // 例如：重试、刷新token等
    }
  }

  @override
  String getErrorMessage(dynamic error) {
    if (error is NetworkException) {
      switch (error.type) {
        case NetworkErrorType.noConnection:
          return '网络连接失败';
        case NetworkErrorType.timeout:
          return '网络请求超时';
        case NetworkErrorType.serverError:
          return '服务器错误';
        default:
          return '网络错误';
      }
    }
    return '网络错误';
  }
}

/// 存储错误处理策略
class StorageErrorStrategy implements ErrorStrategy {
  @override
  void handleError(dynamic error) {
    if (error is StorageException) {
      // 处理存储错误
      // 例如：清理缓存、重试等
    }
  }

  @override
  String getErrorMessage(dynamic error) {
    if (error is StorageException) {
      return '存储操作失败';
    }
    return '存储错误';
  }
}

/// 服务错误处理策略
class ServiceErrorStrategy implements ErrorStrategy {
  @override
  void handleError(dynamic error) {
    if (error is ServiceException) {
      // 处理服务错误
      // 例如：重新初始化服务等
    }
  }

  @override
  String getErrorMessage(dynamic error) {
    if (error is ServiceException) {
      return '服务操作失败';
    }
    return '服务错误';
  }
}

/// 验证错误处理策略
class ValidationErrorStrategy implements ErrorStrategy {
  @override
  void handleError(dynamic error) {
    if (error is ValidationException) {
      // 处理验证错误
      // 例如：显示表单错误等
    }
  }

  @override
  String getErrorMessage(dynamic error) {
    if (error is ValidationException) {
      return error.message;
    }
    return '验证错误';
  }
} 