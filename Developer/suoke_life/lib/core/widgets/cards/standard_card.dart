import 'package:flutter/material.dart';
import 'package:suoke_life/core/widgets/cards/app_card.dart';
import 'package:suoke_life/core/theme/app_colors.dart';

/// 标准卡片组件
///
/// 一个简化的卡片组件，基于AppCard，但提供了更为简洁的API
/// 适用于大多数场景下的卡片显示
class StandardCard extends StatelessWidget {
  /// 卡片标题
  final String? title;

  /// 卡片内容
  final Widget content;

  /// 卡片高度
  final double? height;

  /// 点击事件
  final VoidCallback? onTap;

  /// 内边距
  final EdgeInsetsGeometry? padding;

  /// 构造函数
  const StandardCard({
    super.key,
    this.title,
    required this.content,
    this.height,
    this.onTap,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return AppCard(
      title: title,
      content: content,
      height: height,
      style: AppCardStyle.standard,
      size: AppCardSize.medium,
      onTap: onTap,
      padding: padding,
    );
  }
}
