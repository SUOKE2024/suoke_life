import 'package:flutter/material.dart';
import 'dart:ui';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/theme/app_shapes.dart';
import 'package:suoke_life/core/theme/app_spacing.dart';

/// 卡片大小枚举
enum AppCardSize {
  /// 小尺寸卡片 - 适用于列表项或紧凑型卡片
  small,

  /// 中等尺寸卡片 - 标准卡片
  medium,

  /// 大尺寸卡片 - 突出显示的卡片
  large
}

/// 卡片风格枚举
enum AppCardStyle {
  /// 标准卡片 - 实色背景
  standard,

  /// 轻量卡片 - 透明度更高
  light,

  /// 磨砂卡片 - 带模糊效果
  frosted,

  /// 轮廓卡片 - 仅带边框
  outline,

  /// 特殊风格卡片 - 带渐变色
  gradient
}

/// 索克风格标准卡片组件
///
/// 统一的卡片组件，支持多种风格和尺寸。
/// 使用示例:
/// ```dart
/// AppCard(
///   title: '标题',
///   content: Text('内容'),
///   style: AppCardStyle.standard,
///   size: AppCardSize.medium,
/// )
/// ```
class AppCard extends StatelessWidget {
  /// 卡片标题
  final String? title;

  /// 卡片子标题
  final String? subtitle;

  /// 卡片内容
  final Widget content;

  /// 卡片尺寸
  final AppCardSize size;

  /// 卡片风格
  final AppCardStyle style;

  /// 卡片高度
  final double? height;

  /// 卡片宽度
  final double? width;

  /// 前导图标
  final IconData? leadingIcon;

  /// 尾随图标
  final IconData? trailingIcon;

  /// 尾随操作按钮
  final Widget? trailingAction;

  /// 自定义背景色
  final Color? backgroundColor;

  /// 自定义边框色
  final Color? borderColor;

  /// 自定义渐变色 (用于渐变风格)
  final LinearGradient? gradient;

  /// 点击回调
  final VoidCallback? onTap;

  /// 长按回调
  final VoidCallback? onLongPress;

  /// 是否显示边框
  final bool showBorder;

  /// 是否有阴影
  final bool hasShadow;

  /// 自定义内边距
  final EdgeInsetsGeometry? padding;

  /// 自定义外边距
  final EdgeInsetsGeometry? margin;

  const AppCard({
    super.key,
    this.title,
    this.subtitle,
    required this.content,
    this.size = AppCardSize.medium,
    this.style = AppCardStyle.standard,
    this.height,
    this.width,
    this.leadingIcon,
    this.trailingIcon,
    this.trailingAction,
    this.backgroundColor,
    this.borderColor,
    this.gradient,
    this.onTap,
    this.onLongPress,
    this.showBorder = false,
    this.hasShadow = true,
    this.padding,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    // 构建卡片内容
    Widget cardContent = _buildCardContent(context, isDarkMode);

    // 应用磨砂玻璃效果 (如果风格是frosted)
    if (style == AppCardStyle.frosted) {
      cardContent = ClipRRect(
        borderRadius: BorderRadius.circular(AppShapes.radiusLG),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: cardContent,
        ),
      );
    }

    // 应用卡片点击效果
    if (onTap != null || onLongPress != null) {
      cardContent = InkWell(
        onTap: onTap,
        onLongPress: onLongPress,
        borderRadius: BorderRadius.circular(AppShapes.radiusLG),
        child: cardContent,
      );
    }

    // 添加阴影
    if (hasShadow) {
      return Container(
        height: height,
        width: width,
        margin: margin ?? EdgeInsets.all(AppSpacing.xs),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(AppShapes.radiusLG),
          boxShadow: [
            BoxShadow(
              color: isDarkMode
                  ? Colors.black.withAlpha(40)
                  : Colors.black.withAlpha(20),
              blurRadius: 8,
              offset: const Offset(0, 2),
              spreadRadius: 0,
            ),
          ],
        ),
        child: cardContent,
      );
    } else {
      return Container(
        height: height,
        width: width,
        margin: margin,
        child: cardContent,
      );
    }
  }

  /// 构建卡片内容
  Widget _buildCardContent(BuildContext context, bool isDarkMode) {
    // 创建内容组件
    Widget contentWidget = content;

    // 如果有明确的尺寸约束，使用Flexible包装内容
    if (height != null || width != null) {
      contentWidget = Flexible(child: content);
    }

    return Container(
      padding: padding ?? _getDefaultPadding(),
      decoration: BoxDecoration(
        color: _getBackgroundColor(isDarkMode),
        gradient: style == AppCardStyle.gradient
            ? (gradient ?? _getDefaultGradient(isDarkMode))
            : null,
        borderRadius: BorderRadius.circular(AppShapes.radiusLG),
        border: showBorder || style == AppCardStyle.outline
            ? Border.all(
                color: borderColor ?? _getBorderColor(isDarkMode),
                width: 1.0,
              )
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // 标题行
          if (title != null || leadingIcon != null || trailingIcon != null) ...[
            _buildTitleRow(context, isDarkMode),
            SizedBox(height: AppSpacing.sm),
          ],

          // 内容
          contentWidget,
        ],
      ),
    );
  }

  /// 构建标题行
  Widget _buildTitleRow(BuildContext context, bool isDarkMode) {
    return Row(
      children: [
        // 前导图标
        if (leadingIcon != null) ...[
          Icon(
            leadingIcon,
            color: _getTitleColor(isDarkMode),
            size: _getIconSize(),
          ),
          SizedBox(width: AppSpacing.xs),
        ],

        // 标题和副标题
        if (title != null)
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title!,
                  style: TextStyle(
                    fontSize: _getTitleFontSize(),
                    fontWeight: FontWeight.bold,
                    color: _getTitleColor(isDarkMode),
                  ),
                ),
                if (subtitle != null) ...[
                  SizedBox(height: 2),
                  Text(
                    subtitle!,
                    style: TextStyle(
                      fontSize: _getSubtitleFontSize(),
                      color: isDarkMode
                          ? AppColors.darkTextSecondary
                          : AppColors.lightTextSecondary,
                    ),
                  ),
                ],
              ],
            ),
          ),

        // 尾随图标或操作
        if (trailingIcon != null)
          Icon(
            trailingIcon,
            color: _getTitleColor(isDarkMode),
            size: _getIconSize(),
          ),

        if (trailingAction != null) trailingAction!,
      ],
    );
  }

  /// 获取默认内边距
  EdgeInsets _getDefaultPadding() {
    switch (size) {
      case AppCardSize.small:
        return EdgeInsets.all(AppSpacing.sm);
      case AppCardSize.medium:
        return EdgeInsets.all(AppSpacing.md);
      case AppCardSize.large:
        return EdgeInsets.all(AppSpacing.lg);
    }
  }

  /// 获取标题字体大小
  double _getTitleFontSize() {
    switch (size) {
      case AppCardSize.small:
        return 14.0;
      case AppCardSize.medium:
        return 16.0;
      case AppCardSize.large:
        return 18.0;
    }
  }

  /// 获取副标题字体大小
  double _getSubtitleFontSize() {
    switch (size) {
      case AppCardSize.small:
        return 12.0;
      case AppCardSize.medium:
        return 13.0;
      case AppCardSize.large:
        return 14.0;
    }
  }

  /// 获取图标大小
  double _getIconSize() {
    switch (size) {
      case AppCardSize.small:
        return 16.0;
      case AppCardSize.medium:
        return 20.0;
      case AppCardSize.large:
        return 24.0;
    }
  }

  /// 获取背景颜色
  Color _getBackgroundColor(bool isDarkMode) {
    if (backgroundColor != null) return backgroundColor!;

    switch (style) {
      case AppCardStyle.standard:
        return isDarkMode ? AppColors.darkSurface : AppColors.lightSurface;
      case AppCardStyle.light:
        return isDarkMode
            ? AppColors.darkSurface.withAlpha(180)
            : AppColors.lightSurface.withAlpha(230);
      case AppCardStyle.frosted:
        return isDarkMode ? AppColors.iosBlurDark : AppColors.iosBlurLight;
      case AppCardStyle.outline:
        return Colors.transparent;
      case AppCardStyle.gradient:
        // 渐变风格使用透明背景色，渐变由BoxDecoration.gradient提供
        return Colors.transparent;
    }
  }

  /// 获取边框颜色
  Color _getBorderColor(bool isDarkMode) {
    if (borderColor != null) return borderColor!;

    return isDarkMode ? AppColors.darkBorder : AppColors.lightBorder;
  }

  /// 获取标题颜色
  Color _getTitleColor(bool isDarkMode) {
    return isDarkMode ? AppColors.darkTextPrimary : AppColors.lightTextPrimary;
  }

  /// 获取默认渐变色
  LinearGradient _getDefaultGradient(bool isDarkMode) {
    return LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        AppColors.primaryColor,
        AppColors.primaryLight,
      ],
    );
  }
}

/// 标准卡片
class BasicCard extends AppCard {
  const BasicCard({
    super.key,
    super.title,
    super.subtitle,
    required super.content,
    super.size = AppCardSize.medium,
    super.height,
    super.width,
    super.leadingIcon,
    super.trailingIcon,
    super.trailingAction,
    super.backgroundColor,
    super.onTap,
    super.onLongPress,
    super.hasShadow = true,
    super.padding,
    super.margin,
  }) : super(style: AppCardStyle.standard);
}

/// 磨砂卡片
class FrostedCard extends AppCard {
  const FrostedCard({
    super.key,
    super.title,
    super.subtitle,
    required super.content,
    super.size = AppCardSize.medium,
    super.height,
    super.width,
    super.leadingIcon,
    super.trailingIcon,
    super.trailingAction,
    super.backgroundColor,
    super.onTap,
    super.onLongPress,
    super.hasShadow = true,
    super.padding,
    super.margin,
  }) : super(style: AppCardStyle.frosted);
}

/// 渐变卡片
class GradientCard extends AppCard {
  const GradientCard({
    super.key,
    super.title,
    super.subtitle,
    required super.content,
    super.size = AppCardSize.medium,
    super.height,
    super.width,
    super.leadingIcon,
    super.trailingIcon,
    super.trailingAction,
    super.gradient,
    super.onTap,
    super.onLongPress,
    super.hasShadow = true,
    super.padding,
    super.margin,
  }) : super(style: AppCardStyle.gradient);
}

/// 轮廓卡片
class OutlineCard extends AppCard {
  const OutlineCard({
    super.key,
    super.title,
    super.subtitle,
    required super.content,
    super.size = AppCardSize.medium,
    super.height,
    super.width,
    super.leadingIcon,
    super.trailingIcon,
    super.trailingAction,
    super.borderColor,
    super.onTap,
    super.onLongPress,
    super.padding,
    super.margin,
  }) : super(
          style: AppCardStyle.outline,
          showBorder: true,
          hasShadow: false,
        );
}
