import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/di/providers/blockchain_providers.dart';

class CreateHealthRecordForm extends ConsumerStatefulWidget {
  const CreateHealthRecordForm({Key? key}) : super(key: key);

  @override
  ConsumerState<CreateHealthRecordForm> createState() => _CreateHealthRecordFormState();
}

class _CreateHealthRecordFormState extends ConsumerState<CreateHealthRecordForm> {
  final _formKey = GlobalKey<FormState>();
  final _dataHashController = TextEditingController();
  final _dataUrlController = TextEditingController();
  
  bool _isSubmitting = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void dispose() {
    _dataHashController.dispose();
    _dataUrlController.dispose();
    super.dispose();
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final repository = ref.read(blockchainRepositoryProvider);
      final txHash = await repository.createHealthRecord(
        _dataHashController.text.trim(),
        _dataUrlController.text.trim(),
      );

      setState(() {
        _successMessage = '健康记录创建成功！交易哈希: ${txHash.substring(0, 10)}...';
        _dataHashController.clear();
        _dataUrlController.clear();
      });
    } catch (e) {
      setState(() {
        _errorMessage = '创建健康记录失败: $e';
      });
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '创建健康记录',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFF35BB78),
            ),
          ),
          const SizedBox(height: 16),
          if (_errorMessage != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red.shade200),
              ),
              child: Text(
                _errorMessage!,
                style: TextStyle(color: Colors.red.shade800),
              ),
            ),
          if (_successMessage != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Text(
                _successMessage!,
                style: TextStyle(color: Colors.green.shade800),
              ),
            ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _dataHashController,
            decoration: const InputDecoration(
              labelText: '数据哈希',
              hintText: '输入健康数据的哈希值',
              border: OutlineInputBorder(),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入数据哈希';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _dataUrlController,
            decoration: const InputDecoration(
              labelText: '数据URL',
              hintText: '输入访问健康数据的URL',
              border: OutlineInputBorder(),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入数据URL';
              }
              return null;
            },
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF35BB78),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              onPressed: _isSubmitting ? null : _submitForm,
              child: _isSubmitting
                  ? const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        color: Colors.white,
                        strokeWidth: 2,
                      ),
                    )
                  : const Text('提交健康记录'),
            ),
          ),
        ],
      ),
    );
  }
} 