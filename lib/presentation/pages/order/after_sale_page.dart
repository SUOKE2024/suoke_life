import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../services/order_service.dart';

class AfterSalePage extends StatefulWidget {
  final String orderId;
  final List<OrderItem> items;
  final double totalAmount;

  const AfterSalePage({
    Key? key,
    required this.orderId,
    required this.items,
    required this.totalAmount,
  }) : super(key: key);

  @override
  State<AfterSalePage> createState() => _AfterSalePageState();
}

class _AfterSalePageState extends State<AfterSalePage> {
  final _formKey = GlobalKey<FormState>();
  final _reasonController = TextEditingController();
  final _imagePicker = ImagePicker();
  
  AfterSaleType _type = AfterSaleType.refundOnly;
  String? _selectedReason;
  List<XFile> _evidenceImages = [];
  List<OrderItem> _selectedItems = [];
  bool _isSubmitting = false;

  final List<String> _refundReasons = [
    '商品质量问题',
    '商品与描述不符',
    '商品损坏',
    '不想要了',
    '其他原因'
  ];

  @override
  void initState() {
    super.initState();
    // 默认选中所有商品
    _selectedItems = List.from(widget.items);
  }

  @override
  void dispose() {
    _reasonController.dispose();
    super.dispose();
  }

  Future<void> _pickImages() async {
    final List<XFile> images = await _imagePicker.pickMultiImage();
    if (images.isNotEmpty) {
      setState(() {
        if (_evidenceImages.length + images.length <= 5) {
          _evidenceImages.addAll(images);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('最多只能上传5张图片')),
          );
        }
      });
    }
  }

  void _removeImage(int index) {
    setState(() {
      _evidenceImages.removeAt(index);
    });
  }

  void _toggleItem(OrderItem item) {
    setState(() {
      if (_selectedItems.contains(item)) {
        _selectedItems.remove(item);
      } else {
        _selectedItems.add(item);
      }
    });
  }

  double get _selectedTotalAmount {
    return _selectedItems.fold(
      0,
      (sum, item) => sum + (item.price * item.quantity),
    );
  }

  Future<void> _submitAfterSale() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请选择要售后的商品')),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      await OrderService().submitAfterSale(
        orderId: widget.orderId,
        type: _type,
        reason: _selectedReason!,
        description: _reasonController.text,
        images: _evidenceImages,
        items: _selectedItems,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('售后申请提交成功')),
        );
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('售后申请提交失败: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('申请售后'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildTypeSelector(),
            const SizedBox(height: 16),
            _buildItemSelector(),
            const SizedBox(height: 16),
            _buildReasonSelector(),
            const SizedBox(height: 16),
            _buildDescriptionInput(),
            const SizedBox(height: 16),
            _buildImageUploader(),
            const SizedBox(height: 16),
            _buildRefundAmount(),
            const SizedBox(height: 24),
            _buildSubmitButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '售后类型',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        SegmentedButton<AfterSaleType>(
          segments: const [
            ButtonSegment(
              value: AfterSaleType.refundOnly,
              label: Text('仅退款'),
            ),
            ButtonSegment(
              value: AfterSaleType.returnAndRefund,
              label: Text('退货退款'),
            ),
          ],
          selected: {_type},
          onSelectionChanged: (Set<AfterSaleType> selected) {
            setState(() {
              _type = selected.first;
            });
          },
        ),
      ],
    );
  }

  Widget _buildItemSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '选择商品',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: widget.items.length,
          itemBuilder: (context, index) {
            final item = widget.items[index];
            final isSelected = _selectedItems.contains(item);
            return CheckboxListTile(
              value: isSelected,
              onChanged: (value) => _toggleItem(item),
              title: Text(item.product.name),
              subtitle: Text('数量: ${item.quantity}'),
              secondary: Image.network(
                item.product.imageUrl,
                width: 50,
                height: 50,
                fit: BoxFit.cover,
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildReasonSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '退款原因',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<String>(
          value: _selectedReason,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            hintText: '请选择退款原因',
          ),
          items: _refundReasons
              .map((reason) => DropdownMenuItem(
                    value: reason,
                    child: Text(reason),
                  ))
              .toList(),
          onChanged: (value) {
            setState(() {
              _selectedReason = value;
            });
          },
          validator: (value) {
            if (value == null || value.isEmpty) {
              return '请选择退款原因';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildDescriptionInput() {
    return TextFormField(
      controller: _reasonController,
      maxLines: 3,
      maxLength: 200,
      decoration: const InputDecoration(
        labelText: '问题描述',
        hintText: '请详细描述问题...',
        border: OutlineInputBorder(),
      ),
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return '请输入问题描述';
        }
        if (value.trim().length < 10) {
          return '问题描述至少10个字';
        }
        return null;
      },
    );
  }

  Widget _buildImageUploader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '上传凭证',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
          ),
          itemCount: _evidenceImages.length + (_evidenceImages.length < 5 ? 1 : 0),
          itemBuilder: (context, index) {
            if (index == _evidenceImages.length) {
              return InkWell(
                onTap: _pickImages,
                child: Container(
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.add_photo_alternate, size: 40),
                ),
              );
            }

            return Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    _evidenceImages[index].path,
                    fit: BoxFit.cover,
                    width: double.infinity,
                    height: double.infinity,
                  ),
                ),
                Positioned(
                  right: 0,
                  top: 0,
                  child: IconButton(
                    icon: const Icon(Icons.close, color: Colors.white),
                    onPressed: () => _removeImage(index),
                  ),
                ),
              ],
            );
          },
        ),
      ],
    );
  }

  Widget _buildRefundAmount() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '退款金额',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('预计退款'),
              Text(
                '¥${_selectedTotalAmount.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.red,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSubmitButton() {
    return ElevatedButton(
      onPressed: _isSubmitting ? null : _submitAfterSale,
      child: _isSubmitting
          ? const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Text('提交申请'),
    );
  }
} 