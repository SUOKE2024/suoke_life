import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/explore/topic_detail_bloc.dart';

@RoutePage()
class TopicDetailPage extends StatelessWidget {
  final String id;

  const TopicDetailPage({
    @PathParam('id') required this.id,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<TopicDetailBloc>()
        ..add(TopicDetailEvent.started(id)),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('主题详情'),
        ),
        body: BlocBuilder<TopicDetailBloc, TopicDetailState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (topic) => SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      topic.title,
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      topic.description,
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    const SizedBox(height: 24),
                    Wrap(
                      spacing: 8,
                      children: topic.tags.map((tag) {
                        return Chip(label: Text(tag));
                      }).toList(),
                    ),
                  ],
                ),
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
      ),
    );
  }
} 