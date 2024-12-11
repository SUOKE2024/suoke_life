import 'dart:async';
import 'package:flutter/material.dart';
import '../../../services/payment_service.dart';
import '../../../core/di/service_locator.dart';

class PaymentPage extends StatefulWidget {
  final String orderId;
  final double amount;
  final String description;

  const PaymentPage({
    super.key,
    required this.orderId,
    required this.amount,
    required this.description,
  });

  @override
  State<PaymentPage> createState() => _PaymentPageState();
}

class _PaymentPageState extends State<PaymentPage> {
  final _paymentService = serviceLocator<PaymentService>();
  PaymentMethod _selectedMethod = PaymentMethod.wechat;
  bool _isProcessing = false;
  StreamSubscription? _paymentStatusSubscription;
  String? _paymentId;

  final List<PaymentMethodOption> _paymentMethods = [
    PaymentMethodOption(
      method: PaymentMethod.wechat,
      icon: Icons.wechat,
      name: '微信支付',
      description: '推荐使用微信支付',
      color: const Color(0xFF07C160),
    ),
    PaymentMethodOption(
      method: PaymentMethod.alipay,
      icon: Icons.account_balance_wallet,
      name: '支付宝',
      description: '推荐使用支付宝',
      color: const Color(0xFF1677FF),
    ),
    PaymentMethodOption(
      method: PaymentMethod.bankCard,
      icon: Icons.credit_card,
      name: '银行卡',
      description: '支持储蓄卡和信用卡',
      color: Colors.orange,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _listenToPaymentStatus();
  }

  void _listenToPaymentStatus() {
    _paymentStatusSubscription = _paymentService.paymentStatusStream.listen(
      (status) {
        switch (status) {
          case PaymentStatus.success:
            if (mounted) {
              Navigator.pop(context, true);
            }
            break;
          case PaymentStatus.failed:
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('支付失败，请重试')),
              );
              setState(() {
                _isProcessing = false;
              });
            }
            break;
          case PaymentStatus.cancelled:
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('支付已取消')),
              );
              setState(() {
                _isProcessing = false;
              });
            }
            break;
          default:
            break;
        }
      },
    );
  }

  @override
  void dispose() {
    _paymentStatusSubscription?.cancel();
    super.dispose();
  }

  Future<void> _processPayment() async {
    if (_isProcessing) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      _paymentId = await _paymentService.createPaymentOrder(
        orderId: widget.orderId,
        amount: widget.amount,
        method: _selectedMethod,
        description: widget.description,
      );

      await _paymentService.processPayment(
        paymentId: _paymentId!,
        method: _selectedMethod,
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('支付失败：$e')),
        );
        setState(() {
          _isProcessing = false;
        });
      }
    }
  }

  Future<bool> _onWillPop() async {
    if (_isProcessing) {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('确认取消'),
          content: const Text('当前正在支付中，确定要取消吗？'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('继续支付'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text(
                '取消支付',
                style: TextStyle(color: Colors.red),
              ),
            ),
          ],
        ),
      );

      if (confirmed == true && _paymentId != null) {
        await _paymentService.cancelPayment(_paymentId!);
      }

      return confirmed ?? false;
    }
    return true;
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: _onWillPop,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('收银台'),
          centerTitle: true,
        ),
        body: Column(
          children: [
            // 支付金额
            Container(
              padding: const EdgeInsets.all(24),
              color: Theme.of(context).primaryColor.withOpacity(0.1),
              child: Column(
                children: [
                  const Text(
                    '支付金额',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '¥${widget.amount.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (widget.description.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      widget.description,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // 支付方式列表
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  const Text(
                    '选择支付方式',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  ...List.generate(
                    _paymentMethods.length,
                    (index) {
                      final method = _paymentMethods[index];
                      return RadioListTile<PaymentMethod>(
                        value: method.method,
                        groupValue: _selectedMethod,
                        onChanged: _isProcessing
                            ? null
                            : (value) {
                                setState(() {
                                  _selectedMethod = value!;
                                });
                              },
                        title: Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: method.color.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Icon(
                                method.icon,
                                color: method.color,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  method.name,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                Text(
                                  method.description,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),

            // 支付按钮
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: _isProcessing ? null : _processPayment,
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
                            : Text(
                                '确认支付 ¥${widget.amount.toStringAsFixed(2)}',
                              ),
                      ),
                    ),
                  ),
                  if (_isProcessing) ...[
                    const SizedBox(height: 16),
                    Text(
                      '正在处理支付请求，请勿关闭页面',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class PaymentMethodOption {
  final PaymentMethod method;
  final IconData icon;
  final String name;
  final String description;
  final Color color;

  const PaymentMethodOption({
    required this.method,
    required this.icon,
    required this.name,
    required this.description,
    required this.color,
  });
} 