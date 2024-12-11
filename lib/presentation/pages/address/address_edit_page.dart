import 'package:flutter/material.dart';
import '../../../services/address_service.dart';
import '../../../core/di/service_locator.dart';

class AddressEditPage extends StatefulWidget {
  final Address? address;

  const AddressEditPage({
    super.key,
    this.address,
  });

  @override
  State<AddressEditPage> createState() => _AddressEditPageState();
}

class _AddressEditPageState extends State<AddressEditPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _provinceController = TextEditingController();
  final _cityController = TextEditingController();
  final _districtController = TextEditingController();
  final _streetController = TextEditingController();
  final _detailController = TextEditingController();
  
  bool _isDefault = false;
  String? _selectedTag;
  bool _isProcessing = false;

  final List<String> _tags = ['家', '公司', '学校'];

  @override
  void initState() {
    super.initState();
    if (widget.address != null) {
      _nameController.text = widget.address!.name;
      _phoneController.text = widget.address!.phone;
      _provinceController.text = widget.address!.province;
      _cityController.text = widget.address!.city;
      _districtController.text = widget.address!.district;
      _streetController.text = widget.address!.street;
      _detailController.text = widget.address!.detail;
      _isDefault = widget.address!.isDefault;
      _selectedTag = widget.address!.tag;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _provinceController.dispose();
    _cityController.dispose();
    _districtController.dispose();
    _streetController.dispose();
    _detailController.dispose();
    super.dispose();
  }

  Future<void> _saveAddress() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      final addressService = serviceLocator<AddressService>();
      final address = Address(
        id: widget.address?.id ?? DateTime.now().millisecondsSinceEpoch.toString(),
        name: _nameController.text,
        phone: _phoneController.text,
        province: _provinceController.text,
        city: _cityController.text,
        district: _districtController.text,
        street: _streetController.text,
        detail: _detailController.text,
        isDefault: _isDefault,
        tag: _selectedTag,
      );

      if (widget.address != null) {
        await addressService.updateAddress(address);
      } else {
        await addressService.addAddress(address);
      }

      if (mounted) {
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('保存失败：$e')),
        );
      }
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.address == null ? '新增地址' : '编辑地址'),
        centerTitle: true,
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 联系人信息
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '联系人信息',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _nameController,
                      decoration: const InputDecoration(
                        labelText: '收货人',
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入收货人姓名';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _phoneController,
                      decoration: const InputDecoration(
                        labelText: '手机号码',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.phone,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入手机号码';
                        }
                        // TODO: 添加手机号码格式验证
                        return null;
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 收货地址
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '收货地址',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _provinceController,
                            decoration: const InputDecoration(
                              labelText: '省份',
                              border: OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return '请输入省份';
                              }
                              return null;
                            },
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: TextFormField(
                            controller: _cityController,
                            decoration: const InputDecoration(
                              labelText: '城市',
                              border: OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return '请输入城市';
                              }
                              return null;
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _districtController,
                            decoration: const InputDecoration(
                              labelText: '区/县',
                              border: OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return '请输入区/县';
                              }
                              return null;
                            },
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: TextFormField(
                            controller: _streetController,
                            decoration: const InputDecoration(
                              labelText: '街道',
                              border: OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return '请输入街道';
                              }
                              return null;
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _detailController,
                      decoration: const InputDecoration(
                        labelText: '详细地址',
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入详细地址';
                        }
                        return null;
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 地址标签
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '地址标签',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 8,
                      children: [
                        ..._tags.map((tag) {
                          return ChoiceChip(
                            label: Text(tag),
                            selected: _selectedTag == tag,
                            onSelected: (selected) {
                              setState(() {
                                _selectedTag = selected ? tag : null;
                              });
                            },
                          );
                        }),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 设为默认地址
            Card(
              child: SwitchListTile(
                title: const Text('设为默认地址'),
                value: _isDefault,
                onChanged: (value) {
                  setState(() {
                    _isDefault = value;
                  });
                },
              ),
            ),
            const SizedBox(height: 32),

            // 保存按钮
            FilledButton(
              onPressed: _isProcessing ? null : _saveAddress,
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: _isProcessing
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Colors.white,
                          ),
                        ),
                      )
                    : const Text('保存地址'),
              ),
            ),
          ],
        ),
      ),
    );
  }
} 