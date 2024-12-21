import 'package:flutter/material.dart';

/// 错误状态组件
class AppError extends StatelessWidget {
  final String? message;
  final VoidCallback? onRetry;
  
  const AppError({
    super.key,
    this.message,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (message != null) ...[
              const SizedBox(height: 8),
              Text(
                message!,
                textAlign: TextAlign.center,
              ),
            ],
            if (onRetry != null) ...[
              const SizedBox(height: 24),
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
}

/// 错误边界组件
class AppErrorBoundary extends StatefulWidget {
  final Widget child;
  final Widget Function(BuildContext, Object?)? errorBuilder;
  
  const AppErrorBoundary({
    super.key,
    required this.child,
    this.errorBuilder,
  });

  @override
  State<AppErrorBoundary> createState() => _AppErrorBoundaryState();
}

class _AppErrorBoundaryState extends State<AppErrorBoundary> {
  Object? _error;

  @override
  void initState() {
    super.initState();
    _error = null;
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return widget.errorBuilder?.call(context, _error) ?? AppError(
        message: _error.toString(),
        onRetry: () => setState(() => _error = null),
      );
    }

    return ErrorWidget.builder = (details) {
      setState(() => _error = details.exception);
      return const SizedBox();
    };
  }
} 