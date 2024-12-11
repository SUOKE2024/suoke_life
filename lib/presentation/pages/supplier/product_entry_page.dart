import 'package:flutter/material.dart';

class ProductEntryPage extends StatefulWidget {
  const ProductEntryPage({super.key});

  @override
  State<ProductEntryPage> createState() => _ProductEntryPageState();
}

class _ProductEntryPageState extends State<ProductEntryPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _priceController = TextEditingController();
  final _stockController = TextEditingController();
  final _originController = TextEditingController();
  final _specificationController = TextEditingController();
  final _customizationController = TextEditingController();

  String _selectedCategory = '优质农产';
  bool _isCustomizable = false;
  List<String> _productImages = [];
  DateTime? _harvestDate;
  DateTime? _deliveryDate;

  final List<String> _categories = [
    '优质农产',
    '预定制品',
    '养生茶饮',
    '健康食品',
    '其他',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _priceController.dispose();
    _stockController.dispose();
    _originController.dispose();
    _specificationController.dispose();
    _customizationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('产品录入'),
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
                  DropdownButtonFormField<String>(
                    value: _selectedCategory,
                    decoration: const InputDecoration(
                      labelText: '产品类别',
                      border: OutlineInputBorder(),
                    ),
                    items: _categories.map((category) {
                      return DropdownMenuItem(
                        value: category,
                        child: Text(category),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedCategory = value!;
                        _isCustomizable = value == '预定制品';
                      });
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _nameController,
                    decoration: const InputDecoration(
                      labelText: '产品名称',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入产品名称';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _descriptionController,
                    decoration: const InputDecoration(
                      labelText: '产品描述',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 3,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入产品描述';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: _priceController,
                          decoration: const InputDecoration(
                            labelText: '价格',
                            border: OutlineInputBorder(),
                            prefixText: '¥',
                          ),
                          keyboardType: TextInputType.number,
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return '请输入价格';
                            }
                            return null;
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: TextFormField(
                          controller: _stockController,
                          decoration: const InputDecoration(
                            labelText: '库存',
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return '请输入库存';
                            }
                            return null;
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    '产品图片',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    height: 120,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      padding: const EdgeInsets.all(8),
                      itemCount: _productImages.length + 1,
                      itemBuilder: (context, index) {
                        if (index == _productImages.length) {
                          return GestureDetector(
                            onTap: () {
                              // TODO: 实现图片上传功能
                            },
                            child: Container(
                              width: 100,
                              margin: const EdgeInsets.only(right: 8),
                              decoration: BoxDecoration(
                                color: Colors.grey[200],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Icon(
                                Icons.add_photo_alternate,
                                size: 40,
                                color: Colors.grey,
                              ),
                            ),
                          );
                        }
                        return Container(
                          width: 100,
                          margin: const EdgeInsets.only(right: 8),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(8),
                            image: DecorationImage(
                              image: NetworkImage(_productImages[index]),
                              fit: BoxFit.cover,
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    '产地信息',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _originController,
                    decoration: const InputDecoration(
                      labelText: '产地',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入产地';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _specificationController,
                    decoration: const InputDecoration(
                      labelText: '规格',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入规格';
                      }
                      return null;
                    },
                  ),
                  if (_isCustomizable) ...[
                    const SizedBox(height: 24),
                    const Text(
                      '预定制信息',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    ListTile(
                      title: const Text('预计收获日期'),
                      subtitle: Text(
                        _harvestDate?.toString() ?? '请选择日期',
                      ),
                      trailing: const Icon(Icons.calendar_today),
                      onTap: () async {
                        final date = await showDatePicker(
                          context: context,
                          initialDate: DateTime.now(),
                          firstDate: DateTime.now(),
                          lastDate: DateTime.now().add(const Duration(days: 365)),
                        );
                        if (date != null) {
                          setState(() {
                            _harvestDate = date;
                          });
                        }
                      },
                    ),
                    ListTile(
                      title: const Text('预计配送日期'),
                      subtitle: Text(
                        _deliveryDate?.toString() ?? '请选择日期',
                      ),
                      trailing: const Icon(Icons.calendar_today),
                      onTap: () async {
                        final date = await showDatePicker(
                          context: context,
                          initialDate: DateTime.now(),
                          firstDate: DateTime.now(),
                          lastDate: DateTime.now().add(const Duration(days: 365)),
                        );
                        if (date != null) {
                          setState(() {
                            _deliveryDate = date;
                          });
                        }
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _customizationController,
                      decoration: const InputDecoration(
                        labelText: '定制要求说明',
                        border: OutlineInputBorder(),
                      ),
                      maxLines: 3,
                    ),
                  ],
                  const SizedBox(height: 32),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: () {
                        if (_formKey.currentState!.validate()) {
                          // TODO: 提交产品信息
                        }
                      },
                      child: const Padding(
                        padding: EdgeInsets.symmetric(vertical: 16.0),
                        child: Text('提交'),
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