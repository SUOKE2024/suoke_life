import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/profile/device_management_bloc.dart';

@RoutePage()
class DeviceManagementPage extends StatelessWidget {
  const DeviceManagementPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<DeviceManagementBloc>()
        ..add(const DeviceManagementEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('设备管理'),
          actions: [
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: () => context.router.push(const AddDeviceRoute()),
            ),
          ],
        ),
        body: BlocBuilder<DeviceManagementBloc, DeviceManagementState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (devices) => ListView.builder(
                itemCount: devices.length,
                itemBuilder: (context, index) {
                  final device = devices[index];
                  return DeviceCard(
                    device: device,
                    onTap: () => context.router.push(
                      DeviceDetailRoute(id: device.id),
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

class DeviceCard extends StatelessWidget {
  final Device device;
  final VoidCallback onTap;

  const DeviceCard({
    required this.device,
    required this.onTap,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ListTile(
        leading: Icon(
          device.isConnected ? Icons.bluetooth_connected : Icons.bluetooth,
          color: device.isConnected ? Colors.blue : Colors.grey,
        ),
        title: Text(device.name),
        subtitle: Text(device.type),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            switch (value) {
              case 'rename':
                // 重命名设备
                break;
              case 'disconnect':
                // 断开连接
                break;
              case 'remove':
                // 删除设备
                break;
            }
          },
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'rename',
              child: Text('重命名'),
            ),
            const PopupMenuItem(
              value: 'disconnect',
              child: Text('断开连接'),
            ),
            const PopupMenuItem(
              value: 'remove',
              child: Text('删除'),
            ),
          ],
        ),
        onTap: onTap,
      ),
    );
  }
} 