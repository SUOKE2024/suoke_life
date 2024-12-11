/// 基础页面组件
class BasePage extends StatelessWidget {
  final String? title;
  final Widget body;
  final List<Widget>? actions;
  final Widget? floatingActionButton;
  final Widget? bottomNavigationBar;
  final bool showAppBar;
  final bool showBackButton;
  final Color? backgroundColor;
  final EdgeInsets padding;

  const BasePage({
    super.key,
    this.title,
    required this.body,
    this.actions,
    this.floatingActionButton,
    this.bottomNavigationBar,
    this.showAppBar = true,
    this.showBackButton = true,
    this.backgroundColor,
    this.padding = AppStyles.padding,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: showAppBar ? _buildAppBar() : null,
      body: SafeArea(
        child: Padding(
          padding: padding,
          child: body,
        ),
      ),
      floatingActionButton: floatingActionButton,
      bottomNavigationBar: bottomNavigationBar,
      backgroundColor: backgroundColor ?? Theme.of(context).scaffoldBackgroundColor,
    );
  }

  PreferredSizeWidget? _buildAppBar() {
    if (!showAppBar) return null;
    
    return AppBar(
      title: title != null ? Text(title!) : null,
      centerTitle: true,
      leading: showBackButton ? const BackButton() : null,
      actions: actions,
      elevation: 0,
    );
  }
} 