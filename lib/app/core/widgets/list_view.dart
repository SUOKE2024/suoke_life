/// 列表组件
class AppListView extends StatelessWidget {
  final List<ListItem> items;
  final bool showDivider;
  final EdgeInsets? padding;
  final ScrollController? controller;
  final Widget? emptyWidget;
  final Widget? loadingWidget;
  final bool isLoading;
  final bool hasMore;
  final VoidCallback? onLoadMore;
  final Widget Function(BuildContext, ListItem)? itemBuilder;

  const AppListView({
    super.key,
    required this.items,
    this.showDivider = true,
    this.padding,
    this.controller,
    this.emptyWidget,
    this.loadingWidget,
    this.isLoading = false,
    this.hasMore = false,
    this.onLoadMore,
    this.itemBuilder,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading && items.isEmpty) {
      return loadingWidget ?? const Center(child: CircularProgressIndicator());
    }

    if (items.isEmpty) {
      return emptyWidget ??
          const Center(
            child: Text('暂无数据'),
          );
    }

    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification is ScrollEndNotification) {
          if (notification.metrics.pixels >= notification.metrics.maxScrollExtent) {
            if (hasMore && !isLoading) {
              onLoadMore?.call();
            }
          }
        }
        return false;
      },
      child: ListView.separated(
        controller: controller,
        padding: padding,
        itemCount: items.length + (hasMore ? 1 : 0),
        separatorBuilder: (_, __) =>
            showDivider ? const Divider(height: 1) : const SizedBox(),
        itemBuilder: (context, index) {
          if (index == items.length) {
            return Container(
              padding: const EdgeInsets.all(16),
              alignment: Alignment.center,
              child: isLoading
                  ? const CircularProgressIndicator()
                  : const Text('加载更多...'),
            );
          }

          final item = items[index];
          if (itemBuilder != null) {
            return itemBuilder!(context, item);
          }

          return ListTile(
            leading: item.leading,
            title: Text(item.title),
            subtitle: item.subtitle != null ? Text(item.subtitle!) : null,
            trailing: item.trailing,
            onTap: item.onTap,
          );
        },
      ),
    );
  }
}

/// 列表项
class ListItem {
  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;

  const ListItem({
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
  });
} 