import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/di/providers/blockchain_providers.dart';
import 'package:suoke_life/domain/entities/health_record.dart';

class HealthRecordsList extends ConsumerWidget {
  final String userAddress;

  const HealthRecordsList({Key? key, required this.userAddress}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recordsAsync = ref.watch(userHealthRecordsProvider(userAddress));

    return recordsAsync.when(
      data: (records) {
        if (records.isEmpty) {
          return _buildEmptyState();
        } else {
          return _buildRecordsList(records);
        }
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => Center(
        child: Text('加载健康记录失败: $error'),
      ),
    );
  }
  
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.health_and_safety_outlined,
            size: 64,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            '暂无健康记录',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '请在"创建记录"标签页添加您的第一条健康记录',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
  
  Widget _buildRecordsList(List<HealthRecord> records) {
    return ListView.builder(
      itemCount: records.length,
      itemBuilder: (context, index) {
        final record = records[index];
        return HealthRecordCard(record: record);
      },
    );
  }
}

class HealthRecordCard extends StatelessWidget {
  final HealthRecord record;

  const HealthRecordCard({Key? key, required this.record}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final dateTime = DateTime.fromMillisecondsSinceEpoch(
      record.timestamp.toInt() * 1000,
    );
    final formattedDate = '${dateTime.year}-${dateTime.month.toString().padLeft(2, '0')}-${dateTime.day.toString().padLeft(2, '0')}';

    return GestureDetector(
      onTap: () {
        context.router.pushNamed('/blockchain/health-records/${record.id}');
      },
      child: Card(
        elevation: 2,
        margin: const EdgeInsets.only(bottom: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '记录 #${record.id}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  _buildShareStatusBadge(record.isShared),
                ],
              ),
              const Divider(height: 24),
              _buildInfoRow('数据哈希', record.dataHash, isHash: true),
              const SizedBox(height: 8),
              _buildInfoRow('创建日期', formattedDate),
              const SizedBox(height: 8),
              _buildInfoRow('数据URL', record.dataUrl, isUrl: true),
              if (record.isShared) ...[
                const Divider(height: 24),
                const Text(
                  '已授权用户',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 8),
                _buildAuthorizedUsersList(record.authorizedUsers),
              ],
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton.icon(
                    icon: const Icon(Icons.share, size: 16),
                    label: const Text('共享记录'),
                    onPressed: () => _showShareDialog(context),
                  ),
                  const SizedBox(width: 8),
                  TextButton.icon(
                    icon: const Icon(Icons.arrow_forward, size: 16),
                    label: const Text('查看详情'),
                    onPressed: () {
                      context.router.pushNamed('/blockchain/health-records/${record.id}');
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildShareStatusBadge(bool isShared) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isShared
            ? const Color(0xFF35BB78).withAlpha(30)
            : Colors.orange.withAlpha(30),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(
        isShared ? '已共享' : '未共享',
        style: TextStyle(
          fontSize: 12,
          color: isShared ? const Color(0xFF35BB78) : Colors.orange,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
  
  Widget _buildAuthorizedUsersList(List<String> users) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: users.map((user) {
        return Chip(
          backgroundColor: Colors.grey.shade100,
          label: Text(
            '${user.substring(0, 6)}...${user.substring(user.length - 4)}',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade800,
            ),
          ),
        );
      }).toList(),
    );
  }
  
  Widget _buildInfoRow(String label, String value, {bool isHash = false, bool isUrl = false}) {
    String displayValue = value;
    if (isHash && value.length > 20) {
      displayValue = '${value.substring(0, 10)}...${value.substring(value.length - 10)}';
    } else if (isUrl && value.length > 30) {
      displayValue = '${value.substring(0, 30)}...';
    }

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 80,
          child: Text(
            label,
            style: TextStyle(
              color: Colors.grey.shade600,
            ),
          ),
        ),
        Expanded(
          child: Text(
            displayValue,
            style: const TextStyle(
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }
  
  void _showShareDialog(BuildContext context) {
    final addressController = TextEditingController();
    bool isSubmitting = false;

    // 获取WidgetRef以使用Riverpod
    final widgetRef = context.findAncestorStateOfType<ConsumerState>()?.ref;
    if (widgetRef == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('无法获取状态管理器，请重试')),
      );
      return;
    }

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('共享健康记录'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('请输入您想要共享此健康记录的用户地址：'),
              const SizedBox(height: 16),
              TextField(
                controller: addressController,
                decoration: const InputDecoration(
                  labelText: '用户地址',
                  hintText: '0x...',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('取消'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF35BB78),
                foregroundColor: Colors.white,
              ),
              onPressed: isSubmitting 
                ? null 
                : () async {
                  final address = addressController.text.trim();
                  if (address.isEmpty || !address.startsWith('0x') || address.length != 42) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('请输入有效的以太坊地址')),
                    );
                    return;
                  }
                  
                  setState(() {
                    isSubmitting = true;
                  });
                  
                  try {
                    // 通过 Riverpod 获取区块链存储库
                    final blockchainRepo = widgetRef.read(blockchainRepositoryProvider);
                    
                    // 调用共享记录方法
                    await blockchainRepo.shareHealthRecord(record.id, address);
                    
                    Navigator.of(context).pop();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('健康记录共享成功！')),
                    );
                  } catch (e) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('共享失败: $e')),
                    );
                  } finally {
                    setState(() {
                      isSubmitting = false;
                    });
                  }
                },
              child: isSubmitting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Text('共享'),
            ),
          ],
        ),
      ),
    );
  }
}