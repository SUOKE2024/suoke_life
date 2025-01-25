import 'package:flutter/material.dart';

/// 评分组件
class AppRating extends StatelessWidget {
  final double value;
  final int count;
  final double size;
  final Color? activeColor;
  final Color? inactiveColor;
  final ValueChanged<double>? onChanged;
  final IconData activeIcon;
  final IconData inactiveIcon;
  final bool allowHalf;
  final bool readonly;
  
  const AppRating({
    super.key,
    required this.value,
    this.count = 5,
    this.size = 24,
    this.activeColor,
    this.inactiveColor,
    this.onChanged,
    this.activeIcon = Icons.star,
    this.inactiveIcon = Icons.star_border,
    this.allowHalf = true,
    this.readonly = false,
  }) : assert(value >= 0 && value <= count);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultActiveColor = activeColor ?? theme.primaryColor;
    final defaultInactiveColor = inactiveColor ?? Colors.grey;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(count, (index) {
        final active = value > index;
        final half = allowHalf && value > index && value < index + 1;

        return GestureDetector(
          onTapDown: readonly ? null : (details) {
            final box = context.findRenderObject() as RenderBox;
            final pos = box.globalToLocal(details.globalPosition);
            final i = index + (pos.dx % size > size / 2 ? 1 : 0.5);
            onChanged?.call(i.clamp(0, count).toDouble());
          },
          child: Icon(
            half ? Icons.star_half : (active ? activeIcon : inactiveIcon),
            size: size,
            color: active ? defaultActiveColor : defaultInactiveColor,
          ),
        );
      }),
    );
  }
} 