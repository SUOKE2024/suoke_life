import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/suoke/tcm_test_bloc.dart';

@RoutePage()
class TCMTestPage extends StatelessWidget {
  const TCMTestPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<TCMTestBloc>()
        ..add(const TCMTestEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('中医体质检测'),
        ),
        body: BlocBuilder<TCMTestBloc, TCMTestState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('开始检测')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (questions, currentIndex) => Column(
                children: [
                  LinearProgressIndicator(
                    value: (currentIndex + 1) / questions.length,
                  ),
                  Expanded(
                    child: PageView.builder(
                      itemCount: questions.length,
                      controller: PageController(initialPage: currentIndex),
                      physics: const NeverScrollableScrollPhysics(),
                      itemBuilder: (context, index) {
                        final question = questions[index];
                        return QuestionCard(
                          question: question,
                          onAnswered: (answer) {
                            context.read<TCMTestBloc>().add(
                              TCMTestEvent.questionAnswered(answer),
                            );
                          },
                        );
                      },
                    ),
                  ),
                ],
              ),
              completed: (result) => TCMResultView(result: result),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
      ),
    );
  }
} 