import 'package:flutter/material.dart';

/// 索克生活APP色彩系统
/// 定义了品牌色、功能色和中性色等设计令牌
class AppColors {
  AppColors._();

  // 品牌主色
  static const Color primaryColor = Color(0xFF35BB78); // 索克绿
  static const Color secondaryColor = Color(0xFFFF6800); // 索克橙
  static const Color tertiaryColor = Color(0xFF5B5BD0); // 第三色调

  // 主色调衍生色
  static const Color primaryLight = Color(0xFF7DDAA6); // 浅索克绿
  static const Color primaryDark = Color(0xFF219A59); // 深索克绿
  static const Color primaryBg = Color(0xFFE8F7EF); // 索克绿背景色

  // 辅色调衍生色
  static const Color secondaryLight = Color(0xFFFF9248); // 浅索克橙
  static const Color secondaryDark = Color(0xFFD14800); // 深索克橙
  static const Color secondaryBg = Color(0xFFFFF1E6); // 索克橙背景色

  // 五行色系 - 用于中医特色元素
  static const Color woodColor = Color(0xFF8BC34A); // 木 - 青绿
  static const Color fireColor = Color(0xFFFF5252); // 火 - 赤红
  static const Color earthColor = Color(0xFFFFB300); // 土 - 黄褐
  static const Color metalColor = Color(0xFFB0BEC5); // 金 - 白灰
  static const Color waterColor = Color(0xFF42A5F5); // 水 - 青蓝

  // 特殊颜色
  static const Color goldColor = Color(0xFFFFD700); // 金色

  // 功能色
  static const Color successColor = Color(0xFF4CAF50); // 成功
  static const Color errorColor = Color(0xFFD32F2F); // 错误
  static const Color warningColor = Color(0xFFFFC107); // 警告
  static const Color infoColor = Color(0xFF4FC3F7); // 信息

  // 中性色调 - 亮色主题
  static const Color lightBackground = Color(0xFFF5F5F5); // 背景
  static const Color lightSurface = Color(0xFFFFFFFF); // 表面
  static const Color lightTextPrimary = Color(0xFF212121); // 主要文本
  static const Color lightTextSecondary = Color(0xFF757575); // 次要文本
  static const Color lightBorder = Color(0xFFE0E0E0); // 边框
  static const Color lightDivider = Color(0xFFEEEEEE); // 分割线

  // 中性色调 - 暗色主题
  static const Color darkBackground = Color(0xFF121212); // 背景
  static const Color darkSurface = Color(0xFF1E1E1E); // 表面
  static const Color darkTextPrimary = Color(0xFFE0E0E0); // 主要文本
  static const Color darkTextSecondary = Color(0xFFB3B3B3); // 次要文本
  static const Color darkBorder = Color(0xFF424242); // 边框
  static const Color darkDivider = Color(0xFF353535); // 分割线

  // 系统状态栏颜色
  static const Color darkSystemGray = Color(0xFF8E8E93); // 暗色系统灰
  static const Color lightSystemGray = Color(0xFF8E8E93); // 亮色系统灰

  // 亮色主题iOS特有颜色
  static const Color lightBackgroundSecondary = Color(0xFFE5E5EA); // 次要背景色
  static const Color lightBackgroundTertiary = Color(0xFFFFFFFF); // 三级背景色
  static const Color lightSystemGray2 = Color(0xFFAEAEB2); // 系统灰色2
  static const Color lightSystemGray3 = Color(0xFFC7C7CC); // 系统灰色3
  static const Color lightSystemGray4 = Color(0xFFD1D1D6); // 系统灰色4
  static const Color lightSystemGray5 = Color(0xFFE5E5EA); // 系统灰色5
  static const Color lightSystemGray6 = Color(0xFFF2F2F7); // 系统灰色6
  static const Color lightInputBackground = Color(0xFFE9E9EB); // 输入框背景色

  // 暗色主题iOS特有颜色
  static const Color darkBackgroundSecondary = Color(0xFF2C2C2E); // 次要背景色
  static const Color darkBackgroundTertiary = Color(0xFF3A3A3C); // 三级背景色
  static const Color darkSystemGray2 = Color(0xFF636366); // 系统灰色2
  static const Color darkSystemGray3 = Color(0xFF48484A); // 系统灰色3
  static const Color darkSystemGray4 = Color(0xFF3A3A3C); // 系统灰色4
  static const Color darkSystemGray5 = Color(0xFF2C2C2E); // 系统灰色5
  static const Color darkSystemGray6 = Color(0xFF1C1C1E); // 系统灰色6
  static const Color darkInputBackground = Color(0xFF2C2C2E); // 输入框背景色

  // 模糊效果专用颜色
  static const Color lightBlurTint = Color(0xF0FFFFFF); // 亮色模糊背景色
  static const Color darkBlurTint = Color(0xA01C1C1E); // 暗色模糊背景色

  // iOS磨砂玻璃标准颜色
  static const Color iosBlurLight = Color(0x60FFFFFF); // 亮色磨砂玻璃
  static const Color iosBlurDark = Color(0x602C2C2E); // 暗色磨砂玻璃
  static const Color iosBlurExtraLight = Color(0x80FFFFFF); // 超亮磨砂玻璃
  static const Color iosBlurUltraDark = Color(0x801C1C1E); // 超暗磨砂玻璃

  // iOS标准边框颜色
  static const Color iosBorderLight = Color(0x33000000); // 亮模式下的边框
  static const Color iosBorderDark = Color(0x33FFFFFF); // 暗模式下的边框

  // 获取当前主题适配的颜色
  static Color getAdaptiveColor({
    required BuildContext context,
    required Color lightModeColor,
    required Color darkModeColor,
  }) {
    final brightness = Theme.of(context).brightness;
    return brightness == Brightness.light ? lightModeColor : darkModeColor;
  }

  // 透明度辅助函数
  static Color withAlphaValue(Color color, double opacity) {
    // 根据规范，使用withAlpha替代withOpacity
    return color.withAlpha((opacity * 255).toInt());
  }

  // 获取磨砂背景颜色 (基于当前主题)
  static Color getBlurTintColor(bool isDarkMode) {
    return isDarkMode ? darkBlurTint : lightBlurTint;
  }

  // 获取苹果风格边框颜色 (基于当前主题)
  static Color getBorderColor(bool isDarkMode) {
    return isDarkMode ? iosBorderDark : iosBorderLight;
  }

  // 获取磨砂玻璃颜色 (基于当前主题)
  static Color getBlurColor(bool isDarkMode, {bool extraEffect = false}) {
    if (isDarkMode) {
      return extraEffect ? iosBlurUltraDark : iosBlurDark;
    } else {
      return extraEffect ? iosBlurExtraLight : iosBlurLight;
    }
  }
}
