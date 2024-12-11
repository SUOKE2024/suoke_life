import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../core/auth/models/auth_models.dart';
import '../../core/auth/services/auth_service.dart';
import '../../core/storage/services/file_storage_service.dart';

class ProfileEditPage extends StatefulWidget {
  const ProfileEditPage({super.key});

  @override
  State<ProfileEditPage> createState() => _ProfileEditPageState();
}

class _ProfileEditPageState extends State<ProfileEditPage> {
  final _nicknameController = TextEditingController();
  final _emailController = TextEditingController();
  final _authService = AuthService.instance;
  final _storageService = FileStorageService.instance;
  bool _isLoading = false;
  String? _avatarUrl;
  File? _avatarFile;
  double _uploadProgress = 0;

  @override
  void initState() {
    super.initState();
    _loadUserProfile();
  }

  @override
  void dispose() {
    _nicknameController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  void _loadUserProfile() {
    final profile = _authService.currentUser;
    if (profile != null) {
      _nicknameController.text = profile.nickname ?? '';
      _emailController.text = profile.email ?? '';
      _avatarUrl = profile.avatar;
    }
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 800,
      maxHeight: 800,
      imageQuality: 85,
    );
    
    if (image != null) {
      setState(() {
        _avatarFile = File(image.path);
        _uploadProgress = 0;
      });
      
      await _uploadAvatar();
    }
  }

  Future<void> _uploadAvatar() async {
    if (_avatarFile == null) return;

    try {
      setState(() => _isLoading = true);
      
      final url = await _storageService.uploadImage(
        file: _avatarFile!,
        onProgress: (sent, total) {
          setState(() {
            _uploadProgress = sent / total;
          });
        },
      );

      // 如果有旧头像,删除它
      if (_avatarUrl != null) {
        await _storageService.deleteFile(_avatarUrl!);
      }

      setState(() {
        _avatarUrl = url;
        _uploadProgress = 0;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('上传头像失败: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _saveProfile() async {
    if (_nicknameController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入昵称')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final currentUser = _authService.currentUser;
      if (currentUser == null) {
        throw Exception('用户未登录');
      }

      final updatedProfile = currentUser.copyWith(
        nickname: _nicknameController.text,
        email: _emailController.text.isEmpty ? null : _emailController.text,
        avatar: _avatarUrl,
      );

      await _authService.updateProfile(updatedProfile);
      
      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('保存成功')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('保存失败: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('编辑资料'),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveProfile,
            child: _isLoading
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Text('保存'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Center(
              child: Stack(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundImage: _avatarFile != null
                        ? FileImage(_avatarFile!)
                        : _avatarUrl != null
                            ? NetworkImage(_avatarUrl!) as ImageProvider
                            : null,
                    child: _avatarFile == null && _avatarUrl == null
                        ? const Icon(Icons.person, size: 50)
                        : null,
                  ),
                  if (_uploadProgress > 0 && _uploadProgress < 1)
                    Positioned.fill(
                      child: CircularProgressIndicator(
                        value: _uploadProgress,
                        backgroundColor: Colors.white.withOpacity(0.5),
                      ),
                    ),
                  Positioned(
                    right: 0,
                    bottom: 0,
                    child: CircleAvatar(
                      radius: 18,
                      backgroundColor: Theme.of(context).colorScheme.primary,
                      child: IconButton(
                        icon: const Icon(
                          Icons.camera_alt,
                          size: 18,
                          color: Colors.white,
                        ),
                        onPressed: _isLoading ? null : _pickImage,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _nicknameController,
              decoration: const InputDecoration(
                labelText: '昵称',
                border: OutlineInputBorder(),
              ),
              maxLength: 20,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(
                labelText: '邮箱(选填)',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
          ],
        ),
      ),
    );
  }
} 