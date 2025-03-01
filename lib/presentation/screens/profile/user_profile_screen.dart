import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

import '../../../domain/entities/user.dart';
import '../../../presentation/providers/auth_providers.dart';
import '../../../presentation/providers/user_providers.dart';
import '../../widgets/form/form_field_wrapper.dart';
import '../../widgets/loading_overlay.dart';

@RoutePage()
class UserProfileScreen extends ConsumerStatefulWidget {
  const UserProfileScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<UserProfileScreen> createState() => _UserProfileScreenState();
}

class _UserProfileScreenState extends ConsumerState<UserProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  File? _selectedImage;
  bool _isLoading = false;
  bool _isEditing = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  // 加载用户数据
  Future<void> _loadUserData() async {
    final user = ref.read(currentUserProvider).value;
    if (user != null) {
      _usernameController.text = user.username;
      _emailController.text = user.email ?? '';
      _phoneController.text = user.phoneNumber ?? '';
    }
  }

  // 保存用户资料
  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final currentUser = ref.read(currentUserProvider).value;
      if (currentUser == null) {
        throw Exception('当前用户不存在');
      }

      // 创建更新后的用户对象
      final updatedUser = currentUser.copyWith(
        username: _usernameController.text,
        email: _emailController.text.isEmpty ? null : _emailController.text,
        phoneNumber: _phoneController.text.isEmpty ? null : _phoneController.text,
      );

      // 更新用户资料
      final success = await ref.read(userProfileProvider.notifier).updateUserProfile(
            updatedUser,
            _selectedImage,
          );

      if (success) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('个人资料更新成功')),
          );
          setState(() {
            _isEditing = false;
          });
        }
      } else {
        setState(() {
          _errorMessage = '更新资料失败，请稍后重试';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = '更新资料时发生错误: ${e.toString()}';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  // 选择头像图片
  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 800,
      maxHeight: 800,
      imageQuality: 85,
    );

    if (image != null) {
      setState(() {
        _selectedImage = File(image.path);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final userAsync = ref.watch(currentUserProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('个人资料'),
        centerTitle: true,
        actions: [
          // 编辑/保存按钮
          if (!_isEditing)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () {
                setState(() {
                  _isEditing = true;
                });
              },
              tooltip: '编辑',
            )
          else
            IconButton(
              icon: const Icon(Icons.save),
              onPressed: _isLoading ? null : _saveProfile,
              tooltip: '保存',
            ),
        ],
      ),
      body: userAsync.when(
        data: (user) {
          if (user == null) {
            return const Center(
              child: Text('用户未登录'),
            );
          }
          
          return _buildUserProfileForm(context, user, theme);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('加载用户数据失败: $error'),
        ),
      ),
    );
  }

  Widget _buildUserProfileForm(BuildContext context, User user, ThemeData theme) {
    return LoadingOverlay(
      isLoading: _isLoading,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 头像区域
              _buildAvatarSection(user, theme),
              
              const SizedBox(height: 32),
              
              // 错误信息
              if (_errorMessage != null)
                _buildErrorMessage(),
              
              // 用户信息表单
              _buildUserInfoForm(theme, user),
              
              const SizedBox(height: 32),
              
              // 编辑模式按钮
              if (_isEditing) _buildEditModeButtons(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatarSection(User user, ThemeData theme) {
    return Center(
      child: Stack(
        children: [
          // 头像
          GestureDetector(
            onTap: _isEditing ? _pickImage : null,
            child: CircleAvatar(
              radius: 60,
              backgroundColor: Colors.grey.shade200,
              backgroundImage: _selectedImage != null
                  ? FileImage(_selectedImage!)
                  : (user.avatarUrl != null
                      ? NetworkImage(user.avatarUrl!)
                      : null) as ImageProvider?,
              child: (user.avatarUrl == null && _selectedImage == null)
                  ? Icon(
                      Icons.person,
                      size: 60,
                      color: Colors.grey.shade400,
                    )
                  : null,
            ),
          ),
          
          // 编辑图标
          if (_isEditing)
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: theme.primaryColor,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.camera_alt,
                  color: Colors.white,
                  size: 20,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildErrorMessage() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.red.shade50,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.red.shade200),
        ),
        child: Text(
          _errorMessage!,
          style: TextStyle(color: Colors.red.shade800),
        ),
      ),
    );
  }

  Widget _buildUserInfoForm(ThemeData theme, User user) {
    return Column(
      children: [
        // 用户名
        FormFieldWrapper(
          label: '用户名',
          child: TextFormField(
            controller: _usernameController,
            decoration: const InputDecoration(
              hintText: '请输入用户名',
              prefixIcon: Icon(Icons.person_outline),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入用户名';
              }
              return null;
            },
            enabled: _isEditing,
          ),
        ),
        const SizedBox(height: 16),
        
        // 电子邮箱
        FormFieldWrapper(
          label: '电子邮箱',
          child: TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(
              hintText: '请输入电子邮箱',
              prefixIcon: Icon(Icons.email_outlined),
            ),
            keyboardType: TextInputType.emailAddress,
            validator: (value) {
              if (value != null && value.isNotEmpty) {
                // 简单的邮箱格式验证
                final emailRegex = RegExp(
                  r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                );
                if (!emailRegex.hasMatch(value)) {
                  return '请输入有效的电子邮箱';
                }
              }
              return null;
            },
            enabled: _isEditing,
          ),
        ),
        const SizedBox(height: 16),
        
        // 手机号码
        FormFieldWrapper(
          label: '手机号码',
          child: TextFormField(
            controller: _phoneController,
            decoration: const InputDecoration(
              hintText: '请输入手机号码',
              prefixIcon: Icon(Icons.phone_outlined),
            ),
            keyboardType: TextInputType.phone,
            validator: (value) {
              if (value != null && value.isNotEmpty) {
                // 简单的手机号码格式验证（中国）
                final phoneRegex = RegExp(r'^1[3-9]\d{9}$');
                if (!phoneRegex.hasMatch(value)) {
                  return '请输入有效的手机号码';
                }
              }
              return null;
            },
            enabled: _isEditing,
          ),
        ),
        const SizedBox(height: 16),
        
        // 用户角色信息
        FormFieldWrapper(
          label: '用户角色',
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 14,
            ),
            decoration: BoxDecoration(
              color: theme.brightness == Brightness.dark
                  ? Colors.grey.shade800
                  : Colors.grey.shade100,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.admin_panel_settings_outlined),
                const SizedBox(width: 12),
                Text(
                  user.isAdmin ? '管理员' : '普通用户',
                  style: theme.textTheme.bodyMedium,
                ),
                if (user.isAdmin)
                  Padding(
                    padding: const EdgeInsets.only(left: 8),
                    child: Icon(
                      Icons.verified,
                      size: 16,
                      color: theme.primaryColor,
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        
        // 账号状态信息
        FormFieldWrapper(
          label: '账号状态',
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 14,
            ),
            decoration: BoxDecoration(
              color: theme.brightness == Brightness.dark
                  ? Colors.grey.shade800
                  : Colors.grey.shade100,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Icon(
                  user.isVerified
                      ? Icons.verified_user_outlined
                      : Icons.pending_outlined,
                  color: user.isVerified
                      ? Colors.green
                      : Colors.orange,
                ),
                const SizedBox(width: 12),
                Text(
                  user.isVerified ? '已验证' : '待验证',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: user.isVerified
                        ? Colors.green
                        : Colors.orange,
                  ),
                ),
              ],
            ),
          ),
        ),
        
        // 注册时间信息
        if (user.createdAt != null)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: FormFieldWrapper(
              label: '注册时间',
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 14,
                ),
                decoration: BoxDecoration(
                  color: theme.brightness == Brightness.dark
                      ? Colors.grey.shade800
                      : Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.calendar_today_outlined),
                    const SizedBox(width: 12),
                    Text(
                      _formatDate(user.createdAt!),
                      style: theme.textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildEditModeButtons() {
    return Column(
      children: [
        // 保存按钮
        SizedBox(
          width: double.infinity,
          height: 54,
          child: ElevatedButton(
            onPressed: _isLoading ? null : _saveProfile,
            style: ElevatedButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: _isLoading
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Text('保存更改'),
          ),
        ),
        
        const SizedBox(height: 16),
        
        // 取消按钮
        SizedBox(
          width: double.infinity,
          height: 54,
          child: OutlinedButton(
            onPressed: _isLoading
                ? null
                : () {
                    // 重新加载用户数据，取消编辑
                    _loadUserData();
                    setState(() {
                      _isEditing = false;
                      _selectedImage = null;
                      _errorMessage = null;
                    });
                  },
            style: OutlinedButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text('取消'),
          ),
        ),
      ],
    );
  }
  
  // 格式化日期
  String _formatDate(DateTime date) {
    return '${date.year}年${date.month}月${date.day}日';
  }
}