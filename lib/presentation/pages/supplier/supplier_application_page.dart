import 'package:flutter/material.dart';

class SupplierApplicationPage extends StatefulWidget {
  const SupplierApplicationPage({super.key});

  @override
  State<SupplierApplicationPage> createState() => _SupplierApplicationPageState();
}

class _SupplierApplicationPageState extends State<SupplierApplicationPage> {
  final _formKey = GlobalKey<FormState>();
  final _companyNameController = TextEditingController();
  final _contactNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _addressController = TextEditingController();
  final _businessLicenseController = TextEditingController();
  final _descriptionController = TextEditingController();

  List<String> _selectedCategories = [];
  final List<String> _categories = [
    '优质农产',
    '预定制品',
    '养生茶饮',
    '健康食品',
    '其他',
  ];

  @override
  void dispose() {
    _companyNameController.dispose();
    _contactNameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _addressController.dispose();
    _businessLicenseController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('供应商申请'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.support_agent),
            onPressed: () {
              Navigator.pushNamed(context, '/supplier/assistant');
            },
            tooltip: 'AI商务助手',
          ),
        ],
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '基本信息',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _companyNameController,
                    decoration: const InputDecoration(
                      labelText: '企业名称',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入企业名称';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _contactNameController,
                    decoration: const InputDecoration(
                      labelText: '联系人',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入联系人姓名';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _phoneController,
                    decoration: const InputDecoration(
                      labelText: '联系电话',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.phone,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入联系电话';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _emailController,
                    decoration: const InputDecoration(
                      labelText: '电子邮箱',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.emailAddress,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入电子邮箱';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    '经营类目',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _categories.map((category) {
                      final isSelected = _selectedCategories.contains(category);
                      return FilterChip(
                        label: Text(category),
                        selected: isSelected,
                        onSelected: (selected) {
                          setState(() {
                            if (selected) {
                              _selectedCategories.add(category);
                            } else {
                              _selectedCategories.remove(category);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    '资质认证',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.upload_file),
                            const SizedBox(width: 8),
                            const Text('上传营业执照'),
                            const Spacer(),
                            TextButton(
                              onPressed: () {
                                // TODO: 实现文件上传功能
                              },
                              child: const Text('选择文件'),
                            ),
                          ],
                        ),
                        if (_businessLicenseController.text.isNotEmpty)
                          Text(_businessLicenseController.text),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    '补充说明',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _descriptionController,
                    decoration: const InputDecoration(
                      labelText: '请描述您的产品特色和优势',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 4,
                  ),
                  const SizedBox(height: 32),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: () {
                        if (_formKey.currentState!.validate()) {
                          // TODO: 提交申请
                        }
                      },
                      child: const Padding(
                        padding: EdgeInsets.symmetric(vertical: 16.0),
                        child: Text('提交申请'),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            right: 16,
            bottom: 16,
            child: FloatingActionButton(
              onPressed: () {
                Navigator.pushNamed(context, '/supplier/assistant');
              },
              child: const Icon(Icons.support_agent),
            ),
          ),
        ],
      ),
    );
  }
} 