import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../network/api_health_service.dart';

/// API连接状态组件
///
/// 显示API服务的连接状态，并在连接不可用时提供重试选项
class ApiConnectionStatus extends ConsumerWidget {
  /// 构造函数
  const ApiConnectionStatus({
    super.key,
    this.onRetry,
    this.compact = false,
  });
  
  /// 重试回调
  final VoidCallback? onRetry;
  
  /// 是否使用紧凑模式
  final bool compact;
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final apiHealth = ref.watch(apiHealthStatusProvider);
    
    return apiHealth.when(
      data: (isHealthy) {
        if (isHealthy) {
          return const SizedBox.shrink(); // 如果健康，不显示任何内容
        }
        
        // 如果不健康，显示警告
        return _buildUnhealthyWidget(context);
      },
      loading: () => _buildLoadingWidget(),
      error: (error, stackTrace) => _buildErrorWidget(context, error),
    );
  }
  
  /// 构建健康检查中的Widget
  Widget _buildLoadingWidget() {
    if (compact) {
      return const SizedBox(
        height: 2,
        child: LinearProgressIndicator(),
      );
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      color: Colors.blue.withAlpha(50),
      child: const Center(
        child: Text(
          '正在检查API服务状态...',
          style: TextStyle(color: Colors.blue),
        ),
      ),
    );
  }
  
  /// 构建不健康的Widget
  Widget _buildUnhealthyWidget(BuildContext context) {
    if (compact) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
        color: Colors.red.withAlpha(50),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, color: Colors.red, size: 16),
            const SizedBox(width: 4),
            const Text('服务连接异常', style: TextStyle(color: Colors.red, fontSize: 12)),
            if (onRetry != null) ...[
              const SizedBox(width: 8),
              TextButton(
                onPressed: onRetry,
                style: TextButton.styleFrom(
                  minimumSize: const Size(40, 20),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                ),
                child: const Text('重试', style: TextStyle(fontSize: 12)),
              ),
            ],
          ],
        ),
      );
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      color: Colors.red.withAlpha(50),
      child: Row(
        children: [
          const Icon(Icons.cloud_off, color: Colors.red),
          const SizedBox(width: 16),
          const Expanded(
            child: Text(
              'API服务连接异常，请检查网络连接或联系客服',
              style: TextStyle(color: Colors.red),
            ),
          ),
          if (onRetry != null)
            TextButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
            ),
        ],
      ),
    );
  }
  
  /// 构建错误Widget
  Widget _buildErrorWidget(BuildContext context, Object error) {
    if (compact) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
        color: Colors.orange.withAlpha(50),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.warning, color: Colors.orange, size: 16),
            const SizedBox(width: 4),
            const Text('检查服务状态失败', style: TextStyle(color: Colors.orange, fontSize: 12)),
            if (onRetry != null) ...[
              const SizedBox(width: 8),
              TextButton(
                onPressed: onRetry,
                style: TextButton.styleFrom(
                  minimumSize: const Size(40, 20),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                ),
                child: const Text('重试', style: TextStyle(fontSize: 12)),
              ),
            ],
          ],
        ),
      );
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      color: Colors.orange.withAlpha(50),
      child: Row(
        children: [
          const Icon(Icons.warning, color: Colors.orange),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              '检查API服务状态失败: ${error.toString()}',
              style: const TextStyle(color: Colors.orange),
            ),
          ),
          if (onRetry != null)
            TextButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
            ),
        ],
      ),
    );
  }
} 