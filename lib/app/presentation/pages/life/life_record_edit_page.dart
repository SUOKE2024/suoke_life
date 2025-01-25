import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/life/life_record_edit_controller.dart';
import '../../widgets/image_picker_grid.dart';

class LifeRecordEditPage extends StatelessWidget {
  const LifeRecordEditPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(controller.isEditing ? '编辑记录' : '新建记录'),
        actions: [
          TextButton(
            onPressed: controller.saveRecord,
            child: const Text('保存'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: controller.formKey,
          child: Column(
            children: [
              // 标题输入
              TextFormField(
                controller: controller.titleController,
                decoration: const InputDecoration(
                  labelText: '标题',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return '请输入标题';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // 内容输入
              TextFormField(
                controller: controller.contentController,
                decoration: const InputDecoration(
                  labelText: '内容',
                  border: OutlineInputBorder(),
                ),
                maxLines: 5,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return '请输入内容';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // 图片选择
              Obx(() => ImagePickerGrid(
                images: controller.selectedImages,
                onAdd: controller.pickImage,
                onRemove: controller.removeImage,
                maxCount: 9,
              )),

              // 类型选择
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: controller.selectedType.value,
                decoration: const InputDecoration(
                  labelText: '类型',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'daily', child: Text('日常')),
                  DropdownMenuItem(value: 'health', child: Text('健康')),
                  DropdownMenuItem(value: 'event', child: Text('事件')),
                  DropdownMenuItem(value: 'note', child: Text('笔记')),
                ],
                onChanged: (value) => controller.selectedType.value = value!,
              ),
            ],
          ),
        ),
      ),
    );
  }
} 