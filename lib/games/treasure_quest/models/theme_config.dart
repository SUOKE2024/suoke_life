import 'package:flutter/material.dart';

class ThemeConfig {
  final double borderRadius;
  final double elevation;
  final double spacing;
  final double iconSize;
  final double fontSize;
  final bool isDense;
  final bool useShadows;
  final bool useGradients;
  final bool useAnimations;
  final ColorScheme? customColorScheme;
  final TextTheme? customTextTheme;

  const ThemeConfig({
    this.borderRadius = 12.0,
    this.elevation = 2.0,
    this.spacing = 16.0,
    this.iconSize = 24.0,
    this.fontSize = 14.0,
    this.isDense = false,
    this.useShadows = true,
    this.useGradients = false,
    this.useAnimations = true,
    this.customColorScheme,
    this.customTextTheme,
  });

  // 从JSON创建实例
  factory ThemeConfig.fromJson(Map<String, dynamic> json) {
    return ThemeConfig(
      borderRadius: json['border_radius']?.toDouble() ?? 12.0,
      elevation: json['elevation']?.toDouble() ?? 2.0,
      spacing: json['spacing']?.toDouble() ?? 16.0,
      iconSize: json['icon_size']?.toDouble() ?? 24.0,
      fontSize: json['font_size']?.toDouble() ?? 14.0,
      isDense: json['is_dense'] ?? false,
      useShadows: json['use_shadows'] ?? true,
      useGradients: json['use_gradients'] ?? false,
      useAnimations: json['use_animations'] ?? true,
    );
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'border_radius': borderRadius,
      'elevation': elevation,
      'spacing': spacing,
      'icon_size': iconSize,
      'font_size': fontSize,
      'is_dense': isDense,
      'use_shadows': useShadows,
      'use_gradients': useGradients,
      'use_animations': useAnimations,
    };
  }

  // 复制实例并修改部分属性
  ThemeConfig copyWith({
    double? borderRadius,
    double? elevation,
    double? spacing,
    double? iconSize,
    double? fontSize,
    bool? isDense,
    bool? useShadows,
    bool? useGradients,
    bool? useAnimations,
    ColorScheme? customColorScheme,
    TextTheme? customTextTheme,
  }) {
    return ThemeConfig(
      borderRadius: borderRadius ?? this.borderRadius,
      elevation: elevation ?? this.elevation,
      spacing: spacing ?? this.spacing,
      iconSize: iconSize ?? this.iconSize,
      fontSize: fontSize ?? this.fontSize,
      isDense: isDense ?? this.isDense,
      useShadows: useShadows ?? this.useShadows,
      useGradients: useGradients ?? this.useGradients,
      useAnimations: useAnimations ?? this.useAnimations,
      customColorScheme: customColorScheme ?? this.customColorScheme,
      customTextTheme: customTextTheme ?? this.customTextTheme,
    );
  }

  // 获取主题数据
  ThemeData getThemeData({
    required bool isDark,
    required Color primaryColor,
    required bool useMaterial3,
  }) {
    final baseTheme = ThemeData(
      useMaterial3: useMaterial3,
      brightness: isDark ? Brightness.dark : Brightness.light,
      colorScheme: customColorScheme ??
          ColorScheme.fromSeed(
            seedColor: primaryColor,
            brightness: isDark ? Brightness.dark : Brightness.light,
          ),
    );

    return baseTheme.copyWith(
      textTheme: customTextTheme ?? _getAdjustedTextTheme(baseTheme.textTheme),
      cardTheme: CardTheme(
        elevation: useShadows ? elevation : 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: useShadows ? elevation : 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadius),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadius),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        isDense: isDense,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
      iconTheme: IconThemeData(
        size: iconSize,
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(borderRadius / 2),
        ),
      ),
      dialogTheme: DialogTheme(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
      bottomSheetTheme: BottomSheetThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(borderRadius),
          ),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        elevation: useShadows ? elevation : 0,
        labelBehavior: isDense
            ? NavigationDestinationLabelBehavior.onlyShowSelected
            : NavigationDestinationLabelBehavior.alwaysShow,
      ),
      listTileTheme: ListTileThemeData(
        dense: isDense,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
    );
  }

  // 调整文本主题
  TextTheme _getAdjustedTextTheme(TextTheme base) {
    return base.copyWith(
      displayLarge: base.displayLarge?.copyWith(fontSize: fontSize * 3),
      displayMedium: base.displayMedium?.copyWith(fontSize: fontSize * 2.5),
      displaySmall: base.displaySmall?.copyWith(fontSize: fontSize * 2),
      headlineLarge: base.headlineLarge?.copyWith(fontSize: fontSize * 1.8),
      headlineMedium: base.headlineMedium?.copyWith(fontSize: fontSize * 1.6),
      headlineSmall: base.headlineSmall?.copyWith(fontSize: fontSize * 1.4),
      titleLarge: base.titleLarge?.copyWith(fontSize: fontSize * 1.3),
      titleMedium: base.titleMedium?.copyWith(fontSize: fontSize * 1.2),
      titleSmall: base.titleSmall?.copyWith(fontSize: fontSize * 1.1),
      bodyLarge: base.bodyLarge?.copyWith(fontSize: fontSize * 1.1),
      bodyMedium: base.bodyMedium?.copyWith(fontSize: fontSize),
      bodySmall: base.bodySmall?.copyWith(fontSize: fontSize * 0.9),
      labelLarge: base.labelLarge?.copyWith(fontSize: fontSize),
      labelMedium: base.labelMedium?.copyWith(fontSize: fontSize * 0.9),
      labelSmall: base.labelSmall?.copyWith(fontSize: fontSize * 0.8),
    );
  }
} 