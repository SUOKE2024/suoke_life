import 'package:flutter/material.dart';
import 'package:suoke_life/features/auth/pages/login_page.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('登录'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 一键登录按钮
            ElevatedButton(
              onPressed: () {
                // 实现一键登录逻辑
                _oneClickLogin();
              },
              style: ElevatedButton.styleFrom(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                primary: Colors.blue,
              ),
              child: const Text(
                '一键登录',
                style: TextStyle(color: Colors.white),
              ),
            ),
            const SizedBox(height: 20),
            // 第三方登录
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  icon: Image.asset('assets/icons/wechat.png'),
                  iconSize: 40,
                  onPressed: () {
                    // 实现微信登录逻辑
                    _loginWithWeChat();
                  },
                ),
                const SizedBox(width: 20),
                IconButton(
                  icon: Image.asset('assets/icons/douyin.png'),
                  iconSize: 40,
                  onPressed: () {
                    // 实现抖音登录逻辑
                    _loginWithDouyin();
                  },
                ),
                const SizedBox(width: 20),
                IconButton(
                  icon: Image.asset('assets/icons/xiaohongshu.png'),
                  iconSize: 40,
                  onPressed: () {
                    // 实现小红书登录逻辑
                    _loginWithXiaohongshu();
                  },
                ),
              ],
            ),
            const SizedBox(height: 40),
            // 用户信息设置卡片
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    CircleAvatar(
                      radius: 50,
                      backgroundImage: AssetImage('assets/images/default_avatar.png'),
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      decoration: InputDecoration(
                        hintText: '请输入昵称',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Radio(value: '男', groupValue: '性别', onChanged: (value) {}),
                        const Text('男'),
                        Radio(value: '女', groupValue: '性别', onChanged: (value) {}),
                        const Text('女'),
                      ],
                    ),
                    const SizedBox(height: 10),
                    ElevatedButton(
                      onPressed: () {
                        // 实现确定按钮逻辑
                        _confirmUserInfo();
                      },
                      style: ElevatedButton.styleFrom(
                        primary: Colors.blue,
                      ),
                      child: const Text(
                        '确定',
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _oneClickLogin() {
    // TODO: 实现一键登录逻辑
    print('一键登录成功');
  }

  void _loginWithWeChat() {
    // TODO: 实现微信登录逻辑
    print('微信登录成功');
  }

  void _loginWithDouyin() {
    // TODO: 实现抖音登录逻辑
    print('抖音登录成功');
  }

  void _loginWithXiaohongshu() {
    // TODO: 实现小红书登录逻辑
    print('小红书登录成功');
  }

  void _confirmUserInfo() {
    // TODO: 实现用户信息确认逻辑
    print('用户信息已确认');
  }
} 