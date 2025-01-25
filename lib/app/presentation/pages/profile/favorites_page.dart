import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/profile/favorites_bloc.dart';

@RoutePage()
class FavoritesPage extends StatelessWidget {
  const FavoritesPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<FavoritesBloc>()
        ..add(const FavoritesEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('我的收藏'),
        ),
        body: BlocBuilder<FavoritesBloc, FavoritesState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (items) => ListView.builder(
                itemCount: items.length,
                itemBuilder: (context, index) {
                  final item = items[index];
                  return ListTile(
                    leading: Icon(_getIconForType(item.type)),
                    title: Text(item.title),
                    subtitle: Text(item.description),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete),
                      onPressed: () {
                        context.read<FavoritesBloc>().add(
                              FavoritesEvent.itemRemoved(item.id),
                            );
                      },
                    ),
                    onTap: () => _navigateToDetail(context, item),
                  );
                },
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
      ),
    );
  }

  IconData _getIconForType(String type) {
    switch (type) {
      case 'article':
        return Icons.article;
      case 'service':
        return Icons.medical_services;
      case 'topic':
        return Icons.explore;
      default:
        return Icons.bookmark;
    }
  }

  void _navigateToDetail(BuildContext context, FavoriteItem item) {
    switch (item.type) {
      case 'article':
        context.router.push(ArticleDetailRoute(id: item.id));
        break;
      case 'service':
        context.router.push(ServiceDetailRoute(id: item.id));
        break;
      case 'topic':
        context.router.push(TopicDetailRoute(id: item.id));
        break;
    }
  }
} 