/// 折叠面板组件
class AppExpansionPanel extends StatefulWidget {
  final String title;
  final Widget? subtitle;
  final Widget child;
  final bool initiallyExpanded;
  final bool enabled;
  final Color? backgroundColor;
  final Color? textColor;
  final EdgeInsets? padding;
  final EdgeInsets? childPadding;
  final BorderRadius? borderRadius;
  final BoxBorder? border;
  final Widget? leading;
  final Widget? trailing;
  final ValueChanged<bool>? onExpansionChanged;

  const AppExpansionPanel({
    super.key,
    required this.title,
    this.subtitle,
    required this.child,
    this.initiallyExpanded = false,
    this.enabled = true,
    this.backgroundColor,
    this.textColor,
    this.padding,
    this.childPadding,
    this.borderRadius,
    this.border,
    this.leading,
    this.trailing,
    this.onExpansionChanged,
  });

  @override
  State<AppExpansionPanel> createState() => _AppExpansionPanelState();
}

class _AppExpansionPanelState extends State<AppExpansionPanel> {
  bool _isExpanded = false;

  @override
  void initState() {
    super.initState();
    _isExpanded = widget.initiallyExpanded;
  }

  void _handleTap() {
    if (!widget.enabled) return;
    setState(() {
      _isExpanded = !_isExpanded;
      widget.onExpansionChanged?.call(_isExpanded);
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultBackgroundColor = widget.backgroundColor ?? theme.cardColor;
    final defaultTextColor = widget.textColor ?? theme.textTheme.titleMedium?.color;

    return Container(
      decoration: BoxDecoration(
        color: defaultBackgroundColor,
        borderRadius: widget.borderRadius,
        border: widget.border,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          InkWell(
            onTap: _handleTap,
            child: Padding(
              padding: widget.padding ?? const EdgeInsets.all(16),
              child: Row(
                children: [
                  if (widget.leading != null) ...[
                    widget.leading!,
                    const SizedBox(width: 16),
                  ],
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.title,
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: defaultTextColor,
                          ),
                        ),
                        if (widget.subtitle != null) ...[
                          const SizedBox(height: 4),
                          DefaultTextStyle(
                            style: theme.textTheme.bodySmall ?? const TextStyle(),
                            child: widget.subtitle!,
                          ),
                        ],
                      ],
                    ),
                  ),
                  widget.trailing ??
                      Icon(
                        _isExpanded ? Icons.expand_less : Icons.expand_more,
                        color: theme.iconTheme.color,
                      ),
                ],
              ),
            ),
          ),
          AnimatedCrossFade(
            firstChild: const SizedBox(height: 0),
            secondChild: Padding(
              padding: widget.childPadding ?? const EdgeInsets.all(16),
              child: widget.child,
            ),
            crossFadeState: _isExpanded
                ? CrossFadeState.showSecond
                : CrossFadeState.showFirst,
            duration: const Duration(milliseconds: 200),
          ),
        ],
      ),
    );
  }
} 