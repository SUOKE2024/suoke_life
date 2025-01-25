import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/life/record_edit_bloc.dart';

@RoutePage()
class RecordEditPage extends StatelessWidget {
  final String? id;

  const RecordEditPage({
    @PathParam('id') this.id,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final titleController = TextEditingController();
    final contentController = TextEditingController();

    return BlocProvider(
      create: (context) => context.read<RecordEditBloc>()
        ..add(RecordEditEvent.started(id)),
      child: BlocConsumer<RecordEditBloc, RecordEditState>(
        listener: (context, state) {
          state.maybeWhen(
            success: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('保存成功')),
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
          return Scaffold(
            appBar: AppBar(
              title: Text(id == null ? '新建记录' : '编辑记录'),
              actions: [
                TextButton(
                  onPressed: state.maybeWhen(
                    loading: () => null,
                    orElse: () => () {
                      if (titleController.text.isNotEmpty &&
                          contentController.text.isNotEmpty) {
                        context.read<RecordEditBloc>().add(
                              RecordEditEvent.saved(
                                title: titleController.text,
                                content: contentController.text,
                              ),
                            );
                      }
                    },
                  ),
                  child: state.maybeWhen(
                    loading: () => const CircularProgressIndicator(),
                    orElse: () => const Text('保存'),
                  ),
                ),
              ],
            ),
            body: state.maybeWhen(
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (record) {
                titleController.text = record?.title ?? '';
                contentController.text = record?.content ?? '';
                return SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      TextField(
                        controller: titleController,
                        decoration: const InputDecoration(
                          labelText: '标题',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: contentController,
                        maxLines: 10,
                        decoration: const InputDecoration(
                          labelText: '内容',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () {
                          // 处理添加图片
                        },
                        icon: const Icon(Icons.add_photo_alternate),
                        label: const Text('添加图片'),
                      ),
                    ],
                  ),
                );
              },
              orElse: () => const SizedBox(),
            ),
          );
        },
      ),
    );
  }
} 