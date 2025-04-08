import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/blockchain/blockchain_service.dart';
import 'package:suoke_life/di/providers.dart';

/// 健康记录列表状态提供者
final healthRecordsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final service = ref.watch(blockchainServiceProvider);
  final recordCount = await service.getUserRecordCount();
  
  final records = <Map<String, dynamic>>[];
  
  for (int i = 0; i < recordCount; i++) {
    final recordId = await service.getRecordIdAtIndex(i);
    final record = await service.getHealthRecord(recordId);
    
    records.add({
      'id': recordId,
      ...record,
    });
  }
  
  return records;
});

/// 健康记录创建状态提供者
final createRecordStateProvider = StateProvider<AsyncValue<void>>((ref) {
  return const AsyncValue.data(null);
});

class HealthRecordPage extends ConsumerStatefulWidget {
  const HealthRecordPage({Key? key}) : super(key: key);

  @override
  ConsumerState<HealthRecordPage> createState() => _HealthRecordPageState();
}

class _HealthRecordPageState extends ConsumerState<HealthRecordPage> {
  final _dataHashController = TextEditingController();
  final _dataTypeController = TextEditingController();
  final _metadataController = TextEditingController();
  
  @override
  void dispose() {
    _dataHashController.dispose();
    _dataTypeController.dispose();
    _metadataController.dispose();
    super.dispose();
  }
  
  Future<void> _createHealthRecord() async {
    if (_dataHashController.text.isEmpty || 
        _dataTypeController.text.isEmpty || 
        _metadataController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请填写所有字段')),
      );
      return;
    }
    
    ref.read(createRecordStateProvider.notifier).state = 
        const AsyncValue.loading();
    
    try {
      final service = ref.read(blockchainServiceProvider);
      await service.createHealthRecord(
        _dataHashController.text,
        _dataTypeController.text,
        _metadataController.text,
      );
      
      if (mounted) {
        // 成功后清空输入框
        _dataHashController.clear();
        _dataTypeController.clear();
        _metadataController.clear();
        
        // 刷新记录列表
        ref.invalidate(healthRecordsProvider);
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('健康记录创建成功')),
        );
      }
      
      ref.read(createRecordStateProvider.notifier).state = 
          const AsyncValue.data(null);
    } catch (e) {
      ref.read(createRecordStateProvider.notifier).state = 
          AsyncValue.error(e, StackTrace.current);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('创建失败: ${e.toString()}')),
        );
      }
    }
  }
  
  void _showCreateRecordDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('创建健康记录'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _dataHashController,
                decoration: const InputDecoration(
                  labelText: '数据哈希',
                  hintText: '输入IPFS哈希或其他数据标识符',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _dataTypeController,
                decoration: const InputDecoration(
                  labelText: '数据类型',
                  hintText: '例如: 舌诊、面诊、体质检测',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _metadataController,
                decoration: const InputDecoration(
                  labelText: '元数据',
                  hintText: '加密的元数据信息',
                ),
                maxLines: 3,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          Consumer(
            builder: (context, ref, child) {
              final createState = ref.watch(createRecordStateProvider);
              
              return createState.when(
                data: (_) => ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    _createHealthRecord();
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF35BB78),
                  ),
                  child: const Text('创建'),
                ),
                loading: () => const ElevatedButton(
                  onPressed: null,
                  child: SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (_, __) => ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    _createHealthRecord();
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF35BB78),
                  ),
                  child: const Text('重试'),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    final recordsAsync = ref.watch(healthRecordsProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的健康记录'),
        backgroundColor: const Color(0xFF35BB78),
      ),
      body: recordsAsync.when(
        data: (records) {
          if (records.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.health_and_safety_outlined,
                    size: 80,
                    color: Colors.grey,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    '您还没有健康记录',
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: _showCreateRecordDialog,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF35BB78),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                    ),
                    child: const Text('创建健康记录'),
                  ),
                ],
              ),
            );
          }
          
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: records.length,
            itemBuilder: (context, index) {
              final record = records[index];
              final timestamp = DateTime.fromMillisecondsSinceEpoch(
                (record['timestamp'] as int) * 1000,
              );
              
              return Card(
                margin: const EdgeInsets.only(bottom: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: const Color(0xFF35BB78).withOpacity(0.2),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              record['dataType'] as String,
                              style: const TextStyle(
                                color: Color(0xFF35BB78),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const Spacer(),
                          Icon(
                            record['isShared'] as bool
                                ? Icons.share
                                : Icons.lock,
                            color: record['isShared'] as bool
                                ? const Color(0xFFFF6800)
                                : Colors.grey,
                            size: 18,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            record['isShared'] as bool ? '已共享' : '未共享',
                            style: TextStyle(
                              color: record['isShared'] as bool
                                  ? const Color(0xFFFF6800)
                                  : Colors.grey,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        '记录ID: ${record['id']}',
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          const Text(
                            '数据哈希: ',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Expanded(
                            child: Text(
                              record['dataHash'] as String,
                              style: const TextStyle(
                                fontSize: 14,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '创建时间: ${timestamp.toLocal()}',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton.icon(
                            onPressed: () {
                              // 查看详情功能
                            },
                            icon: const Icon(Icons.visibility),
                            label: const Text('查看'),
                          ),
                          const SizedBox(width: 8),
                          TextButton.icon(
                            onPressed: () {
                              // 共享功能
                            },
                            icon: const Icon(Icons.share),
                            label: const Text('共享'),
                            style: TextButton.styleFrom(
                              foregroundColor: const Color(0xFFFF6800),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
        loading: () => const Center(
          child: CircularProgressIndicator(),
        ),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                color: Colors.red,
                size: 60,
              ),
              const SizedBox(height: 16),
              Text(
                '加载失败: $error',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => ref.refresh(healthRecordsProvider),
                child: const Text('重试'),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showCreateRecordDialog,
        backgroundColor: const Color(0xFF35BB78),
        child: const Icon(Icons.add),
      ),
    );
  }
}
