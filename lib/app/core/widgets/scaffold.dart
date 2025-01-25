import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// 页面骨架组件
class AppScaffold extends StatelessWidget {
  final String? title;
  final Widget? titleWidget;
  final Widget? body;
  final Widget? bottomBar;
  final Widget? floatingActionButton;
  final FloatingActionButtonLocation? floatingActionButtonLocation;
  final bool showBackButton;
  final List<Widget>? actions;
  final Color? backgroundColor;
  final Color? appBarBackgroundColor;
  final SystemUiOverlayStyle? systemOverlayStyle;
  final bool extendBody;
  final bool extendBodyBehindAppBar;
  final bool resizeToAvoidBottomInset;
  final EdgeInsets? padding;
  
  const AppScaffold({
    super.key,
    this.title,
    this.titleWidget,
    this.body,
    this.bottomBar,
    this.floatingActionButton,
    this.floatingActionButtonLocation,
    this.showBackButton = true,
    this.actions,
    this.backgroundColor,
    this.appBarBackgroundColor,
    this.systemOverlayStyle,
    this.extendBody = false,
    this.extendBodyBehindAppBar = false,
    this.resizeToAvoidBottomInset = true,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final canPop = Navigator.of(context).canPop();
    
    Widget? leading;
    if (showBackButton && canPop) {
      leading = IconButton(
        icon: const Icon(Icons.arrow_back_ios),
        onPressed: () => Navigator.of(context).pop(),
      );
    }

    Widget? content = body;
    if (padding != null) {
      content = Padding(
        padding: padding!,
        child: content,
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: titleWidget ?? (title != null ? Text(title!) : null),
        leading: leading,
        actions: actions,
        backgroundColor: appBarBackgroundColor,
        systemOverlayStyle: systemOverlayStyle,
        centerTitle: true,
      ),
      body: content,
      bottomNavigationBar: bottomBar,
      floatingActionButton: floatingActionButton,
      floatingActionButtonLocation: floatingActionButtonLocation,
      backgroundColor: backgroundColor,
      extendBody: extendBody,
      extendBodyBehindAppBar: extendBodyBehindAppBar,
      resizeToAvoidBottomInset: resizeToAvoidBottomInset,
    );
  }
} 