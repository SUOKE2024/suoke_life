import 'package:flutter/material.dart';

/// 加载组件
class AppLoading extends StatelessWidget {
  final String? message;
  final Widget? indicator;
  final bool overlay; // 是否显示遮罩
  final Color? color;
  final double size;
  final double strokeWidth;
  final EdgeInsets padding;
  
  const AppLoading({
    super.key,
    this.message,
    this.indicator,
    this.overlay = false,
    this.color,
    this.size = 36,
    this.strokeWidth = 4,
    this.padding = const EdgeInsets.all(16),
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: padding,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: size,
              height: size,
              child: CircularProgressIndicator(
                strokeWidth: strokeWidth,
                valueColor: color != null 
                    ? AlwaysStoppedAnimation(color)
                    : null,
              ),
            ),
            if (message != null) ...[
              const SizedBox(height: 16),
              Text(
                message!,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// 显示全屏加载
  static Future<T?> show<T>({
    required BuildContext context,
    String? message,
    Color? color,
    bool barrierDismissible = false,
  }) {
    return showDialog<T>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => AppLoading(
        message: message,
        color: color,
      ),
    );
  }
}

/// 加载状态包装组件
class AppLoadingWrapper extends StatelessWidget {
  final bool loading;
  final Widget child;
  final String? message;
  final Color? color;
  
  const AppLoadingWrapper({
    super.key,
    required this.loading,
    required this.child,
    this.message,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (loading)
          Container(
            color: Colors.black26,
            child: AppLoading(
              message: message,
              color: color,
            ),
          ),
      ],
    );
  }
} 