import 'package:injectable/injectable.dart';
import '../../core/logger/app_logger.dart';
import '../../core/network/network_service.dart';

abstract class BaseService {
  final NetworkService _network;
  final AppLogger _logger;

  BaseService(this._network, this._logger);

  Future<T> handleRequest<T>(Future<T> Function() request) async {
    try {
      return await request();
    } catch (e, stack) {
      _logger.error('Request failed', e, stack);
      rethrow;
    }
  }

  NetworkService get network => _network;
  AppLogger get logger => _logger;
} 