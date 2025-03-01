import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:intl/intl.dart';

import '../../../domain/entities/appointment.dart';
import '../../providers/appointment_providers.dart';
import '../../providers/auth_providers.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/error_view.dart';

@RoutePage()
class AppointmentListScreen extends ConsumerStatefulWidget {
  const AppointmentListScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<AppointmentListScreen> createState() => _AppointmentListScreenState();
}

class _AppointmentListScreenState extends ConsumerState<AppointmentListScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadAppointments();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadAppointments() async {
    final authState = ref.read(authStateProvider);
    if (authState.currentUser == null) {
      setState(() {
        _errorMessage = '请先登录';
        _isLoading = false;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 使用Riverpod的Provider加载数据
      await ref.read(appointmentProvider.notifier).getUpcomingAppointments(authState.currentUser!.id);
      await ref.read(appointmentProvider.notifier).getPastAppointments(authState.currentUser!.id);
      
      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '加载预约失败: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final appointmentState = ref.watch(appointmentProvider);
    final upcomingAppointments = appointmentState.upcomingAppointments;
    final pastAppointments = appointmentState.pastAppointments;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的预约'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '即将到来'),
            Tab(text: '历史预约'),
          ],
        ),
      ),
      body: LoadingOverlay(
        isLoading: _isLoading,
        child: _errorMessage != null
            ? ErrorView(
                errorMessage: _errorMessage!,
                onRetry: _loadAppointments,
              )
            : TabBarView(
                controller: _tabController,
                children: [
                  _buildAppointmentList(upcomingAppointments, isUpcoming: true),
                  _buildAppointmentList(pastAppointments, isUpcoming: false),
                ],
              ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // 导航到创建预约页面
          context.router.pushNamed('/appointment/create');
        },
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildAppointmentList(List<Appointment> appointments, {required bool isUpcoming}) {
    if (appointments.isEmpty) {
      return Center(
        child: Text(
          isUpcoming ? '暂无即将到来的预约' : '暂无历史预约',
          style: Theme.of(context).textTheme.titleMedium,
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadAppointments,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: appointments.length,
        itemBuilder: (context, index) {
          final appointment = appointments[index];
          return _buildAppointmentCard(appointment, isUpcoming);
        },
      ),
    );
  }

  Widget _buildAppointmentCard(Appointment appointment, bool isUpcoming) {
    final dateFormat = DateFormat('yyyy年MM月dd日');
    final timeFormat = DateFormat('HH:mm');
    
    // 根据预约状态设置不同的颜色
    Color statusColor;
    switch (appointment.status) {
      case AppointmentStatus.pending:
        statusColor = Colors.orange;
        break;
      case AppointmentStatus.confirmed:
        statusColor = Colors.green;
        break;
      case AppointmentStatus.completed:
        statusColor = Colors.blue;
        break;
      case AppointmentStatus.cancelled:
        statusColor = Colors.red;
        break;
      case AppointmentStatus.expired:
        statusColor = Colors.grey;
        break;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      child: InkWell(
        onTap: () {
          // 导航到预约详情页面
          context.router.pushNamed('/appointment/detail/${appointment.id}');
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      appointment.serviceName,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: statusColor),
                    ),
                    child: Text(
                      _getStatusText(appointment.status),
                      style: TextStyle(color: statusColor, fontSize: 12),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.person, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    appointment.providerName,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.calendar_today, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    dateFormat.format(appointment.appointmentDate),
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.access_time, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    '${timeFormat.format(appointment.startTime)} - ${timeFormat.format(appointment.endTime)}',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
              if (appointment.notes != null && appointment.notes!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.note, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        appointment.notes!,
                        style: Theme.of(context).textTheme.bodySmall,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],
              if (isUpcoming) ...[
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    if (appointment.status == AppointmentStatus.pending ||
                        appointment.status == AppointmentStatus.confirmed)
                      TextButton(
                        onPressed: () => _showCancelDialog(appointment.id),
                        child: const Text('取消预约'),
                      ),
                    if (appointment.status == AppointmentStatus.pending)
                      TextButton(
                        onPressed: () => _confirmAppointment(appointment.id),
                        child: const Text('确认预约'),
                      ),
                    if (appointment.status == AppointmentStatus.confirmed)
                      TextButton(
                        onPressed: () => _showRescheduleDialog(appointment),
                        child: const Text('重新安排'),
                      ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _getStatusText(AppointmentStatus status) {
    switch (status) {
      case AppointmentStatus.pending:
        return '待确认';
      case AppointmentStatus.confirmed:
        return '已确认';
      case AppointmentStatus.completed:
        return '已完成';
      case AppointmentStatus.cancelled:
        return '已取消';
      case AppointmentStatus.expired:
        return '已过期';
    }
  }

  Future<void> _showCancelDialog(String appointmentId) async {
    final reasonController = TextEditingController();
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('取消预约'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('确定要取消这个预约吗？'),
            const SizedBox(height: 16),
            TextField(
              controller: reasonController,
              decoration: const InputDecoration(
                labelText: '取消原因（可选）',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('返回'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('确认取消'),
          ),
        ],
      ),
    );

    if (result == true) {
      setState(() {
        _isLoading = true;
      });
      
      try {
        final success = await ref.read(appointmentProvider.notifier).cancelAppointment(
              appointmentId,
              reason: reasonController.text.isNotEmpty ? reasonController.text : null,
            );
        
        if (success) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('预约已取消')),
            );
          }
        } else {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('取消预约失败')),
            );
          }
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('取消预约失败: $e')),
          );
        }
      } finally {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _confirmAppointment(String appointmentId) async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final success = await ref.read(appointmentProvider.notifier).confirmAppointment(appointmentId);
      
      if (success) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('预约已确认')),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('确认预约失败')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('确认预约失败: $e')),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _showRescheduleDialog(Appointment appointment) async {
    // 这里简化处理，实际应用中应该跳转到重新安排预约的页面
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('重新安排预约'),
        content: const Text('确定要重新安排这个预约吗？这将跳转到重新安排页面。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    if (result == true) {
      // 导航到重新安排预约页面
      if (mounted) {
        context.router.pushNamed('/appointment/reschedule/${appointment.id}');
      }
    }
  }
} 