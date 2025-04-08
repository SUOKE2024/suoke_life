import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/di/providers/blockchain_providers.dart';
import 'package:suoke_life/domain/entities/health_data_token.dart';
import 'package:suoke_life/domain/entities/health_record.dart';
import 'package:suoke_life/presentation/blockchain/widgets/account_info_card.dart';
import 'package:suoke_life/presentation/blockchain/widgets/create_health_record_form.dart';
import 'package:suoke_life/presentation/blockchain/widgets/health_records_list.dart';
import 'package:suoke_life/presentation/blockchain/widgets/token_info_card.dart';

/// 区块链页面
@RoutePage()
class BlockchainPage extends ConsumerStatefulWidget {
  const BlockchainPage({Key? key}) : super(key: key);

  @override
  ConsumerState<BlockchainPage> createState() => _BlockchainPageState();
}

class _BlockchainPageState extends ConsumerState<BlockchainPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('区块链健康数据'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.account_balance_wallet), text: '账户信息'),
            Tab(icon: Icon(Icons.add_circle), text: '创建记录'),
            Tab(icon: Icon(Icons.list), text: '健康记录'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          _AccountInfoTab(),
          _CreateHealthRecordTab(),
          _HealthRecordsTab(),
        ],
      ),
    );
  }
}

class _AccountInfoTab extends ConsumerWidget {
  const _AccountInfoTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final accountAddressAsync = ref.watch(currentAccountAddressProvider);
    
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          accountAddressAsync.when(
            data: (address) => AccountInfoCard(address: address),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, stackTrace) => Text('加载账户地址出错: $error'),
          ),
          const SizedBox(height: 24),
          const Text(
            '代币信息',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          ref.watch(tokenInfoProvider).when(
            data: (token) => TokenInfoCard(token: token),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, stackTrace) => Text('加载代币信息出错: $error'),
          ),
        ],
      ),
    );
  }
}

class _CreateHealthRecordTab extends ConsumerWidget {
  const _CreateHealthRecordTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return const Padding(
      padding: EdgeInsets.all(16.0),
      child: CreateHealthRecordForm(),
    );
  }
}

class _HealthRecordsTab extends ConsumerWidget {
  const _HealthRecordsTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final accountAddressAsync = ref.watch(currentAccountAddressProvider);
    
    return accountAddressAsync.when(
      data: (address) => Padding(
        padding: const EdgeInsets.all(16.0),
        child: HealthRecordsList(userAddress: address),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => Center(child: Text('加载账户地址出错: $error')),
    );
  }
}
