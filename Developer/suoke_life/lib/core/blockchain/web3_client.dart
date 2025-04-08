import 'dart:io';
import 'package:flutter/services.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:web3dart/web3dart.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/io.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

/// Web3客户端服务，用于连接以太坊网络并与智能合约交互
class Web3Client {
  late web3dart.Web3Client _client;
  late EthereumAddress _defaultAccount;
  late Credentials _credentials;
  
  // 合约地址
  late EthereumAddress _healthRecordAddress;
  late EthereumAddress _healthDataTokenAddress;
  
  // 合约ABI
  late DeployedContract _healthRecordContract;
  late DeployedContract _healthDataTokenContract;
  
  // 是否已初始化
  bool _isInitialized = false;
  
  /// 初始化Web3客户端
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    // 从环境变量获取RPC URL和私钥
    final rpcUrl = dotenv.env['ETH_RPC_URL'] ?? 'http://127.0.0.1:7545';
    final wsUrl = dotenv.env['ETH_WS_URL'] ?? 'ws://127.0.0.1:7545';
    final privateKey = dotenv.env['ETH_PRIVATE_KEY'] ?? '';
    
    // 创建Web3客户端
    final httpClient = http.Client();
    final wsClient = IOWebSocketChannel.connect(wsUrl).cast<String>();
    _client = web3dart.Web3Client(rpcUrl, httpClient, socketConnector: () => wsClient);
    
    // 设置默认账户
    _credentials = EthPrivateKey.fromHex(privateKey);
    _defaultAccount = await _credentials.extractAddress();
    
    // 从环境变量获取合约地址
    final healthRecordAddressStr = dotenv.env['HEALTH_RECORD_ADDRESS'] ?? '0xDdDd9a53Fb2D9c8d62E21827559183D52Cadd357';
    final healthDataTokenAddressStr = dotenv.env['HEALTH_DATA_TOKEN_ADDRESS'] ?? '0x4a58DE0Ec653a049ebc37dE6b063841d58D50Aee';
    
    _healthRecordAddress = EthereumAddress.fromHex(healthRecordAddressStr);
    _healthDataTokenAddress = EthereumAddress.fromHex(healthDataTokenAddressStr);
    
    // 加载合约ABI
    await _loadContracts();
    
    _isInitialized = true;
  }
  
  /// 加载合约ABI
  Future<void> _loadContracts() async {
    // 检查是否已保存到本地文件系统
    final healthRecordAbi = await _loadContractAbi('HealthRecord.json');
    final healthDataTokenAbi = await _loadContractAbi('HealthDataToken.json');
    
    // 创建合约实例
    _healthRecordContract = DeployedContract(
      ContractAbi.fromJson(healthRecordAbi, 'HealthRecord'), 
      _healthRecordAddress
    );
    
    _healthDataTokenContract = DeployedContract(
      ContractAbi.fromJson(healthDataTokenAbi, 'HealthDataToken'), 
      _healthDataTokenAddress
    );
  }
  
  /// 从本地加载合约ABI，如果不存在则从assets加载
  Future<String> _loadContractAbi(String fileName) async {
    try {
      // 优先从文件系统加载
      final directory = await getApplicationDocumentsDirectory();
      final file = File(path.join(directory.path, 'contracts', fileName));
      
      if (await file.exists()) {
        return await file.readAsString();
      }
      
      // 从assets加载
      final abiJson = await rootBundle.loadString('assets/contracts/$fileName');
      
      // 保存到文件系统
      await file.parent.create(recursive: true);
      await file.writeAsString(abiJson);
      
      return abiJson;
    } catch (e) {
      // 如果加载失败，尝试直接从assets加载
      return await rootBundle.loadString('assets/contracts/$fileName');
    }
  }
  
  /// 获取默认账户地址
  Future<String> getDefaultAccountAddress() async {
    await _ensureInitialized();
    return _defaultAccount.hex;
  }
  
  /// 获取账户余额（以太坊）
  Future<EtherAmount> getAccountBalance(String address) async {
    await _ensureInitialized();
    final ethAddress = EthereumAddress.fromHex(address);
    return await _client.getBalance(ethAddress);
  }
  
  /// 获取健康数据代币余额
  Future<BigInt> getTokenBalance(String address) async {
    await _ensureInitialized();
    final ethAddress = EthereumAddress.fromHex(address);
    final function = _healthDataTokenContract.function('balanceOf');
    final result = await _client.call(
      contract: _healthDataTokenContract,
      function: function,
      params: [ethAddress],
    );
    return result.first as BigInt;
  }
  
  /// 创建健康记录
  Future<String> createHealthRecord(String dataHash, String dataUrl) async {
    await _ensureInitialized();
    final function = _healthRecordContract.function('createRecord');
    final result = await _client.sendTransaction(
      _credentials,
      Transaction.callContract(
        contract: _healthRecordContract,
        function: function,
        parameters: [dataHash, dataUrl],
      ),
    );
    return result;
  }
  
  /// 共享健康记录
  Future<String> shareHealthRecord(BigInt recordId, String toAddress) async {
    await _ensureInitialized();
    final function = _healthRecordContract.function('shareRecord');
    final result = await _client.sendTransaction(
      _credentials,
      Transaction.callContract(
        contract: _healthRecordContract,
        function: function,
        parameters: [recordId, EthereumAddress.fromHex(toAddress)],
      ),
    );
    return result;
  }
  
  /// 获取健康记录
  Future<List<dynamic>> getHealthRecord(BigInt recordId) async {
    await _ensureInitialized();
    final function = _healthRecordContract.function('getRecord');
    final result = await _client.call(
      contract: _healthRecordContract,
      function: function,
      params: [recordId],
    );
    return result;
  }
  
  /// 检查是否已经初始化
  Future<void> _ensureInitialized() async {
    if (!_isInitialized) {
      await initialize();
    }
  }
  
  /// 关闭客户端连接
  void dispose() {
    _client.dispose();
  }
}