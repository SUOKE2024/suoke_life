import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/profile/history_bloc.dart';

@RoutePage()
class HistoryPage extends StatelessWidget {
  const HistoryPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<HistoryBloc>()
        ..add(const HistoryEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('历史记录'),
          actions: [
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: () {
                context.read<HistoryBloc>().add(
                      const HistoryEvent.clearRequested(),
                    );
              },
            ),
          ],
        ),
        body: BlocBuilder<HistoryBloc, HistoryState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (records) => ListView.builder(
                itemCount: records.length,
                itemBuilder: (context, index) {
                  final record = records[index];
                  return ListTile(
                    leading: Icon(
                      record.type == 'chat' ? Icons.chat : Icons.search,
                    ),
                    title: Text(record.title),
                    subtitle: Text(record.timestamp.toString()),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete),
                      onPressed: () {
                        context.read<HistoryBloc>().add(
                              HistoryEvent.recordDeleted(record.id),
                            );
                      },
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