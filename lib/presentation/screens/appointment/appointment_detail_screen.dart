import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:intl/intl.dart';

import '../../../domain/entities/appointment.dart';
import '../../providers/appointment_providers.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/error_view.dart';

@RoutePage()
class AppointmentDetailScreen extends ConsumerStatefulWidget {
  final String appointmentId;

  const AppointmentDetailScreen({
    Key? key,
    @PathParam('id') required this.appointmentId,
  }) : super(key: key);

  @override
  ConsumerState<AppointmentDetailScreen> createState() => _AppointmentDetailScreenState();
}

class _AppointmentDetailScreenState extends ConsumerState<AppointmentDetailScreen> {
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadAppointmentDetails();
  }

  Future<void> _loadAppointmentDetails() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await ref.read(appointmentProvider.notifier).getAppointmentById(widget.appointmentId);
      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '加载预约详情失败: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final appointmentState = ref.watch(appointmentProvider);
    final appointment = appointmentState.selectedAppointment;

    return Scaffold(
      appBar: AppBar(
        title: const Text('预约详情'),
        actions: [
          if (appointment != null &&
              (appointment.status == AppointmentStatus.pending ||
                  appointment.status == AppointmentStatus.confirmed))
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () {
                // 导航到编辑预约页面
                context.router.pushNamed('/appointment/edit/${appointment.id}');
              },
            ),
        ],
      ),
      body: LoadingOverlay(
        isLoading: _isLoading,
        child: _errorMessage != null
            ? ErrorView(
                errorMessage: _errorMessage!,
                onRetry: _loadAppointmentDetails,
              )
            : appointment == null
                ? const Center(child: Text('未找到预约信息'))
                : _buildAppointmentDetails(appointment),
      ),
    );
  }

  Widget _buildAppointmentDetails(Appointment appointment) {
    final dateFormat = DateFormat('yyyy年MM月dd日');
    final timeFormat = DateFormat('HH:mm');
    final dateTimeFormat = DateFormat('yyyy年MM月dd日 HH:mm');

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

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 预约状态卡片
          Card(
            elevation: 2,
            color: statusColor.withOpacity(0.1),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
              side: BorderSide(color: statusColor),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    _getStatusIcon(appointment.status),
                    color: statusColor,
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _getStatusText(appointment.status),
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: statusColor,
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _getStatusDescription(appointment.status),
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: statusColor,
                              ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 预约信息卡片
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '预约信息',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const Divider(),
                  _buildInfoRow(
                    context,
                    '服务项目',
                    appointment.serviceName,
                    Icons.medical_services,
                  ),
                  _buildInfoRow(
                    context,
                    '服务提供者',
                    appointment.providerName,
                    Icons.person,
                  ),
                  _buildInfoRow(
                    context,
                    '预约日期',
                    dateFormat.format(appointment.appointmentDate),
                    Icons.calendar_today,
                  ),
                  _buildInfoRow(
                    context,
                    '预约时间',
                    '${timeFormat.format(appointment.startTime)} - ${timeFormat.format(appointment.endTime)}',
                    Icons.access_time,
                  ),
                  _buildInfoRow(
                    context,
                    '服务时长',
                    '${appointment.getDurationInMinutes()}分钟',
                    Icons.timelapse,
                  ),
                  _buildInfoRow(
                    context,
                    '服务费用',
                    '¥${appointment.price.toStringAsFixed(2)}',
                    Icons.payment,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 备注卡片
          if (appointment.notes != null && appointment.notes!.isNotEmpty)
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '备注',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const Divider(),
                    Text(
                      appointment.notes!,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
          if (appointment.notes != null && appointment.notes!.isNotEmpty)
            const SizedBox(height: 16),

          // 预约记录卡片
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '预约记录',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const Divider(),
                  _buildInfoRow(
                    context,
                    '创建时间',
                    dateTimeFormat.format(appointment.createdAt),
                    Icons.create,
                  ),
                  _buildInfoRow(
                    context,
                    '最后更新',
                    dateTimeFormat.format(appointment.updatedAt),
                    Icons.update,
                  ),
                  _buildInfoRow(
                    context,
                    '预约编号',
                    appointment.id,
                    Icons.tag,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 操作按钮
          if (appointment.status == AppointmentStatus.pending ||
              appointment.status == AppointmentStatus.confirmed) ...[
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _showCancelDialog(appointment.id),
                    icon: const Icon(Icons.cancel),
                    label: const Text('取消预约'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: appointment.status == AppointmentStatus.pending
                        ? () => _confirmAppointment(appointment.id)
                        : () => _showRescheduleDialog(appointment),
                    icon: Icon(appointment.status == AppointmentStatus.pending
                        ? Icons.check_circle
                        : Icons.edit_calendar),
                    label: Text(appointment.status == AppointmentStatus.pending
                        ? '确认预约'
                        : '重新安排'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: appointment.status == AppointmentStatus.pending
                          ? Colors.green
                          : Colors.blue,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (appointment.status == AppointmentStatus.confirmed)
              ElevatedButton.icon(
                onPressed: () => _sendReminder(appointment.id),
                icon: const Icon(Icons.notifications),
                label: const Text('发送提醒'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
          ],

          // 已完成预约的评价按钮
          if (appointment.status == AppointmentStatus.completed && !appointment.hasReviewed)
            ElevatedButton.icon(
              onPressed: () {
                // 导航到评价页面
                context.router.pushNamed('/appointment/review/${appointment.id}');
              },
              icon: const Icon(Icons.star),
              label: const Text('评价服务'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.amber,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(BuildContext context, String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 8),
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getStatusIcon(AppointmentStatus status) {
    switch (status) {
      case AppointmentStatus.pending:
        return Icons.pending;
      case AppointmentStatus.confirmed:
        return Icons.check_circle;
      case AppointmentStatus.completed:
        return Icons.done_all;
      case AppointmentStatus.cancelled:
        return Icons.cancel;
      case AppointmentStatus.expired:
        return Icons.timer_off;
    }
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

  String _getStatusDescription(AppointmentStatus status) {
    switch (status) {
      case AppointmentStatus.pending:
        return '您的预约正在等待确认，请耐心等待';
      case AppointmentStatus.confirmed:
        return '您的预约已确认，请按时到达';
      case AppointmentStatus.completed:
        return '您的预约已完成，感谢您的使用';
      case AppointmentStatus.cancelled:
        return '您的预约已取消';
      case AppointmentStatus.expired:
        return '您的预约已过期';
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
            // 重新加载预约详情
            _loadAppointmentDetails();
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
          // 重新加载预约详情
          _loadAppointmentDetails();
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

  Future<void> _sendReminder(String appointmentId) async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final success = await ref.read(appointmentProvider.notifier).sendAppointmentReminder(appointmentId);
      
      if (success) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('提醒已发送')),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('发送提醒失败')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送提醒失败: $e')),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}