import 'package:flutter/material.dart';

/// 分割线组件
class AppDivider extends StatelessWidget {
  final double? height;
  final double? thickness;
  final double? indent;
  final double? endIndent;
  final Color? color;
  
  const AppDivider({
    super.key,
    this.height,
    this.thickness,
    this.indent,
    this.endIndent,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Divider(
      height: height,
      thickness: thickness,
      indent: indent,
      endIndent: endIndent,
      color: color,
    );
  }
}

/// 垂直分割线组件
class AppVerticalDivider extends StatelessWidget {
  final double? width;
  final double? thickness;
  final double? indent;
  final double? endIndent;
  final Color? color;
  
  const AppVerticalDivider({
    super.key,
    this.width,
    this.thickness,
    this.indent,
    this.endIndent,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return VerticalDivider(
      width: width,
      thickness: thickness,
      indent: indent,
      endIndent: endIndent,
      color: color,
    );
  }
} 