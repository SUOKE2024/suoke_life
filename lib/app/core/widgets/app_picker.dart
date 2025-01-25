/// 选择器组件
class AppPicker<T> extends StatelessWidget {
  final String title;
  final List<T> items;
  final T? value;
  final ValueChanged<T>? onChanged;
  final String Function(T) itemText;
  final Widget Function(T)? itemBuilder;
  final bool showSearchBar;
  final String? searchHint;
  final bool showDivider;

  const AppPicker({
    super.key,
    required this.title,
    required this.items,
    this.value,
    this.onChanged,
    required this.itemText,
    this.itemBuilder,
    this.showSearchBar = false,
    this.searchHint,
    this.showDivider = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.7,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 标题栏
          Container(
            padding: AppStyles.padding,
            child: Row(
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
          ),
          if (showDivider) const Divider(height: 1),
          // 搜索栏
          if (showSearchBar)
            AppSearchBar(
              hint: searchHint ?? '搜索',
              margin: AppStyles.paddingSmall,
              onChanged: (text) {
                // TODO: 实现搜索过滤
              },
            ),
          // 列表内容
          Flexible(
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: items.length,
              itemBuilder: (context, index) {
                final item = items[index];
                return ListTile(
                  title: itemBuilder?.call(item) ?? Text(itemText(item)),
                  selected: item == value,
                  trailing: item == value
                      ? const Icon(Icons.check, color: AppColors.primary)
                      : null,
                  onTap: () {
                    onChanged?.call(item);
                    Navigator.of(context).pop();
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  /// 显��选择器
  static Future<T?> show<T>({
    required BuildContext context,
    required String title,
    required List<T> items,
    T? value,
    ValueChanged<T>? onChanged,
    required String Function(T) itemText,
    Widget Function(T)? itemBuilder,
    bool showSearchBar = false,
    String? searchHint,
    bool showDivider = true,
  }) {
    return showModalBottomSheet<T>(
      context: context,
      builder: (_) => AppPicker<T>(
        title: title,
        items: items,
        value: value,
        onChanged: onChanged,
        itemText: itemText,
        itemBuilder: itemBuilder,
        showSearchBar: showSearchBar,
        searchHint: searchHint,
        showDivider: showDivider,
      ),
    );
  }
} 