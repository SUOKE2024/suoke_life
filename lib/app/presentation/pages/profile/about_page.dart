import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/profile/about_bloc.dart';

@RoutePage()
class AboutPage extends StatelessWidget {
  const AboutPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<AboutBloc>()
        ..add(const AboutEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('关于'),
        ),
        body: BlocBuilder<AboutBloc, AboutState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (info) => SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Image.asset(
                      'assets/images/logo.png',
                      width: 120,
                      height: 120,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      info.appName,
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                    Text(
                      'Version ${info.version}',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 32),
                    _buildMenuItem(
                      context,
                      '用户协议',
                      () => context.router.push(const UserAgreementRoute()),
                    ),
                    _buildMenuItem(
                      context,
                      '隐私政策',
                      () => context.router.push(const PrivacyPolicyRoute()),
                    ),
                    _buildMenuItem(
                      context,
                      '开源许可',
                      () => context.router.push(const LicensesRoute()),
                    ),
                    _buildMenuItem(
                      context,
                      '检查更新',
                      () {
                        context.read<AboutBloc>().add(
                              const AboutEvent.checkUpdateRequested(),
                            );
                      },
                    ),
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

  Widget _buildMenuItem(
    BuildContext context,
    String title,
    VoidCallback onTap,
  ) {
    return ListTile(
      title: Text(title),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
} 