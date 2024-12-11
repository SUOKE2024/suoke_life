/// 列表刷新组件
class RefreshList extends StatelessWidget {
  final Future<void> Function() onRefresh;
  final Future<void> Function()? onLoadMore;
  final List<Widget> children;
  final bool loading;
  final bool hasMore;
  final String? emptyMessage;
  final ScrollController? controller;
  final EdgeInsets? padding;

  const RefreshList({
    super.key,
    required this.onRefresh,
    this.onLoadMore,
    required this.children,
    this.loading = false,
    this.hasMore = false,
    this.emptyMessage,
    this.controller,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    if (children.isEmpty && !loading) {
      return EmptyView(
        message: emptyMessage ?? '暂无数据',
        onAction: onRefresh,
        actionText: '刷新',
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: ListView.builder(
        controller: controller,
        padding: padding,
        itemCount: children.length + (loading || hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == children.length) {
            if (loading) {
              return const Center(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: CircularProgressIndicator(),
                ),
              );
            }
            if (hasMore) {
              return Center(
                child: TextButton(
                  onPressed: onLoadMore,
                  child: const Text('加载更多'),
                ),
              );
            }
          }
          return children[index];
        },
      ),
    );
  }
} 