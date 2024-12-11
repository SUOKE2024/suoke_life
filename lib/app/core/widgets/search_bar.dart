/// 搜索组件
class AppSearchBar extends StatefulWidget {
  final String? hint;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final VoidCallback? onClear;
  final bool autofocus;
  final bool showClearButton;
  final TextEditingController? controller;
  final FocusNode? focusNode;
  final Color? backgroundColor;
  final Color? iconColor;
  final TextStyle? textStyle;
  final TextStyle? hintStyle;
  final BorderRadius? borderRadius;
  final EdgeInsets? contentPadding;
  final Widget? prefix;
  final Widget? suffix;

  const AppSearchBar({
    super.key,
    this.hint,
    this.onChanged,
    this.onSubmitted,
    this.onClear,
    this.autofocus = false,
    this.showClearButton = true,
    this.controller,
    this.focusNode,
    this.backgroundColor,
    this.iconColor,
    this.textStyle,
    this.hintStyle,
    this.borderRadius,
    this.contentPadding,
    this.prefix,
    this.suffix,
  });

  @override
  State<AppSearchBar> createState() => _AppSearchBarState();
}

class _AppSearchBarState extends State<AppSearchBar> {
  late TextEditingController _controller;
  late FocusNode _focusNode;
  bool _showClear = false;

  @override
  void initState() {
    super.initState();
    _controller = widget.controller ?? TextEditingController();
    _focusNode = widget.focusNode ?? FocusNode();
    _showClear = _controller.text.isNotEmpty;
    _controller.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    if (widget.controller == null) {
      _controller.dispose();
    }
    if (widget.focusNode == null) {
      _focusNode.dispose();
    }
    super.dispose();
  }

  void _onTextChanged() {
    final showClear = _controller.text.isNotEmpty;
    if (showClear != _showClear) {
      setState(() {
        _showClear = showClear;
      });
    }
    widget.onChanged?.call(_controller.text);
  }

  void _onClear() {
    _controller.clear();
    widget.onClear?.call();
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultBackgroundColor = theme.brightness == Brightness.light
        ? Colors.grey[100]
        : Colors.grey[800];

    return Container(
      decoration: BoxDecoration(
        color: widget.backgroundColor ?? defaultBackgroundColor,
        borderRadius: widget.borderRadius ?? BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          if (widget.prefix != null)
            Padding(
              padding: const EdgeInsets.only(left: 12),
              child: widget.prefix,
            )
          else
            Padding(
              padding: const EdgeInsets.only(left: 12),
              child: Icon(
                Icons.search,
                color: widget.iconColor ?? theme.hintColor,
              ),
            ),
          Expanded(
            child: TextField(
              controller: _controller,
              focusNode: _focusNode,
              autofocus: widget.autofocus,
              style: widget.textStyle,
              decoration: InputDecoration(
                hintText: widget.hint ?? '搜索',
                hintStyle: widget.hintStyle,
                border: InputBorder.none,
                contentPadding: widget.contentPadding ??
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
              onSubmitted: widget.onSubmitted,
            ),
          ),
          if (widget.showClearButton && _showClear)
            IconButton(
              icon: Icon(
                Icons.clear,
                color: widget.iconColor ?? theme.hintColor,
              ),
              onPressed: _onClear,
            )
          else if (widget.suffix != null)
            Padding(
              padding: const EdgeInsets.only(right: 12),
              child: widget.suffix,
            ),
        ],
      ),
    );
  }
} 