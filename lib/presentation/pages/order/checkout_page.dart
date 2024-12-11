import 'package:flutter/material.dart';
import '../../../services/cart_service.dart';

class CheckoutPage extends StatefulWidget {
  final List<CartItem> items;
  final double totalAmount;

  const CheckoutPage({
    super.key,
    required this.items,
    required this.totalAmount,
  });

  @override
  State<CheckoutPage> createState() => _CheckoutPageState();
}

class _CheckoutPageState extends State<CheckoutPage> {
  String? _selectedPaymentMethod;
  String? _selectedAddress;
  String? _remarks;
  bool _isProcessing = false;

  final List<String> _paymentMethods = [
    '微信支付',
    '支付宝',
    '银行卡',
  ];

  final List<Address> _addresses = [
    const Address(
      id: '1',
      name: '张三',
      phone: '13800138000',
      address: '北京市朝阳区某某街道某某小区1号楼1单元101室',
      isDefault: true,
    ),
    const Address(
      id: '2',
      name: '李四',
      phone: '13900139000',
      address: '上海市浦东新区某某路某某大厦B座2201室',
      isDefault: false,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _selectedAddress = _addresses.firstWhere((addr) => addr.isDefault).id;
    _selectedPaymentMethod = _paymentMethods.first;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('订单结算'),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 收货地址
              Card(
                child: Column(
                  children: [
                    const ListTile(
                      title: Text(
                        '收货地址',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const Divider(height: 1),
                    ..._addresses.map((address) {
                      final isSelected = address.id == _selectedAddress;
                      return RadioListTile<String>(
                        value: address.id,
                        groupValue: _selectedAddress,
                        onChanged: (value) {
                          setState(() {
                            _selectedAddress = value;
                          });
                        },
                        title: Text(
                          '${address.name} ${address.phone}',
                          style: const TextStyle(
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        subtitle: Text(
                          address.address,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                        secondary: TextButton(
                          onPressed: () {
                            // TODO: 实现地址编辑功能
                          },
                          child: const Text('编辑'),
                        ),
                      );
                    }).toList(),
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: OutlinedButton(
                        onPressed: () {
                          // TODO: 实现新增地址功能
                        },
                        child: const Text('新增收货地址'),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // 商品清单
              Card(
                child: Column(
                  children: [
                    const ListTile(
                      title: Text(
                        '商品清单',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const Divider(height: 1),
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: widget.items.length,
                      itemBuilder: (context, index) {
                        final item = widget.items[index];
                        return ListTile(
                          leading: ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: Image.asset(
                              item.imageUrl,
                              width: 50,
                              height: 50,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                return Container(
                                  width: 50,
                                  height: 50,
                                  color: Colors.grey[200],
                                  child: const Icon(
                                    Icons.image,
                                    color: Colors.grey,
                                  ),
                                );
                              },
                            ),
                          ),
                          title: Text(
                            item.name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          subtitle: Text(
                            item.specification,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                          trailing: Text(
                            '¥${item.price.toStringAsFixed(2)} × ${item.quantity}',
                            style: const TextStyle(
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // 支付方式
              Card(
                child: Column(
                  children: [
                    const ListTile(
                      title: Text(
                        '支付方式',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const Divider(height: 1),
                    ...List.generate(_paymentMethods.length, (index) {
                      final method = _paymentMethods[index];
                      return RadioListTile<String>(
                        value: method,
                        groupValue: _selectedPaymentMethod,
                        onChanged: (value) {
                          setState(() {
                            _selectedPaymentMethod = value;
                          });
                        },
                        title: Text(method),
                      );
                    }),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // 订单备注
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '订单备注',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        maxLines: 3,
                        maxLength: 100,
                        decoration: const InputDecoration(
                          hintText: '请输入订单备注信息（选填）',
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (value) {
                          setState(() {
                            _remarks = value;
                          });
                        },
                      ),
                    ],
                  ),
                ),
              ),

              // 底部占位
              const SizedBox(height: 80),
            ],
          ),
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 8,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: SafeArea(
                child: Row(
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text('实付金额'),
                        Text(
                          '¥${widget.totalAmount.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.red,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: FilledButton(
                        onPressed: _isProcessing
                            ? null
                            : () async {
                                if (_selectedAddress == null) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('请选择收货地址'),
                                    ),
                                  );
                                  return;
                                }
                                if (_selectedPaymentMethod == null) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('请选择支付方式'),
                                    ),
                                  );
                                  return;
                                }

                                setState(() {
                                  _isProcessing = true;
                                });

                                // TODO: 实现订单提交和支付功能
                                await Future.delayed(
                                  const Duration(seconds: 2),
                                );

                                setState(() {
                                  _isProcessing = false;
                                });

                                if (mounted) {
                                  Navigator.pop(context);
                                }
                              },
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
                            : const Text('提交订单'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class Address {
  final String id;
  final String name;
  final String phone;
  final String address;
  final bool isDefault;

  const Address({
    required this.id,
    required this.name,
    required this.phone,
    required this.address,
    required this.isDefault,
  });
} 