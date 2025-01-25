import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/help/feedback_bloc.dart';

@RoutePage()
class FeedbackPage extends StatelessWidget {
  const FeedbackPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final contentController = TextEditingController();
    final contactController = TextEditingController();

    return BlocProvider(
      create: (context) => context.read<FeedbackBloc>(),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('意见反馈'),
        ),
        body: BlocConsumer<FeedbackBloc, FeedbackState>(
          listener: (context, state) {
            state.maybeWhen(
              success: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('反馈提交成功')),
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
            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextField(
                    controller: contentController,
                    maxLines: 5,
                    decoration: const InputDecoration(
                      labelText: '反馈内容',
                      hintText: '请描述您的问题或建议...',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: contactController,
                    decoration: const InputDecoration(
                      labelText: '联系方式',
                      hintText: '请留下您的联系方式（选填）',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: state.maybeWhen(
                      loading: () => null,
                      orElse: () => () {
                        if (contentController.text.isNotEmpty) {
                          context.read<FeedbackBloc>().add(
                                FeedbackEvent.submitted(
                                  content: contentController.text,
                                  contact: contactController.text,
                                ),
                              );
                        }
                      },
                    ),
                    child: state.maybeWhen(
                      loading: () => const CircularProgressIndicator(),
                      orElse: () => const Text('提交反馈'),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
} 