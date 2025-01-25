/// 应用样式
abstract class AppStyles {
  // 系统UI样式
  static const lightOverlayStyle = SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
    systemNavigationBarColor: AppColors.background,
    systemNavigationBarIconBrightness: Brightness.dark,
  );

  static const darkOverlayStyle = SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: AppColors.backgroundDark,
    systemNavigationBarIconBrightness: Brightness.light,
  );

  // 边距
  static const padding = EdgeInsets.all(16);
  static const paddingSmall = EdgeInsets.all(8);
  static const paddingLarge = EdgeInsets.all(24);

  // 圆角
  static final borderRadius = BorderRadius.circular(8);
  static final borderRadiusLarge = BorderRadius.circular(16);

  // 阴影
  static const elevation = 2.0;
  static const elevationLarge = 4.0;
} 