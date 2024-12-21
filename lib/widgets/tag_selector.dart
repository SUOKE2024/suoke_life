import 'package:flutter/material.dart';

class TagSelector extends StatelessWidget {
  final List<String> selectedTags;
  final Function(String) onTagSelected;
  final List<String> availableTags;

  const TagSelector({
    Key? key,
    required this.selectedTags,
    required this.onTagSelected,
    this.availableTags = const [
      '健康', '运动', '饮食', '心情',
      '工作', '学习', '娱乐', '生活',
      '其他'
    ],
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: availableTags.map((tag) {
        final isSelected = selectedTags.contains(tag);
        return FilterChip(
          label: Text(tag),
          selected: isSelected,
          onSelected: (_) => onTagSelected(tag),
          backgroundColor: Colors.grey[200],
          selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
          checkmarkColor: Theme.of(context).primaryColor,
          labelStyle: TextStyle(
            color: isSelected 
              ? Theme.of(context).primaryColor
              : Colors.black87,
          ),
        );
      }).toList(),
    );
  }
} 