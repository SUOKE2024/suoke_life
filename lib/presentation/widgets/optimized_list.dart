class OptimizedList extends StatelessWidget {
  final List<Item> items;
  
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        return AutomaticKeepAliveClient(
          child: ItemWidget(item: items[index]),
        );
      },
      cacheExtent: 100.0,
    );
  }
} 