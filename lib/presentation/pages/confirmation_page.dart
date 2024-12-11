import 'dart:async';
import 'package:flutter/material.dart';
import '../../service/models/confirmation.dart';
import '../../service/services/task_executor_service.dart';
import '../widgets/confirmation_list.dart';

class ConfirmationPage extends StatefulWidget {
  final TaskExecutorService taskExecutor;
  
  const ConfirmationPage({
    super.key,
    required this.taskExecutor,
  });
  
  @override
  State<ConfirmationPage> createState() => _ConfirmationPageState();
}

class _ConfirmationPageState extends State<ConfirmationPage> {
  List<ConfirmationRequest> _requests = [];
  StreamSubscription? _requestSubscription;
  Timer? _refreshTimer;
  
  @override
  void initState() {
    super.initState();
    _loadRequests();
    _setupSubscriptions();
  }
  
  @override
  void dispose() {
    _requestSubscription?.cancel();
    _refreshTimer?.cancel();
    super.dispose();
  }
  
  void _loadRequests() {
    setState(() {
      _requests = widget.taskExecutor.getPendingConfirmations();
    });
  }
  
  void _setupSubscriptions() {
    // 监听新的确认请求
    _requestSubscription = widget.taskExecutor.onConfirmationRequest.listen((request) {
      setState(() {
        _requests.add(request);
      });
    });
    
    // 定期刷新以更新剩余时间显示
    _refreshTimer = Timer.periodic(
      const Duration(seconds: 1),
      (_) => setState(() {}),
    );
  }
  
  void _handleResponse(ConfirmationResponse response) async {
    try {
      await widget.taskExecutor.processConfirmation(response);
      setState(() {
        _requests.removeWhere((r) => r.id == response.requestId);
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              response.approved ? '已批准任务' : '已拒绝任务',
            ),
            backgroundColor: response.approved ? Colors.green : Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('处理确认请求失败：$e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
  
  void _handleCancel(String requestId) async {
    try {
      await widget.taskExecutor.cancelTask(requestId);
      setState(() {
        _requests.removeWhere((r) => r.id == requestId);
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('已取消任务'),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('取消任务失败：$e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('待处理的确认请求'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadRequests,
            tooltip: '刷新',
          ),
        ],
      ),
      body: ConfirmationList(
        requests: _requests,
        onResponse: _handleResponse,
        onCancel: _handleCancel,
      ),
    );
  }
} 