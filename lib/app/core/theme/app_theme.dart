/// 应用主题管理
abstract class AppTheme {
  /// 亮色主题
  static final light = ThemeData.light().copyWith(
    primaryColor: AppColors.primary,
    scaffoldBackgroundColor: AppColors.background,
    appBarTheme: const AppBarTheme(
      elevation: 0,
      centerTitle: true,
      backgroundColor: AppColors.primary,
      foregroundColor: AppColors.onPrimary,
    ),
    cardTheme: CardTheme(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    ),
    buttonTheme: ButtonThemeData(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      buttonColor: AppColors.primary,
    ),
    textTheme: TextTheme(
      headlineLarge: AppTextStyles.headlineLarge,
      headlineMedium: AppTextStyles.headlineMedium,
      bodyLarge: AppTextStyles.bodyLarge,
      bodyMedium: AppTextStyles.bodyMedium,
    ),
  );

  /// 暗色主题
  static final dark = ThemeData.dark().copyWith(
    primaryColor: AppColors.primaryDark,
    scaffoldBackgroundColor: AppColors.backgroundDark,
    // ... 其他暗色主题配置
  );

  /// 初始化主题
  static void init() {
    Get.changeTheme(Get.isDarkMode ? dark : light);
    SystemChrome.setSystemUIOverlayStyle(
      Get.isDarkMode ? AppStyles.darkOverlayStyle : AppStyles.lightOverlayStyle,
    );
  }
} 