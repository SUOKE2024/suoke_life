import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../models/user_profile.dart';
import '../services/auth_service.dart';
import 'dart:io';

class ProfileEditScreen extends StatefulWidget {
  final UserProfile profile;

  const ProfileEditScreen({
    Key? key,
    required this.profile,
  }) : super(key: key);

  @override
  State<ProfileEditScreen> createState() => _ProfileEditScreenState();
}

class _ProfileEditScreenState extends State<ProfileEditScreen> {
  final _formKey = GlobalKey<FormState>();
  final _authService = AuthService();
  bool _isLoading = false;
  File? _avatarFile;

  late final TextEditingController _nicknameController;
  late final TextEditingController _bioController;
  late final TextEditingController _locationController;
  late final TextEditingController _websiteController;

  DateTime? _selectedBirthday;
  String? _selectedGender;
  final List<String> _selectedInterests = [];

  final List<String> _availableInterests = [
    '探险',
    '摄影',
    '徒步',
    '收藏',
    '美食',
    '文化',
    '艺术',
    '音乐',
    '运动',
    '旅行',
    '手工',
    '园艺',
    '科技',
    '阅读',
  ];

  final List<String> _genderOptions = ['男', '女', '其他', '不愿透露'];

  @override
  void initState() {
    super.initState();
    _nicknameController = TextEditingController(text: widget.profile.nickname);
    _bioController = TextEditingController(text: widget.profile.bio);
    _locationController = TextEditingController(text: widget.profile.location);
    _websiteController = TextEditingController(text: widget.profile.website);
    _selectedBirthday = widget.profile.birthday;
    _selectedGender = widget.profile.gender;
    _selectedInterests.addAll(widget.profile.interests);
  }

  @override
  void dispose() {
    _nicknameController.dispose();
    _bioController.dispose();
    _locationController.dispose();
    _websiteController.dispose();
    super.dispose();
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    if (pickedFile != null) {
      setState(() {
        _avatarFile = File(pickedFile.path);
      });
    }
  }

  Future<void> _selectBirthday() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedBirthday ?? DateTime(2000),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );

    if (picked != null) {
      setState(() {
        _selectedBirthday = picked;
      });
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final updatedProfile = widget.profile.copyWith(
        nickname: _nicknameController.text,
        bio: _bioController.text,
        location: _locationController.text,
        website: _websiteController.text,
        birthday: _selectedBirthday,
        gender: _selectedGender,
        interests: _selectedInterests,
      );

      // TODO: 实现保存头像和个人资料的API调用

      if (!mounted) return;
      Navigator.of(context).pop(updatedProfile);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('保存失败：$e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('编辑个人资料'),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveProfile,
            child: _isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Text('保存'),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 头像
            Center(
              child: Stack(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundImage: _avatarFile != null
                        ? FileImage(_avatarFile!)
                        : (widget.profile.avatar != null
                            ? NetworkImage(widget.profile.avatar!)
                            : null) as ImageProvider?,
                    child: widget.profile.avatar == null && _avatarFile == null
                        ? const Icon(Icons.person, size: 50)
                        : null,
                  ),
                  Positioned(
                    right: 0,
                    bottom: 0,
                    child: CircleAvatar(
                      radius: 18,
                      backgroundColor: Theme.of(context).primaryColor,
                      child: IconButton(
                        icon: const Icon(Icons.camera_alt, size: 18),
                        color: Colors.white,
                        onPressed: _pickImage,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 基本信息
            _buildSection(
              '基本信息',
              [
                TextFormField(
                  controller: _nicknameController,
                  decoration: const InputDecoration(
                    labelText: '昵称',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return '请输入昵称';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _bioController,
                  decoration: const InputDecoration(
                    labelText: '个人简介',
                    prefixIcon: Icon(Icons.description_outlined),
                  ),
                  maxLines: 3,
                ),
              ],
            ),

            // 个人信息
            _buildSection(
              '个人信息',
              [
                ListTile(
                  leading: const Icon(Icons.cake_outlined),
                  title: const Text('生日'),
                  subtitle: Text(
                    _selectedBirthday != null
                        ? '${_selectedBirthday!.year}年${_selectedBirthday!.month}月${_selectedBirthday!.day}日'
                        : '未设置',
                  ),
                  onTap: _selectBirthday,
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.person_outline),
                  title: const Text('性别'),
                  subtitle: Text(_selectedGender ?? '未设置'),
                  onTap: () {
                    showDialog(
                      context: context,
                      builder: (context) => SimpleDialog(
                        title: const Text('选择性别'),
                        children: _genderOptions.map((gender) {
                          return SimpleDialogOption(
                            onPressed: () {
                              setState(() => _selectedGender = gender);
                              Navigator.pop(context);
                            },
                            child: Text(gender),
                          );
                        }).toList(),
                      ),
                    );
                  },
                ),
              ],
            ),

            // 位置信息
            _buildSection(
              '位置信息',
              [
                TextFormField(
                  controller: _locationController,
                  decoration: const InputDecoration(
                    labelText: '所在地',
                    prefixIcon: Icon(Icons.location_on_outlined),
                  ),
                ),
              ],
            ),

            // 联系方式
            _buildSection(
              '联系方式',
              [
                TextFormField(
                  controller: _websiteController,
                  decoration: const InputDecoration(
                    labelText: '个人网站',
                    prefixIcon: Icon(Icons.link),
                  ),
                ),
              ],
            ),

            // 兴趣标签
            _buildSection(
              '兴趣标签',
              [
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _availableInterests.map((interest) {
                    final isSelected = _selectedInterests.contains(interest);
                    return FilterChip(
                      label: Text(interest),
                      selected: isSelected,
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            _selectedInterests.add(interest);
                          } else {
                            _selectedInterests.remove(interest);
                          }
                        });
                      },
                    );
                  }).toList(),
                ),
              ],
            ),

            // 游戏统计
            _buildSection(
              '游戏统计',
              [
                ListTile(
                  leading: const Icon(Icons.stars_outlined),
                  title: const Text('等级'),
                  trailing: Text(
                    'Lv.${widget.profile.level}',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: LinearProgressIndicator(
                    value: widget.profile.levelProgress,
                    backgroundColor: Colors.grey[200],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    '距离下一级还需 ${widget.profile.expToNextLevel} 经验',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(0, 16, 0, 8),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
        ),
        ...children,
        const SizedBox(height: 8),
        const Divider(),
      ],
    );
  }
} 