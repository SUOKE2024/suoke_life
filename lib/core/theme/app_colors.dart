import 'package:flutter/material.dart';

/// 应用颜色主题
class AppColors {
  /// 主色调
  static const Color primary = Color(0xFF35BB78); // 索克绿
  
  /// 次要色调
  static const Color secondary = Color(0xFF2A6CBE); // 深蓝色
  
  /// 强调色
  static const Color accent = Color(0xFFFF6800); // 索克橙
  
  /// 背景色
  static const Color background = Color(0xFFF9F9F9);
  
  /// 表面色
  static const Color surface = Colors.white;
  
  /// 错误色
  static const Color error = Color(0xFFE53935);
  
  /// 成功色
  static const Color success = Color(0xFF43A047);
  
  /// 警告色
  static const Color warning = Color(0xFFFFA000);
  
  /// 信息色
  static const Color info = Color(0xFF2196F3);
  
  /// 暗色文本
  static const Color textDark = Color(0xFF212121);
  
  /// 浅色文本
  static const Color textLight = Color(0xFF757575);
  
  /// 最浅色文本
  static const Color textLighter = Color(0xFFBDBDBD);
  
  /// 白色文本
  static const Color textWhite = Colors.white;
  
  /// 分隔线颜色
  static const Color divider = Color(0xFFEEEEEE);
  
  /// 卡片阴影颜色
  static const Color shadow = Color(0x1A000000);
  
  /// 健康数据颜色
  static const Map<String, Color> healthColors = {
    'steps': Color(0xFF4CAF50),
    'sleep': Color(0xFF5C6BC0),
    'heartRate': Color(0xFFE53935),
    'weight': Color(0xFF8D6E63),
    'waterIntake': Color(0xFF29B6F6),
    'bloodPressure': Color(0xFFF44336),
    'temperature': Color(0xFFFF9800),
    'calories': Color(0xFFFF6F00),
  };
  
  /// 知识图谱节点颜色
  static const Map<String, Color> knowledgeNodeColors = {
    '中医理论': Color(0xFFE53935),
    '西医概念': Color(0xFF1E88E5),
    '疾病': Color(0xFF8E24AA),
    '症状': Color(0xFFFF9800),
    '治疗方法': Color(0xFF43A047),
    '药材': Color(0xFF00897B),
    '食材': Color(0xFFFFB300),
    '穴位': Color(0xFF3949AB),
  };
  
  /// 禁止直接实例化
  AppColors._();
} 