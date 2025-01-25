import 'package:flutter/material.dart';

class TagSelector extends StatelessWidget {
  final List<String> tags;
  final List<String> selectedTags;
  final ValueChanged<String> onTagToggle;

  const TagSelector({
    Key? key,
    required this.tags,
    required this.selectedTags,
    required this.onTagToggle,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: tags.map((tag) {
        final isSelected = selectedTags.contains(tag);
        return FilterChip(
          label: Text(tag),
          selected: isSelected,
          onSelected: (_) => onTagToggle(tag),
          backgroundColor: isSelected 
            ? Theme.of(context).primaryColor.withOpacity(0.1)
            : null,
          selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
        );
      }).toList(),
    );
  }
} 