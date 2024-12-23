import 'package:flutter/material.dart';

class AppColors {
  // 主题色
  static const Color primary = Color(0xFF2196F3);
  static const Color primaryDark = Color(0xFF1976D2);
  static const Color primaryLight = Color(0xFFBBDEFB);
  static const Color accent = Color(0xFFFF4081);

  // 文本颜色
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
  static const Color textHint = Color(0xFFBDBDBD);

  // 背景颜色
  static const Color background = Color(0xFFFFFFFF);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color error = Color(0xFFD32F2F);

  // 聊天气泡颜色
  static const Color userBubble = primary;
  static const Color assistantBubble = Color(0xFFEEEEEE);
  static const Color userText = Colors.white;
  static const Color assistantText = textPrimary;

  // 分割线颜色
  static const Color divider = Color(0xFFE0E0E0);

  // 图标颜色
  static const Color icon = Color(0xFF757575);
  static const Color iconActive = primary;

  // 状态颜色
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFFC107);
  static const Color info = Color(0xFF2196F3);

  // 渐变色
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, primaryDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
} 