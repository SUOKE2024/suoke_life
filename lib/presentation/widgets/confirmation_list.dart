import 'package:flutter/material.dart';
import '../../service/models/confirmation.dart';
import 'confirmation_dialog.dart';

class ConfirmationList extends StatelessWidget {
  final List<ConfirmationRequest> requests;
  final Function(ConfirmationResponse) onResponse;
  final Function(String)? onCancel;
  
  const ConfirmationList({
    super.key,
    required this.requests,
    required this.onResponse,
    this.onCancel,
  });
  
  void _showConfirmationDialog(BuildContext context, ConfirmationRequest request) {
    showDialog(
      context: context,
      builder: (context) => ConfirmationDialog(
        request: request,
        onResponse: onResponse,
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    if (requests.isEmpty) {
      return const Center(
        child: Text('没有待处理的确认请求'),
      );
    }
    
    return ListView.builder(
      itemCount: requests.length,
      itemBuilder: (context, index) {
        final request = requests[index];
        final remainingTime = request.expireTime.difference(DateTime.now());
        
        return Card(
          margin: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 8,
          ),
          child: ListTile(
            leading: _buildStatusIcon(request.status),
            title: Text(request.action),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(request.taskType),
                if (!request.isExpired)
                  Text(
                    '剩余时间: ${_formatDuration(remainingTime)}',
                    style: TextStyle(
                      color: remainingTime.inMinutes < 1 ? 
                          Colors.red : 
                          Colors.green,
                    ),
                  ),
              ],
            ),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (!request.isExpired) ...[
                  IconButton(
                    icon: const Icon(Icons.check_circle),
                    color: Colors.green,
                    onPressed: () => _showConfirmationDialog(context, request),
                    tooltip: '处理',
                  ),
                  if (onCancel != null)
                    IconButton(
                      icon: const Icon(Icons.cancel),
                      color: Colors.red,
                      onPressed: () => onCancel!(request.id),
                      tooltip: '取消',
                    ),
                ],
              ],
            ),
            onTap: request.isExpired ? 
                null : 
                () => _showConfirmationDialog(context, request),
          ),
        );
      },
    );
  }
  
  Widget _buildStatusIcon(ConfirmationStatus status) {
    IconData icon;
    Color color;
    
    switch (status) {
      case ConfirmationStatus.pending:
        icon = Icons.pending;
        color = Colors.orange;
        break;
      case ConfirmationStatus.approved:
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case ConfirmationStatus.rejected:
        icon = Icons.cancel;
        color = Colors.red;
        break;
      case ConfirmationStatus.expired:
        icon = Icons.timer_off;
        color = Colors.grey;
        break;
      case ConfirmationStatus.cancelled:
        icon = Icons.block;
        color = Colors.grey;
        break;
    }
    
    return Icon(icon, color: color);
  }
  
  String _formatDuration(Duration duration) {
    if (duration.isNegative) {
      return '已过期';
    }
    
    final minutes = duration.inMinutes;
    final seconds = duration.inSeconds % 60;
    
    if (minutes > 0) {
      return '$minutes分${seconds}秒';
    }
    return '$seconds秒';
  }
} 