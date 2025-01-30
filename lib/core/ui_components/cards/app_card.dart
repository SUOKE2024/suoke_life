import 'package:flutter/material.dart';
import 'package:ui_components/styles/app_colors.dart';

class AppCard extends StatelessWidget {
  final Widget child;
  final double? elevation;
  final EdgeInsetsGeometry? margin;
  final Color? backgroundColor;

  const AppCard({
    super.key,
    required this.child,
    this.elevation,
    this.margin,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: elevation ?? 4,
      margin: margin,
      color: backgroundColor ?? AppColors.cardBackground,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: child,
      ),
    );
  }
}
