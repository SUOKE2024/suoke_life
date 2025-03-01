import 'package:flutter/material.dart';

/// 通用错误视图组件
class ErrorView extends StatelessWidget {
  /// 错误信息
  final String error;
  
  /// 重试回调
  final VoidCallback? onRetry;
  
  /// 自定义图标
  final IconData? icon;
  
  /// 自定义图标颜色
  final Color? iconColor;
  
  /// 自定义图标大小
  final double iconSize;
  
  /// 自定义错误文本样式
  final TextStyle? errorTextStyle;
  
  /// 自定义重试按钮文本
  final String retryText;
  
  const ErrorView({
    Key? key,
    required this.error,
    this.onRetry,
    this.icon = Icons.error_outline,
    this.iconColor,
    this.iconSize = 80,
    this.errorTextStyle,
    this.retryText = '重试',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: iconSize,
              color: iconColor ?? theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              error,
              textAlign: TextAlign.center,
              style: errorTextStyle ?? TextStyle(
                fontSize: 16,
                color: theme.colorScheme.onSurface,
              ),
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: Text(retryText),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
} 