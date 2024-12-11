import 'package:flutter/material.dart';
import '../../service/models/confirmation.dart';

class ConfirmationDialog extends StatefulWidget {
  final ConfirmationRequest request;
  final Function(ConfirmationResponse) onResponse;
  
  const ConfirmationDialog({
    super.key,
    required this.request,
    required this.onResponse,
  });
  
  @override
  State<ConfirmationDialog> createState() => _ConfirmationDialogState();
}

class _ConfirmationDialogState extends State<ConfirmationDialog> {
  final _reasonController = TextEditingController();
  bool _isApproving = true;
  
  @override
  void dispose() {
    _reasonController.dispose();
    super.dispose();
  }
  
  void _handleResponse(bool approved) {
    final response = ConfirmationResponse(
      requestId: widget.request.id,
      approved: approved,
      reason: _reasonController.text.isEmpty ? null : _reasonController.text,
    );
    widget.onResponse(response);
    Navigator.of(context).pop();
  }
  
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return AlertDialog(
      title: Text('确认${widget.request.action}'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 任务信息
            _buildInfoSection(
              title: '任务类型',
              content: widget.request.taskType,
              icon: Icons.category,
              theme: theme,
            ),
            const SizedBox(height: 8),
            _buildInfoSection(
              title: '发起用户',
              content: widget.request.userId,
              icon: Icons.person,
              theme: theme,
            ),
            const SizedBox(height: 8),
            _buildInfoSection(
              title: '参数',
              content: widget.request.parameters.toString(),
              icon: Icons.settings,
              theme: theme,
            ),
            const SizedBox(height: 8),
            _buildInfoSection(
              title: '过期时间',
              content: widget.request.expireTime.toString(),
              icon: Icons.timer,
              theme: theme,
            ),
            const SizedBox(height: 16),
            
            // 操作选择
            Row(
              children: [
                Icon(
                  _isApproving ? Icons.check_circle : Icons.cancel,
                  color: _isApproving ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  _isApproving ? '批准' : '拒绝',
                  style: theme.textTheme.titleMedium,
                ),
                const Spacer(),
                Switch(
                  value: _isApproving,
                  onChanged: (value) => setState(() => _isApproving = value),
                  activeColor: Colors.green,
                  inactiveTrackColor: Colors.red.withOpacity(0.5),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // 原因输入
            TextField(
              controller: _reasonController,
              decoration: InputDecoration(
                labelText: _isApproving ? '批准原因（可选）' : '拒绝原因',
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.comment),
              ),
              maxLines: 2,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('取消'),
        ),
        ElevatedButton(
          onPressed: () => _handleResponse(_isApproving),
          style: ElevatedButton.styleFrom(
            backgroundColor: _isApproving ? Colors.green : Colors.red,
            foregroundColor: Colors.white,
          ),
          child: Text(_isApproving ? '批准' : '拒绝'),
        ),
      ],
    );
  }
  
  Widget _buildInfoSection({
    required String title,
    required String content,
    required IconData icon,
    required ThemeData theme,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: theme.textTheme.titleSmall?.copyWith(
                  color: theme.colorScheme.primary,
                ),
              ),
              Text(
                content,
                style: theme.textTheme.bodyMedium,
              ),
            ],
          ),
        ),
      ],
    );
  }
} 