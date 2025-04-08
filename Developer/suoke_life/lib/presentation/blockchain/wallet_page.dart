import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/blockchain/blockchain_service.dart';
import 'package:suoke_life/di/providers.dart';

class WalletPage extends ConsumerStatefulWidget {
  const WalletPage({Key? key}) : super(key: key);

  @override
  ConsumerState<WalletPage> createState() => _WalletPageState();
}

class _WalletPageState extends ConsumerState<WalletPage> {
  final _privateKeyController = TextEditingController();
  bool _isImporting = false;

  @override
  void dispose() {
    _privateKeyController.dispose();
    super.dispose();
  }

  void _importWallet() async {
    if (_privateKeyController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入私钥')),
      );
      return;
    }

    setState(() {
      _isImporting = true;
    });

    try {
      await ref.read(blockchainServiceProvider).setCurrentAddress(_privateKeyController.text);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('钱包导入成功')),
        );
        _privateKeyController.clear();
        setState(() {});
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('导入失败: ${e.toString()}')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isImporting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final walletAddressAsync = ref.watch(currentWalletAddressProvider);
    final tokenBalanceAsync = ref.watch(tokenBalanceProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('健康数据钱包'),
        backgroundColor: const Color(0xFF35BB78),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 钱包卡片
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF35BB78), Color(0xFF2D996A)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'HDT 代币',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    walletAddressAsync.when(
                      data: (address) {
                        if (address == null) {
                          return const Text(
                            '未导入钱包',
                            style: TextStyle(color: Colors.white70),
                          );
                        }
                        
                        return Text(
                          '地址: ${address.substring(0, 10)}...${address.substring(address.length - 8)}',
                          style: const TextStyle(color: Colors.white70),
                        );
                      },
                      loading: () => const CircularProgressIndicator(
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                      error: (error, stack) => Text(
                        '加载地址失败: $error',
                        style: const TextStyle(color: Colors.white70),
                      ),
                    ),
                    const SizedBox(height: 20),
                    Row(
                      children: [
                        const Icon(
                          Icons.account_balance_wallet,
                          color: Colors.white,
                          size: 30,
                        ),
                        const SizedBox(width: 10),
                        tokenBalanceAsync.when(
                          data: (balance) {
                            // 将BigInt转换为双精度浮点数
                            final ethValue = balance / BigInt.from(10).pow(18);
                            return Text(
                              '$ethValue HDT',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                              ),
                            );
                          },
                          loading: () => const CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                          error: (error, stack) => const Text(
                            '--',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 20),
            
            // 导入钱包
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '导入钱包',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      '请输入您的私钥以导入现有钱包，注意：请不要在不安全的环境中暴露您的私钥',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey,
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _privateKeyController,
                      decoration: const InputDecoration(
                        labelText: '私钥',
                        border: OutlineInputBorder(),
                        hintText: '输入0x开头的私钥',
                      ),
                      obscureText: true,
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _isImporting ? null : _importWallet,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF35BB78),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: _isImporting
                            ? const CircularProgressIndicator()
                            : const Text(
                                '导入',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 16,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 20),
            
            // 功能区
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '健康数据',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    // 健康记录功能按钮
                    ListTile(
                      leading: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF35BB78).withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(
                          Icons.health_and_safety,
                          color: Color(0xFF35BB78),
                        ),
                      ),
                      title: const Text('我的健康记录'),
                      subtitle: const Text('查看和管理您的健康数据'),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                      onTap: () {
                        // 导航到健康记录页面
                      },
                    ),
                    const Divider(),
                    ListTile(
                      leading: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFF6800).withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(
                          Icons.share,
                          color: Color(0xFFFF6800),
                        ),
                      ),
                      title: const Text('共享健康数据'),
                      subtitle: const Text('安全地共享您的健康数据'),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                      onTap: () {
                        // 导航到数据共享页面
                      },
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
}
