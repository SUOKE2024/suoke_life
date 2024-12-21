import 'package:flutter/material.dart';

class AppTheme {
  // Light Theme
  static final ThemeData light = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.light,
    ),
    appBarTheme: const AppBarTheme(
      centerTitle: true,
      elevation: 0,
      scrolledUnderElevation: 2,
    ),
    cardTheme: CardTheme(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 12,
      ),
      filled: true,
    ),
    chipTheme: ChipThemeData(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      padding: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 4,
      ),
    ),
    navigationBarTheme: NavigationBarThemeData(
      elevation: 4,
      labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      height: 72,
      indicatorShape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  );

  // Dark Theme  
  static final ThemeData dark = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.dark,
    ),
    // 继承 light 主题的其他配置
    appBarTheme: light.appBarTheme,
    cardTheme: light.cardTheme,
    inputDecorationTheme: light.inputDecorationTheme.copyWith(
      fillColor: Colors.grey[800],
    ),
    chipTheme: light.chipTheme,
    navigationBarTheme: light.navigationBarTheme,
  );
} 