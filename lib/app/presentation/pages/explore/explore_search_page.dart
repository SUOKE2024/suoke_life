import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/explore/explore_bloc.dart';
import '../../blocs/explore/explore_event.dart';
import '../../blocs/explore/explore_state.dart';

@RoutePage()
class ExploreSearchPage extends StatefulWidget {
  const ExploreSearchPage({Key? key}) : super(key: key);

  @override
  State<ExploreSearchPage> createState() => _ExploreSearchPageState();
}

class _ExploreSearchPageState extends State<ExploreSearchPage> {
  final _searchController = TextEditingController();
  
  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: _searchController,
          decoration: const InputDecoration(
            hintText: '搜索...',
            border: InputBorder.none,
          ),
          onSubmitted: (query) {
            if (query.isNotEmpty) {
              context.read<ExploreBloc>().add(SearchExploreEvent(query));
            }
          },
        ),
      ),
      body: BlocBuilder<ExploreBloc, ExploreState>(
        builder: (context, state) {
          if (state is ExploreLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          
          if (state is ExploreLoaded) {
            return ListView.builder(
              itemCount: state.items.length,
              itemBuilder: (context, index) {
                final item = state.items[index];
                return ListTile(
                  leading: Image.network(
                    item.imageUrl,
                    width: 56,
                    height: 56,
                    fit: BoxFit.cover,
                  ),
                  title: Text(item.title),
                  subtitle: Text(
                    item.description,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  onTap: () {
                    // 导航到详情页
                  },
                );
              },
            );
          }
          
          if (state is ExploreError) {
            return Center(child: Text(state.message));
          }

          return const Center(child: Text('开始搜索'));
        },
      ),
    );
  }
} 