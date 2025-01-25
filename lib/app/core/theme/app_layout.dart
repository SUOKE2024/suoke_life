import 'package:flutter/material.dart';

class AppLayout {
  // 页面边距
  static const EdgeInsets pagePadding = EdgeInsets.all(16.0);
  static const EdgeInsets cardPadding = EdgeInsets.all(12.0);
  
  // 间距
  static const double spaceXS = 4.0;
  static const double spaceS = 8.0;
  static const double spaceM = 16.0;
  static const double spaceL = 24.0;
  static const double spaceXL = 32.0;

  // 圆角
  static const double radiusS = 4.0;
  static const double radiusM = 8.0;
  static const double radiusL = 16.0;

  // 卡片尺寸
  static const Size cardSize = Size(double.infinity, 120);
  static const Size serviceCardSize = Size(160, 180);
  static const Size avatarSize = Size(48, 48);

  // 动画时长
  static const Duration animFast = Duration(milliseconds: 200);
  static const Duration animNormal = Duration(milliseconds: 300);
  static const Duration animSlow = Duration(milliseconds: 400);

  // 响应式布局断点
  static const double breakpointMobile = 600;
  static const double breakpointTablet = 900;
  static const double breakpointDesktop = 1200;

  // 获取响应式列数
  static int getResponsiveColumns(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    if (width < breakpointMobile) return 1;
    if (width < breakpointTablet) return 2;
    if (width < breakpointDesktop) return 3;
    return 4;
  }
} 