import 'package:flutter/material.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/theme/app_shapes.dart';
import 'package:suoke_life/core/theme/app_spacing.dart';

/// 骨架屏加载组件
///
/// 用于在数据加载时显示内容占位符，提升用户体验
/// 支持多种形状和自定义配置
class SkeletonLoading extends StatefulWidget {
  /// 宽度
  final double? width;

  /// 高度
  final double? height;

  /// 形状 (默认为矩形)
  final SkeletonShape shape;

  /// 圆角
  final BorderRadius? borderRadius;

  /// 是否显示动画
  final bool showAnimation;

  /// 自定义颜色
  final Color? baseColor;

  /// 自定义高亮颜色
  final Color? highlightColor;

  /// 动画速度 (毫秒)
  final int animationDuration;

  const SkeletonLoading({
    Key? key,
    this.width,
    this.height,
    this.shape = SkeletonShape.rectangle,
    this.borderRadius,
    this.showAnimation = true,
    this.baseColor,
    this.highlightColor,
    this.animationDuration = 1500,
  }) : super(key: key);

  @override
  State<SkeletonLoading> createState() => _SkeletonLoadingState();
}

class _SkeletonLoadingState extends State<SkeletonLoading>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: widget.animationDuration),
    );

    _animation = Tween<double>(begin: -2, end: 2).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine),
    );

    if (widget.showAnimation) {
      _controller.repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    // 设置默认颜色
    final Color effectiveBaseColor = widget.baseColor ??
        (isDarkMode ? AppColors.darkSystemGray5 : AppColors.lightSystemGray5);

    final Color effectiveHighlightColor = widget.highlightColor ??
        (isDarkMode ? AppColors.darkSystemGray4 : AppColors.lightSystemGray4);

    // 设置边框半径
    BorderRadius? effectiveBorderRadius = widget.shape == SkeletonShape.circle
        ? null
        : (widget.borderRadius ?? _getDefaultBorderRadius());

    if (widget.showAnimation) {
      return AnimatedBuilder(
        animation: _animation,
        builder: (context, child) {
          return Container(
            width: widget.width,
            height: widget.height,
            decoration: BoxDecoration(
              borderRadius: effectiveBorderRadius,
              shape: widget.shape == SkeletonShape.circle
                  ? BoxShape.circle
                  : BoxShape.rectangle,
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  effectiveBaseColor,
                  effectiveHighlightColor,
                  effectiveBaseColor,
                ],
                stops: [
                  0.0,
                  (_animation.value + 2) / 4, // 0.0 -> 1.0
                  1.0,
                ],
              ),
            ),
          );
        },
      );
    } else {
      return Container(
        width: widget.width,
        height: widget.height,
        decoration: BoxDecoration(
          borderRadius: effectiveBorderRadius,
          shape: widget.shape == SkeletonShape.circle
              ? BoxShape.circle
              : BoxShape.rectangle,
          color: effectiveBaseColor,
        ),
      );
    }
  }

  BorderRadius _getDefaultBorderRadius() {
    switch (widget.shape) {
      case SkeletonShape.rectangle:
        return BorderRadius.circular(AppShapes.radiusXS);
      case SkeletonShape.rounded:
        return BorderRadius.circular(AppShapes.radiusSM);
      case SkeletonShape.circle:
        return BorderRadius.circular(1000); // 圆形效果
      case SkeletonShape.card:
        return BorderRadius.circular(AppShapes.radiusLG);
    }
  }
}

/// 骨架屏形状
enum SkeletonShape {
  /// 矩形 (默认)
  rectangle,

  /// 圆角矩形
  rounded,

  /// 圆形
  circle,

  /// 卡片样式
  card,
}

/// 文本占位骨架
///
/// 用于显示多行文本的骨架加载
class SkeletonText extends StatelessWidget {
  /// 行数
  final int lines;

  /// 行高
  final double lineHeight;

  /// 最大宽度
  final double? maxWidth;

  /// 最短行的宽度百分比 (相对于最大宽度)
  final double minWidthPercentage;

  /// 行间距
  final double spacing;

  /// 是否随机宽度
  final bool randomWidths;

  /// 自定义颜色
  final Color? baseColor;

  /// 自定义高亮颜色
  final Color? highlightColor;

  /// 是否显示动画
  final bool showAnimation;

  /// 动画速度
  final int animationDuration;

  const SkeletonText({
    Key? key,
    this.lines = 3,
    this.lineHeight = 16,
    this.maxWidth,
    this.minWidthPercentage = 0.5,
    this.spacing = 8,
    this.randomWidths = true,
    this.baseColor,
    this.highlightColor,
    this.showAnimation = true,
    this.animationDuration = 1500,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final effectiveMaxWidth = maxWidth ?? constraints.maxWidth;
        final List<Widget> children = [];

        // 创建随机种子
        final seed = DateTime.now().millisecondsSinceEpoch;
        final random = randomWidths ? seed : null;

        for (int i = 0; i < lines; i++) {
          // 计算宽度 (最后一行总是最短的)
          double width;
          if (i == lines - 1) {
            width = effectiveMaxWidth * (minWidthPercentage + 0.1);
          } else if (randomWidths && random != null) {
            // 随机宽度，但确保在minWidthPercentage和1.0之间
            width = effectiveMaxWidth *
                (minWidthPercentage +
                    (1.0 - minWidthPercentage) * ((i * random) % 100) / 100);
          } else {
            width = effectiveMaxWidth;
          }

          children.add(
            SkeletonLoading(
              width: width,
              height: lineHeight,
              shape: SkeletonShape.rounded,
              baseColor: baseColor,
              highlightColor: highlightColor,
              showAnimation: showAnimation,
              animationDuration: animationDuration,
            ),
          );

          if (i < lines - 1) {
            children.add(SizedBox(height: spacing));
          }
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: children,
        );
      },
    );
  }
}

/// 列表项骨架
///
/// 用于显示列表项的骨架加载
class SkeletonListTile extends StatelessWidget {
  /// 是否有前导图标
  final bool hasLeading;

  /// 是否有副标题
  final bool hasSubtitle;

  /// 是否有尾随图标
  final bool hasTrailing;

  /// 标题宽度百分比
  final double titleWidthPercentage;

  /// 副标题宽度百分比
  final double subtitleWidthPercentage;

  /// 自定义高度
  final double? height;

  /// 自定义颜色
  final Color? baseColor;

  /// 自定义高亮颜色
  final Color? highlightColor;

  /// 是否显示动画
  final bool showAnimation;

  /// 列表项内边距
  final EdgeInsetsGeometry? padding;

  const SkeletonListTile({
    Key? key,
    this.hasLeading = true,
    this.hasSubtitle = true,
    this.hasTrailing = true,
    this.titleWidthPercentage = 0.7,
    this.subtitleWidthPercentage = 0.5,
    this.height,
    this.baseColor,
    this.highlightColor,
    this.showAnimation = true,
    this.padding,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height ?? 72.0,
      padding: padding ??
          EdgeInsets.symmetric(
            vertical: AppSpacing.sm,
            horizontal: AppSpacing.md,
          ),
      child: Row(
        children: [
          // 前导图标
          if (hasLeading) ...[
            SkeletonLoading(
              width: 40,
              height: 40,
              shape: SkeletonShape.circle,
              baseColor: baseColor,
              highlightColor: highlightColor,
              showAnimation: showAnimation,
            ),
            SizedBox(width: AppSpacing.md),
          ],

          // 标题和副标题
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // 标题
                SkeletonLoading(
                  width:
                      MediaQuery.of(context).size.width * titleWidthPercentage,
                  height: 16,
                  shape: SkeletonShape.rounded,
                  baseColor: baseColor,
                  highlightColor: highlightColor,
                  showAnimation: showAnimation,
                ),

                // 副标题
                if (hasSubtitle) ...[
                  SizedBox(height: AppSpacing.xs),
                  SkeletonLoading(
                    width: MediaQuery.of(context).size.width *
                        subtitleWidthPercentage,
                    height: 14,
                    shape: SkeletonShape.rounded,
                    baseColor: baseColor,
                    highlightColor: highlightColor,
                    showAnimation: showAnimation,
                  ),
                ],
              ],
            ),
          ),

          // 尾随图标
          if (hasTrailing) ...[
            SizedBox(width: AppSpacing.md),
            SkeletonLoading(
              width: 24,
              height: 24,
              shape: SkeletonShape.circle,
              baseColor: baseColor,
              highlightColor: highlightColor,
              showAnimation: showAnimation,
            ),
          ],
        ],
      ),
    );
  }
}

/// 卡片骨架
///
/// 用于显示卡片的骨架加载
class SkeletonCard extends StatelessWidget {
  /// 宽度
  final double? width;

  /// 高度
  final double? height;

  /// 是否有标题
  final bool hasTitle;

  /// 内容行数
  final int contentLines;

  /// 是否有图像
  final bool hasImage;

  /// 自定义图像高度
  final double? imageHeight;

  /// 自定义颜色
  final Color? baseColor;

  /// 自定义高亮颜色
  final Color? highlightColor;

  /// 是否显示动画
  final bool showAnimation;

  /// 内边距
  final EdgeInsetsGeometry padding;

  const SkeletonCard({
    Key? key,
    this.width,
    this.height,
    this.hasTitle = true,
    this.contentLines = 3,
    this.hasImage = false,
    this.imageHeight,
    this.baseColor,
    this.highlightColor,
    this.showAnimation = true,
    this.padding = const EdgeInsets.all(16.0),
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      padding: padding,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(AppShapes.radiusLG),
        border: Border.all(
          color: Theme.of(context).dividerColor.withAlpha(50),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 图像
          if (hasImage) ...[
            SkeletonLoading(
              width: double.infinity,
              height: imageHeight ?? 120,
              shape: SkeletonShape.rounded,
              baseColor: baseColor,
              highlightColor: highlightColor,
              showAnimation: showAnimation,
            ),
            SizedBox(height: AppSpacing.md),
          ],

          // 标题
          if (hasTitle) ...[
            SkeletonLoading(
              width: width != null ? width! * 0.7 : 200,
              height: 20,
              shape: SkeletonShape.rounded,
              baseColor: baseColor,
              highlightColor: highlightColor,
              showAnimation: showAnimation,
            ),
            SizedBox(height: AppSpacing.md),
          ],

          // 内容
          Expanded(
            child: SkeletonText(
              lines: contentLines,
              lineHeight: 14,
              spacing: 8,
              baseColor: baseColor,
              highlightColor: highlightColor,
              showAnimation: showAnimation,
            ),
          ),
        ],
      ),
    );
  }
}

/// 内容占位符组件
///
/// 在数据加载或出错时提供视觉占位，提升用户体验
class ContentPlaceholder extends StatelessWidget {
  /// 占位符宽度
  final double width;

  /// 占位符高度
  final double height;

  /// 占位符形状 (矩形, 圆形, 圆角矩形)
  final BoxShape shape;

  /// 圆角大小 (当形状为圆角矩形时使用)
  final double borderRadius;

  /// 占位符颜色
  final Color? color;

  /// 是否显示动画效果
  final bool animate;

  const ContentPlaceholder({
    Key? key,
    required this.width,
    required this.height,
    this.shape = BoxShape.rectangle,
    this.borderRadius = 8.0,
    this.color,
    this.animate = true,
  }) : super(key: key);

  /// 创建矩形占位符
  factory ContentPlaceholder.rectangle({
    required double width,
    required double height,
    Color? color,
    bool? animate,
  }) = _RectanglePlaceholder;

  /// 创建圆角矩形占位符
  factory ContentPlaceholder.rounded({
    required double width,
    required double height,
    double? borderRadius,
    Color? color,
    bool? animate,
  }) = _RoundedPlaceholder;

  /// 创建圆形占位符
  factory ContentPlaceholder.circle({
    required double size,
    Color? color,
    bool? animate,
  }) = _CirclePlaceholder;

  @override
  Widget build(BuildContext context) {
    final effectiveColor =
        color ?? Theme.of(context).disabledColor.withAlpha((0.2 * 255).toInt());

    // 根据形状选择实现方式
    Widget placeholder;

    if (shape == BoxShape.circle) {
      // 对于圆形，使用ClipOval而不是BoxShape.circle
      placeholder = ClipOval(
        child: Container(
          width: width,
          height: height,
          color: effectiveColor,
        ),
      );
    } else {
      // 对于矩形或圆角矩形
      placeholder = borderRadius > 0
          ? ClipRRect(
              borderRadius: BorderRadius.circular(borderRadius),
              child: Container(
                width: width,
                height: height,
                color: effectiveColor,
              ),
            )
          : Container(
              width: width,
              height: height,
              color: effectiveColor,
            );
    }

    if (animate) {
      placeholder = _PlaceholderAnimation(
        child: placeholder,
      );
    }

    return placeholder;
  }
}

/// 矩形占位符
class _RectanglePlaceholder extends ContentPlaceholder {
  _RectanglePlaceholder({
    required double width,
    required double height,
    Color? color,
    bool? animate,
  }) : super(
          width: width,
          height: height,
          shape: BoxShape.rectangle,
          borderRadius: 0,
          color: color,
          animate: animate ?? true,
        );
}

/// 圆角矩形占位符
class _RoundedPlaceholder extends ContentPlaceholder {
  _RoundedPlaceholder({
    required double width,
    required double height,
    double? borderRadius,
    Color? color,
    bool? animate,
  }) : super(
          width: width,
          height: height,
          shape: BoxShape.rectangle,
          borderRadius: borderRadius ?? 8.0,
          color: color,
          animate: animate ?? true,
        );
}

/// 圆形占位符
class _CirclePlaceholder extends ContentPlaceholder {
  _CirclePlaceholder({
    required double size,
    Color? color,
    bool? animate,
  }) : super(
          width: size,
          height: size,
          shape: BoxShape.circle,
          color: color,
          animate: animate ?? true,
        );
}

/// 占位符动画包装组件
class _PlaceholderAnimation extends StatefulWidget {
  final Widget child;

  const _PlaceholderAnimation({
    Key? key,
    required this.child,
  }) : super(key: key);

  @override
  _PlaceholderAnimationState createState() => _PlaceholderAnimationState();
}

class _PlaceholderAnimationState extends State<_PlaceholderAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _animation = Tween<double>(begin: 0.4, end: 0.8).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Opacity(
          opacity: _animation.value,
          child: child,
        );
      },
      child: widget.child,
    );
  }
}
