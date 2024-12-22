import 'package:flutter/material.dart';
import '../../core/utils/debouncer.dart';

class SearchBar extends StatefulWidget {
  final String hint;
  final ValueChanged<String> onChanged;
  final VoidCallback? onClear;

  const SearchBar({
    Key? key,
    required this.hint,
    required this.onChanged,
    this.onClear,
  }) : super(key: key);

  @override
  State<SearchBar> createState() => _SearchBarState();
}

class _SearchBarState extends State<SearchBar> {
  final _debouncer = Debouncer(milliseconds: 500);
  final _textController = TextEditingController();

  @override
  void dispose() {
    _debouncer.dispose();
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: TextField(
        controller: _textController,
        onChanged: (value) {
          _debouncer.run(() => widget.onChanged(value.trim()));
        },
        textInputAction: TextInputAction.search,
        onSubmitted: (value) {
          widget.onChanged(value.trim());
        },
        decoration: InputDecoration(
          hintText: widget.hint,
          prefixIcon: const Icon(Icons.search),
          suffixIcon: IconButton(
            icon: const Icon(Icons.clear),
            onPressed: () {
              _textController.clear();
              widget.onClear?.call();
            },
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16),
        ),
      ),
    );
  }
} 