import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/suoke/questionnaire_list_bloc.dart';

@RoutePage()
class QuestionnaireListPage extends StatelessWidget {
  const QuestionnaireListPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<QuestionnaireListBloc>()
        ..add(const QuestionnaireListEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('健康问卷'),
        ),
        body: BlocBuilder<QuestionnaireListBloc, QuestionnaireListState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (questionnaires) => ListView.builder(
                itemCount: questionnaires.length,
                itemBuilder: (context, index) {
                  final questionnaire = questionnaires[index];
                  return Card(
                    margin: const EdgeInsets.all(8),
                    child: ListTile(
                      title: Text(questionnaire.title),
                      subtitle: Text(questionnaire.description),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => context.router.push(
                        QuestionnaireRoute(id: questionnaire.id),
                      ),
                    ),
                  );
                },
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => context.router.push(const QuestionnaireCreateRoute()),
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
} 