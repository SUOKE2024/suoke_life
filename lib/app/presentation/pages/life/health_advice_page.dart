import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/life/health_advice_bloc.dart';

@RoutePage()
class HealthAdvicePage extends StatelessWidget {
  const HealthAdvicePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<HealthAdviceBloc>()
        ..add(const HealthAdviceEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('健康建议'),
        ),
        body: BlocBuilder<HealthAdviceBloc, HealthAdviceState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (advices) => ListView.builder(
                itemCount: advices.length,
                itemBuilder: (context, index) {
                  final advice = advices[index];
                  return Card(
                    margin: const EdgeInsets.all(8),
                    child: ListTile(
                      title: Text(advice.title),
                      subtitle: Text(advice.content),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => context.router.push(
                        HealthAdviceDetailRoute(id: advice.id),
                      ),
                    ),
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
} 