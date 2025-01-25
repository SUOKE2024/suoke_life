import 'package:flutter/material.dart';

class SearchHistoryChip extends StatelessWidget {
  final String keyword;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const SearchHistoryChip({
    Key? key,
    required this.keyword,
    required this.onTap,
    required this.onDelete,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ActionChip(
      label: Text(keyword),
      onPressed: onTap,
      deleteIcon: const Icon(
        Icons.close,
        size: 18,
      ),
      onDeleted: onDelete,
    );
  }
} 