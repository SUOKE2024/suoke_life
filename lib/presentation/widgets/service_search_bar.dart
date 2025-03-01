import 'package:flutter/material.dart';

class ServiceSearchBar extends StatelessWidget {
  final TextEditingController? controller;
  final Function(String)? onChanged;
  final Function(String)? onSubmitted;
  final VoidCallback? onFilterPressed;
  final String hintText;
  final bool showFilterButton;
  
  const ServiceSearchBar({
    Key? key,
    this.controller,
    this.onChanged,
    this.onSubmitted,
    this.onFilterPressed,
    this.hintText = '搜索健康服务、养生知识...',
    this.showFilterButton = true,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Container(
              height: 44,
              decoration: BoxDecoration(
                color: Theme.of(context).brightness == Brightness.dark
                    ? Colors.grey[800]
                    : Colors.grey[200],
                borderRadius: BorderRadius.circular(22),
              ),
              child: TextField(
                controller: controller,
                onChanged: onChanged,
                onSubmitted: onSubmitted,
                decoration: InputDecoration(
                  hintText: hintText,
                  prefixIcon: const Icon(Icons.search),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
              ),
            ),
          ),
          if (showFilterButton)
            Padding(
              padding: const EdgeInsets.only(left: 8),
              child: Container(
                height: 44,
                width: 44,
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor,
                  borderRadius: BorderRadius.circular(22),
                ),
                child: IconButton(
                  icon: const Icon(
                    Icons.filter_list,
                    color: Colors.white,
                  ),
                  onPressed: onFilterPressed,
                  tooltip: '筛选',
                ),
              ),
            ),
        ],
      ),
    );
  }
} 