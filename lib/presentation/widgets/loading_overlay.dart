import 'package:flutter/material.dart';

/// 加载覆盖组件
class LoadingOverlay extends StatelessWidget {
  /// 加载消息
  final String message;
  
  /// 背景颜色
  final Color backgroundColor;
  
  /// 文字颜色
  final Color textColor;
  
  /// 构造函数
  const LoadingOverlay({
    super.key,
    required this.message,
    this.backgroundColor = Colors.black54,
    this.textColor = Colors.white,
  });
  
  @override
  Widget build(BuildContext context) {
    return Positioned.fill(
      child: Container(
        color: backgroundColor,
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
              const SizedBox(height: 16),
              Text(
                message,
                style: TextStyle(
                  color: textColor,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
} 