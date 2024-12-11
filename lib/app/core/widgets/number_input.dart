/// 数字输入框组件
class NumberInput extends StatefulWidget {
  final num? value;
  final num? min;
  final num? max;
  final num step;
  final int? precision;
  final ValueChanged<num?>? onChanged;
  final String? label;
  final String? hint;
  final bool enabled;
  final bool controls;
  final bool allowEmpty;
  final TextInputType? keyboardType;
  final InputDecoration? decoration;
  final TextStyle? style;
  final TextAlign textAlign;
  final Widget? prefix;
  final Widget? suffix;
  final EdgeInsets? contentPadding;
  final bool readOnly;
  final FocusNode? focusNode;

  const NumberInput({
    super.key,
    this.value,
    this.min,
    this.max,
    this.step = 1,
    this.precision,
    this.onChanged,
    this.label,
    this.hint,
    this.enabled = true,
    this.controls = true,
    this.allowEmpty = false,
    this.keyboardType,
    this.decoration,
    this.style,
    this.textAlign = TextAlign.start,
    this.prefix,
    this.suffix,
    this.contentPadding,
    this.readOnly = false,
    this.focusNode,
  });

  @override
  State<NumberInput> createState() => _NumberInputState();
}

class _NumberInputState extends State<NumberInput> {
  late TextEditingController _controller;
  late FocusNode _focusNode;
  num? _value;
  bool _isValid = true;

  @override
  void initState() {
    super.initState();
    _value = widget.value;
    _controller = TextEditingController(
      text: _formatValue(_value),
    );
    _focusNode = widget.focusNode ?? FocusNode();
    _focusNode.addListener(_onFocusChanged);
  }

  @override
  void dispose() {
    _controller.dispose();
    if (widget.focusNode == null) {
      _focusNode.dispose();
    }
    super.dispose();
  }

  @override
  void didUpdateWidget(NumberInput oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      _value = widget.value;
      _controller.text = _formatValue(_value);
    }
  }

  void _onFocusChanged() {
    if (!_focusNode.hasFocus) {
      _validateAndFormat();
    }
  }

  String _formatValue(num? value) {
    if (value == null) return '';
    if (widget.precision != null) {
      return value.toStringAsFixed(widget.precision!);
    }
    return value.toString();
  }

  void _validateAndFormat() {
    final text = _controller.text.trim();
    if (text.isEmpty && widget.allowEmpty) {
      _updateValue(null);
      return;
    }

    final number = num.tryParse(text);
    if (number == null) {
      setState(() => _isValid = false);
      return;
    }

    if (widget.min != null && number < widget.min!) {
      _updateValue(widget.min);
    } else if (widget.max != null && number > widget.max!) {
      _updateValue(widget.max);
    } else {
      _updateValue(number);
    }
  }

  void _updateValue(num? value) {
    setState(() {
      _value = value;
      _controller.text = _formatValue(value);
      _isValid = true;
    });
    widget.onChanged?.call(value);
  }

  void _increment() {
    if (!widget.enabled || widget.readOnly) return;
    final newValue = (_value ?? 0) + widget.step;
    if (widget.max != null && newValue > widget.max!) return;
    _updateValue(newValue);
  }

  void _decrement() {
    if (!widget.enabled || widget.readOnly) return;
    final newValue = (_value ?? 0) - widget.step;
    if (widget.min != null && newValue < widget.min!) return;
    _updateValue(newValue);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    final defaultDecoration = InputDecoration(
      labelText: widget.label,
      hintText: widget.hint,
      errorText: !_isValid ? '无效的数值' : null,
      contentPadding: widget.contentPadding ??
          const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      prefixIcon: widget.prefix,
      suffixIcon: widget.suffix,
      border: const OutlineInputBorder(),
    );

    Widget input = TextField(
      controller: _controller,
      focusNode: _focusNode,
      enabled: widget.enabled && !widget.readOnly,
      readOnly: widget.readOnly,
      keyboardType: widget.keyboardType ??
          const TextInputType.numberWithOptions(decimal: true),
      textAlign: widget.textAlign,
      style: widget.style,
      decoration: widget.decoration ?? defaultDecoration,
      onChanged: (value) {
        final number = num.tryParse(value);
        setState(() {
          _isValid = number != null || (value.isEmpty && widget.allowEmpty);
        });
      },
      onSubmitted: (_) => _validateAndFormat(),
    );

    if (widget.controls) {
      input = Row(
        children: [
          IconButton(
            onPressed: widget.enabled && !widget.readOnly ? _decrement : null,
            icon: const Icon(Icons.remove),
          ),
          Expanded(child: input),
          IconButton(
            onPressed: widget.enabled && !widget.readOnly ? _increment : null,
            icon: const Icon(Icons.add),
          ),
        ],
      );
    }

    return input;
  }
} 