import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'logger.dart';

/// Provider容器观察器
///
/// 用于记录Provider状态变化，方便调试
class ProviderContainerObserver extends ProviderObserver {
  @override
  void didAddProvider(
    ProviderBase provider,
    Object? value,
    ProviderContainer container,
  ) {
    if (provider.name != null) {
      logger.d('Provider添加: ${provider.name}');
    }
  }

  @override
  void didUpdateProvider(
    ProviderBase provider,
    Object? previousValue,
    Object? newValue,
    ProviderContainer container,
  ) {
    if (provider.name != null) {
      logger.d('Provider更新: ${provider.name}');
    }
  }

  @override
  void didDisposeProvider(
    ProviderBase provider,
    ProviderContainer container,
  ) {
    if (provider.name != null) {
      logger.d('Provider释放: ${provider.name}');
    }
  }
} 