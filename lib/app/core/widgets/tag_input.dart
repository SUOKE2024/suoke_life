/// 标签输入组件
class TagInput extends StatefulWidget {
  final List<String> value;
  final ValueChanged<List<String>>? onChanged;
  final String? label;
  final String? hint;
  final String? addHint;
  final bool enabled;
  final bool readOnly;
  final InputDecoration? decoration;
  final TextStyle? style;
  final TextStyle? tagStyle;
  final Color? tagColor;
  final Color? tagBackgroundColor;
  final double? tagSpacing;
  final double? runSpacing;
  final bool allowDuplicates;
  final int? maxLength;
  final RegExp? validator;
  final String? Function(String)? onValidate;
  final String? errorText;
  final Widget? prefix;
  final Widget? suffix;

  const TagInput({
    super.key,
    required this.value,
    this.onChanged,
    this.label,
    this.hint,
    this.addHint,
    this.enabled = true,
    this.readOnly = false,
    this.decoration,
    this.style,
    this.tagStyle,
    this.tagColor,
    this.tagBackgroundColor,
    this.tagSpacing,
    this.runSpacing,
    this.allowDuplicates = false,
    this.maxLength,
    this.validator,
    this.onValidate,
    this.errorText,
    this.prefix,
    this.suffix,
  });

  @override
  State<TagInput> createState() => _TagInputState();
}

class _TagInputState extends State<TagInput> {
  late TextEditingController _controller;
  late FocusNode _focusNode;
  late List<String> _tags;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tags = List.from(widget.value);
    _controller = TextEditingController();
    _focusNode = FocusNode();
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _addTag(String tag) {
    tag = tag.trim();
    if (tag.isEmpty) return;

    if (!widget.allowDuplicates && _tags.contains(tag)) {
      setState(() => _error = '标签已存在');
      return;
    }

    if (widget.maxLength != null && _tags.length >= widget.maxLength!) {
      setState(() => _error = '已达到最大数量');
      return;
    }

    if (widget.validator != null && !widget.validator!.hasMatch(tag)) {
      setState(() => _error = '标签格式不正确');
      return;
    }

    if (widget.onValidate != null) {
      final error = widget.onValidate!(tag);
      if (error != null) {
        setState(() => _error = error);
        return;
      }
    }

    setState(() {
      _tags.add(tag);
      _controller.clear();
      _error = null;
    });

    widget.onChanged?.call(_tags);
  }

  void _removeTag(int index) {
    setState(() {
      _tags.removeAt(index);
      _error = null;
    });
    widget.onChanged?.call(_tags);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultTagSpacing = widget.tagSpacing ?? 8.0;
    final defaultRunSpacing = widget.runSpacing ?? 8.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (widget.label != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              widget.label!,
              style: theme.textTheme.bodyMedium,
            ),
          ),
        Wrap(
          spacing: defaultTagSpacing,
          runSpacing: defaultRunSpacing,
          children: [
            ..._tags.asMap().entries.map((entry) {
              return AppTag(
                text: entry.value,
                color: widget.tagColor,
                backgroundColor: widget.tagBackgroundColor,
                textStyle: widget.tagStyle,
                closable: widget.enabled && !widget.readOnly,
                onClose: () => _removeTag(entry.key),
              );
            }),
            if (widget.enabled && !widget.readOnly)
              SizedBox(
                width: 120,
                child: TextField(
                  controller: _controller,
                  focusNode: _focusNode,
                  style: widget.style,
                  decoration: widget.decoration?.copyWith(
                    hintText: widget.addHint ?? '添加标签',
                    errorText: _error ?? widget.errorText,
                    prefixIcon: widget.prefix,
                    suffixIcon: widget.suffix,
                  ) ??
                      InputDecoration(
                        hintText: widget.addHint ?? '添加标签',
                        errorText: _error ?? widget.errorText,
                        prefixIcon: widget.prefix,
                        suffixIcon: widget.suffix,
                        isDense: true,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                      ),
                  onSubmitted: _addTag,
                ),
              ),
          ],
        ),
      ],
    );
  }
} 