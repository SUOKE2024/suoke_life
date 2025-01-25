import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// 应用栏组件
class AppAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String? title;
  final Widget? titleWidget;
  final Widget? leading;
  final List<Widget>? actions;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double? elevation;
  final SystemUiOverlayStyle? systemOverlayStyle;
  final bool centerTitle;
  final bool automaticallyImplyLeading;
  final double? toolbarHeight;
  final double? leadingWidth;
  final Widget? bottom;
  final double? bottomHeight;
  
  const AppAppBar({
    super.key,
    this.title,
    this.titleWidget,
    this.leading,
    this.actions,
    this.backgroundColor,
    this.foregroundColor,
    this.elevation,
    this.systemOverlayStyle,
    this.centerTitle = true,
    this.automaticallyImplyLeading = true,
    this.toolbarHeight,
    this.leadingWidth,
    this.bottom,
    this.bottomHeight,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: titleWidget ?? (title != null ? Text(title!) : null),
      leading: leading,
      actions: actions,
      backgroundColor: backgroundColor,
      foregroundColor: foregroundColor,
      elevation: elevation,
      systemOverlayStyle: systemOverlayStyle,
      centerTitle: centerTitle,
      automaticallyImplyLeading: automaticallyImplyLeading,
      toolbarHeight: toolbarHeight,
      leadingWidth: leadingWidth,
      bottom: bottom != null
          ? PreferredSize(
              preferredSize: Size.fromHeight(bottomHeight ?? 48),
              child: bottom!,
            )
          : null,
    );
  }

  @override
  Size get preferredSize => Size.fromHeight(
        (toolbarHeight ?? kToolbarHeight) + (bottomHeight ?? 0),
      );
} 