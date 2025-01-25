import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/profile/licenses_bloc.dart';

@RoutePage()
class LicensesPage extends StatelessWidget {
  const LicensesPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<LicensesBloc>()
        ..add(const LicensesEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('开源许可'),
        ),
        body: BlocBuilder<LicensesBloc, LicensesState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (licenses) => ListView.builder(
                itemCount: licenses.length,
                itemBuilder: (context, index) {
                  final license = licenses[index];
                  return ExpansionTile(
                    title: Text(license.packageName),
                    subtitle: Text(license.version),
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(license.licenseText),
                      ),
                    ],
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