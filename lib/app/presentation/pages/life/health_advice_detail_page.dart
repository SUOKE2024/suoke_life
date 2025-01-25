import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/life/health_advice_detail_bloc.dart';

@RoutePage()
class HealthAdviceDetailPage extends StatelessWidget {
  final String id;

  const HealthAdviceDetailPage({
    @PathParam('id') required this.id,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<HealthAdviceDetailBloc>()
        ..add(HealthAdviceDetailEvent.started(id)),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('健康建议详情'),
          actions: [
            BlocBuilder<HealthAdviceDetailBloc, HealthAdviceDetailState>(
              builder: (context, state) {
                return state.maybeWhen(
                  loaded: (advice) => IconButton(
                    icon: Icon(
                      advice.isFavorite ? Icons.favorite : Icons.favorite_border,
                    ),
                    onPressed: () {
                      context.read<HealthAdviceDetailBloc>().add(
                            const HealthAdviceDetailEvent.favoriteToggled(),
                          );
                    },
                  ),
                  orElse: () => const SizedBox(),
                );
              },
            ),
          ],
        ),
        body: BlocBuilder<HealthAdviceDetailBloc, HealthAdviceDetailState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (advice) => SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      advice.title,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      advice.content,
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    if (advice.recommendations.isNotEmpty) ...[
                      const SizedBox(height: 24),
                      Text(
                        '相关建议',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      ...advice.recommendations.map((recommendation) {
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            title: Text(recommendation.title),
                            subtitle: Text(recommendation.description),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () => context.router.push(
                              HealthAdviceDetailRoute(id: recommendation.id),
                            ),
                          ),
                        );
                      }),
                    ],
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