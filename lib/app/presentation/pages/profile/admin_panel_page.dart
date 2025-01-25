import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/profile/admin_panel_bloc.dart';

@RoutePage()
class AdminPanelPage extends StatelessWidget {
  const AdminPanelPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<AdminPanelBloc>()
        ..add(const AdminPanelEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('管理员面板'),
        ),
        body: BlocBuilder<AdminPanelBloc, AdminPanelState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (data) => ListView(
                children: [
                  _buildSection(
                    title: '专家审核',
                    count: data.pendingExperts,
                    onTap: () => context.router.push(const ExpertReviewRoute()),
                  ),
                  _buildSection(
                    title: '服务审核',
                    count: data.pendingServices,
                    onTap: () => context.router.push(const ServiceReviewRoute()),
                  ),
                  _buildSection(
                    title: '产品审核',
                    count: data.pendingProducts,
                    onTap: () => context.router.push(const ProductReviewRoute()),
                  ),
                  _buildSection(
                    title: 'API管理',
                    onTap: () => context.router.push(const APIManagementRoute()),
                  ),
                  _buildSection(
                    title: '大模型管理',
                    onTap: () => context.router.push(const ModelManagementRoute()),
                  ),
                  _buildSection(
                    title: '系统设置',
                    onTap: () => context.router.push(const SystemSettingsRoute()),
                  ),
                ],
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
      ),
    );
  }

  Widget _buildSection({
    required String title,
    int? count,
    required VoidCallback onTap,
  }) {
    return ListTile(
      title: Text(title),
      trailing: count != null
          ? Badge(
              label: Text(count.toString()),
              child: const Icon(Icons.chevron_right),
            )
          : const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
} 