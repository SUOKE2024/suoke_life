import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/profile/legal_document_bloc.dart';

@RoutePage()
class UserAgreementPage extends StatelessWidget {
  const UserAgreementPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<LegalDocumentBloc>()
        ..add(const LegalDocumentEvent.userAgreementRequested()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('用户协议'),
        ),
        body: BlocBuilder<LegalDocumentBloc, LegalDocumentState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (content) => SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Text(content),
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
      ),
    );
  }
} 