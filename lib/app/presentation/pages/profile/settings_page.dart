import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/settings/settings_bloc.dart';

@RoutePage()
class SettingsPage extends StatelessWidget {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<SettingsBloc>()
        ..add(const SettingsEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('设置'),
        ),
        body: BlocBuilder<SettingsBloc, SettingsState>(
          builder: (context, state) {
            return ListView(
              children: [
                ListTile(
                  title: const Text('通知设置'),
                  trailing: Switch(
                    value: state.notificationsEnabled,
                    onChanged: (value) {
                      context.read<SettingsBloc>().add(
                            SettingsEvent.notificationsToggled(value),
                          );
                    },
                  ),
                ),
                ListTile(
                  title: const Text('深色模式'),
                  trailing: Switch(
                    value: state.darkModeEnabled,
                    onChanged: (value) {
                      context.read<SettingsBloc>().add(
                            SettingsEvent.darkModeToggled(value),
                          );
                    },
                  ),
                ),
                ListTile(
                  title: const Text('语言'),
                  trailing: DropdownButton<String>(
                    value: state.language,
                    items: const [
                      DropdownMenuItem(
                        value: 'zh',
                        child: Text('中文'),
                      ),
                      DropdownMenuItem(
                        value: 'en',
                        child: Text('English'),
                      ),
                    ],
                    onChanged: (value) {
                      if (value != null) {
                        context.read<SettingsBloc>().add(
                              SettingsEvent.languageChanged(value),
                            );
                      }
                    },
                  ),
                ),
                ListTile(
                  title: const Text('清除缓存'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    context.read<SettingsBloc>().add(
                          const SettingsEvent.clearCacheRequested(),
                        );
                  },
                ),
                ListTile(
                  title: const Text('退出登录'),
                  trailing: const Icon(Icons.exit_to_app),
                  onTap: () {
                    context.read<SettingsBloc>().add(
                          const SettingsEvent.logoutRequested(),
                        );
                  },
                ),
              ],
            );
          },
        ),
      ),
    );
  }
} 