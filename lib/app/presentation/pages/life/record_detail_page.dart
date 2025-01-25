import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/life/record_detail_bloc.dart';

@RoutePage()
class RecordDetailPage extends StatelessWidget {
  final String id;

  const RecordDetailPage({
    @PathParam('id') required this.id,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<RecordDetailBloc>()
        ..add(RecordDetailEvent.started(id)),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('记录详情'),
          actions: [
            BlocBuilder<RecordDetailBloc, RecordDetailState>(
              builder: (context, state) {
                return state.maybeWhen(
                  loaded: (record) => PopupMenuButton<String>(
                    onSelected: (value) {
                      switch (value) {
                        case 'edit':
                          context.router.push(
                            RecordEditRoute(id: record.id),
                          );
                          break;
                        case 'delete':
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: const Text('确认删除'),
                              content: const Text('确定要删除这条记录吗？'),
                              actions: [
                                TextButton(
                                  onPressed: () => context.router.pop(),
                                  child: const Text('取消'),
                                ),
                                TextButton(
                                  onPressed: () {
                                    context.read<RecordDetailBloc>().add(
                                          const RecordDetailEvent.deleteRequested(),
                                        );
                                    context.router.pop();
                                  },
                                  child: const Text('删除'),
                                ),
                              ],
                            ),
                          );
                          break;
                      }
                    },
                    itemBuilder: (context) => [
                      const PopupMenuItem(
                        value: 'edit',
                        child: Text('编辑'),
                      ),
                      const PopupMenuItem(
                        value: 'delete',
                        child: Text('删除'),
                      ),
                    ],
                  ),
                  orElse: () => const SizedBox(),
                );
              },
            ),
          ],
        ),
        body: BlocConsumer<RecordDetailBloc, RecordDetailState>(
          listener: (context, state) {
            state.maybeWhen(
              deleted: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('记录已删除')),
                );
                context.router.pop();
              },
              error: (message) => ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(message)),
              ),
              orElse: () {},
            );
          },
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (record) => SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      record.title,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      record.date,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      record.content,
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    if (record.images.isNotEmpty) ...[
                      const SizedBox(height: 16),
                      GridView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        gridDelegate:
                            const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 3,
                          crossAxisSpacing: 8,
                          mainAxisSpacing: 8,
                        ),
                        itemCount: record.images.length,
                        itemBuilder: (context, index) {
                          return GestureDetector(
                            onTap: () {
                              // 处理图片预览
                            },
                            child: Image.network(
                              record.images[index],
                              fit: BoxFit.cover,
                            ),
                          );
                        },
                      ),
                    ],
                  ],
                ),
              ),
              deleted: () => const SizedBox(),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
      ),
    );
  }
} 