import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/user.dart';

class EditProfileController extends GetxController {
  final SuokeService suokeService;
  final isLoading = false.obs;
  final avatarUrl = RxnString();

  late final TextEditingController nameController;
  late final TextEditingController emailController;
  late final TextEditingController phoneController;
  late final TextEditingController bioController;

  EditProfileController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    final user = Get.arguments as User;
    
    nameController = TextEditingController(text: user.name);
    emailController = TextEditingController(text: user.email);
    phoneController = TextEditingController(text: user.phone);
    bioController = TextEditingController(text: user.bio);
    avatarUrl.value = user.avatarUrl;
  }

  @override
  void onClose() {
    nameController.dispose();
    emailController.dispose();
    phoneController.dispose();
    bioController.dispose();
    super.onClose();
  }

  Future<void> changeAvatar() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.gallery);
    
    if (image != null) {
      try {
        isLoading.value = true;
        final url = await suokeService.uploadAvatar(image.path);
        avatarUrl.value = url;
      } catch (e) {
        Get.snackbar('错误', '上传头像失败');
      } finally {
        isLoading.value = false;
      }
    }
  }

  Future<void> saveProfile() async {
    try {
      isLoading.value = true;
      
      final updatedUser = User(
        id: Get.arguments.id,
        name: nameController.text,
        email: emailController.text,
        phone: phoneController.text,
        bio: bioController.text,
        avatarUrl: avatarUrl.value,
      );

      await suokeService.updateUser(updatedUser);
      Get.back(result: updatedUser);
      Get.snackbar('成功', '个人资料已更新');
    } catch (e) {
      Get.snackbar('错误', '保存失败');
    } finally {
      isLoading.value = false;
    }
  }
} 