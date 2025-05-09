import 'package:flutter/material.dart';

/// 建议回复选择回调
typedef SuggestedResponseCallback = void Function(String response);

/// 建议回复组件
class SuggestedResponses extends StatelessWidget {
  /// 建议回复列表
  final List<String> suggestions;
  
  /// 选择回复回调
  final SuggestedResponseCallback onResponseSelected;
  
  /// 主题色
  final Color themeColor;

  /// 构造函数
  const SuggestedResponses({
    Key? key,
    required this.suggestions,
    required this.onResponseSelected,
    required this.themeColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (suggestions.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      width: double.infinity,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(
          children: suggestions.map((suggestion) => _buildSuggestionChip(suggestion)).toList(),
        ),
      ),
    );
  }

  /// 构建建议回复气泡
  Widget _buildSuggestionChip(String suggestion) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        onTap: () => onResponseSelected(suggestion),
        borderRadius: BorderRadius.circular(18),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: themeColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: themeColor.withOpacity(0.3)),
          ),
          child: Text(
            suggestion,
            style: TextStyle(
              color: themeColor,
              fontSize: 14,
            ),
          ),
        ),
      ),
    );
  }
} 