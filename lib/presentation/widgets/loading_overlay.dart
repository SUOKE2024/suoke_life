import 'package:flutter/material.dart';

/// 加载覆盖层
/// 在内容上显示半透明加载指示器
class LoadingOverlay extends StatelessWidget {
  final bool isLoading;
  final Widget child;
  final Color? color;
  final double opacity;
  final Widget? loadingWidget;

  const LoadingOverlay({
    Key? key,
    required this.isLoading,
    required this.child,
    this.color,
    this.opacity = 0.5,
    this.loadingWidget,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Stack(
      children: [
        // 内容
        child,
        
        // 加载指示器
        if (isLoading)
          Positioned.fill(
            child: Container(
              color: (color ?? Colors.black).withOpacity(opacity),
              child: Center(
                child: loadingWidget ?? 
                  CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(
                      theme.colorScheme.primary,
                    ),
                  ),
              ),
            ),
          ),
      ],
    );
  }
} 