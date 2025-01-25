import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/suoke/service_list_bloc.dart';

@RoutePage()
class ServiceListPage extends StatelessWidget {
  final String categoryId;

  const ServiceListPage({
    @PathParam('categoryId') required this.categoryId,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<ServiceListBloc>()
        ..add(ServiceListEvent.started(categoryId)),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('服务列表'),
        ),
        body: BlocBuilder<ServiceListBloc, ServiceListState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (services) => ListView.builder(
                itemCount: services.length,
                itemBuilder: (context, index) {
                  final service = services[index];
                  return ServiceCard(
                    service: service,
                    onTap: () => context.router.push(
                      ServiceDetailRoute(id: service.id),
                    ),
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