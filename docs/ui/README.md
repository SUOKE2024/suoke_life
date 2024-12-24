# UI 设计规范

## 设计原则

### 1. 简洁性
- 减少视觉干扰
- 突出重要信息
- 清晰的视觉层次

### 2. 一致性
- 统一的设计语言
- 一致的交互模式
- 标准化的组件

### 3. 易用性
- 直观的操作
- 清晰的反馈
- 容错设计

## 颜色系统

### 主色
```dart
static const Color primary = Color(0xFF2196F3);
static const Color primaryDark = Color(0xFF1976D2);
static const Color primaryLight = Color(0xFF64B5F6);
```

### 辅助色
```dart
static const Color secondary = Color(0xFF4CAF50);
static const Color accent = Color(0xFFFFC107);
static const Color error = Color(0xFFF44336);
```

### 中性色
```dart
static const Color background = Color(0xFFF5F5F5);
static const Color surface = Color(0xFFFFFFFF);
static const Color divider = Color(0xFFE0E0E0);
```

## 字体规范

### 字体家族
```dart
static const String fontFamily = 'PingFang SC';
```

### 字号定义
```dart
static const double fontSizeXS = 12.0;
static const double fontSizeS = 14.0;
static const double fontSizeM = 16.0;
static const double fontSizeL = 18.0;
static const double fontSizeXL = 20.0;
```

### 字重定义
```dart
static const FontWeight light = FontWeight.w300;
static const FontWeight regular = FontWeight.w400;
static const FontWeight medium = FontWeight.w500;
static const FontWeight semibold = FontWeight.w600;
static const FontWeight bold = FontWeight.w700;
```

## 间距规范

### 基础间距
```dart
static const double spaceXS = 4.0;
static const double spaceS = 8.0;
static const double spaceM = 16.0;
static const double spaceL = 24.0;
static const double spaceXL = 32.0;
```

### 内边距
```dart
static const EdgeInsets paddingXS = EdgeInsets.all(4.0);
static const EdgeInsets paddingS = EdgeInsets.all(8.0);
static const EdgeInsets paddingM = EdgeInsets.all(16.0);
static const EdgeInsets paddingL = EdgeInsets.all(24.0);
```

## 组件规范

### 按钮
```dart
class AppButton extends StatelessWidget {
  final double height = 44.0;
  final double borderRadius = 8.0;
  final EdgeInsets padding = EdgeInsets.symmetric(horizontal: 16.0);
}
```

### 输入框
```dart
class AppInput extends StatelessWidget {
  final double height = 48.0;
  final double borderRadius = 8.0;
  final EdgeInsets contentPadding = EdgeInsets.symmetric(horizontal: 16.0);
}
```

### 卡片
```dart
class AppCard extends StatelessWidget {
  final double elevation = 2.0;
  final double borderRadius = 12.0;
  final EdgeInsets padding = EdgeInsets.all(16.0);
}
```

## 响应式设计

### 断点定义
```dart
static const double breakpointMobile = 600.0;
static const double breakpointTablet = 960.0;
static const double breakpointDesktop = 1280.0;
```

### 布局网格
```dart
static const int gridColumns = 12;
static const double gridMargin = 16.0;
static const double gridGutter = 16.0;
```

## 动画规范

### 时长定义
```dart
static const Duration durationFast = Duration(milliseconds: 200);
static const Duration durationNormal = Duration(milliseconds: 300);
static const Duration durationSlow = Duration(milliseconds: 400);
```

### 曲线定义
```dart
static const Curve curveStandard = Curves.easeInOut;
static const Curve curveAccelerate = Curves.easeIn;
static const Curve curveDecelerate = Curves.easeOut;
```

## 图标规范

### 尺寸定义
```dart
static const double iconSizeXS = 16.0;
static const double iconSizeS = 20.0;
static const double iconSizeM = 24.0;
static const double iconSizeL = 32.0;
static const double iconSizeXL = 40.0;
```

### 图标颜色
```dart
static const Color iconPrimary = Color(0xFF333333);
static const Color iconSecondary = Color(0xFF666666);
static const Color iconDisabled = Color(0xFFCCCCCC);
```

## 主题配置

### 亮色主题
```dart
static final ThemeData light = ThemeData(
  primaryColor: AppColors.primary,
  backgroundColor: AppColors.background,
  scaffoldBackgroundColor: AppColors.background,
  appBarTheme: AppBarTheme(
    elevation: 0,
    backgroundColor: AppColors.primary,
  ),
);
```

### 暗色主题
```dart
static final ThemeData dark = ThemeData.dark().copyWith(
  primaryColor: AppColors.primaryDark,
  backgroundColor: Color(0xFF121212),
  scaffoldBackgroundColor: Color(0xFF121212),
);
``` 