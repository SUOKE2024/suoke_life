import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../services/order_service.dart';

class OrderReviewPage extends StatefulWidget {
  final String orderId;
  final List<OrderItem> items;

  const OrderReviewPage({
    Key? key,
    required this.orderId,
    required this.items,
  }) : super(key: key);

  @override
  State<OrderReviewPage> createState() => _OrderReviewPageState();
}

class _OrderReviewPageState extends State<OrderReviewPage> {
  final _formKey = GlobalKey<FormState>();
  final _contentController = TextEditingController();
  final _imagePicker = ImagePicker();
  double _rating = 5.0;
  List<XFile> _selectedImages = [];
  bool _isAnonymous = false;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _contentController.dispose();
    super.dispose();
  }

  Future<void> _pickImages() async {
    final List<XFile> images = await _imagePicker.pickMultiImage();
    if (images.isNotEmpty) {
      setState(() {
        if (_selectedImages.length + images.length <= 9) {
          _selectedImages.addAll(images);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('最多只能上传9张图片')),
          );
        }
      });
    }
  }

  void _removeImage(int index) {
    setState(() {
      _selectedImages.removeAt(index);
    });
  }

  Future<void> _submitReview() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSubmitting = true;
    });

    try {
      await OrderService().submitReview(
        orderId: widget.orderId,
        rating: _rating,
        content: _contentController.text,
        images: _selectedImages,
        isAnonymous: _isAnonymous,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('评价提交成功')),
        );
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('评价提交失败: $e')),
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
        title: const Text('订单评价'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildRatingSection(),
            const SizedBox(height: 16),
            _buildContentInput(),
            const SizedBox(height: 16),
            _buildImageUpload(),
            const SizedBox(height: 16),
            _buildAnonymousSwitch(),
            const SizedBox(height: 24),
            _buildSubmitButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildRatingSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '整体评分',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: Slider(
                value: _rating,
                min: 1,
                max: 5,
                divisions: 4,
                label: _rating.toString(),
                onChanged: (value) {
                  setState(() {
                    _rating = value;
                  });
                },
              ),
            ),
            Text(
              _rating.toString(),
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildContentInput() {
    return TextFormField(
      controller: _contentController,
      maxLines: 5,
      maxLength: 500,
      decoration: const InputDecoration(
        labelText: '评价内容',
        hintText: '请分享您的使用体验...',
        border: OutlineInputBorder(),
      ),
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return '请输入评价内容';
        }
        if (value.trim().length < 10) {
          return '评价内容至少10个字';
        }
        return null;
      },
    );
  }

  Widget _buildImageUpload() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '上传图片',
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
          itemCount: _selectedImages.length + (_selectedImages.length < 9 ? 1 : 0),
          itemBuilder: (context, index) {
            if (index == _selectedImages.length) {
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
                    _selectedImages[index].path,
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

  Widget _buildAnonymousSwitch() {
    return SwitchListTile(
      title: const Text('匿名评价'),
      subtitle: const Text('开启后将不会显示您的用户名'),
      value: _isAnonymous,
      onChanged: (value) {
        setState(() {
          _isAnonymous = value;
        });
      },
    );
  }

  Widget _buildSubmitButton() {
    return ElevatedButton(
      onPressed: _isSubmitting ? null : _submitReview,
      child: _isSubmitting
          ? const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Text('提交评价'),
    );
  }
} 