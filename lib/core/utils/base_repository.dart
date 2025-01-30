/// Base repository class that provides common functionality for all repositories.
/// 
/// Features:
/// - Network operations
/// - Cache management
/// - Error handling
/// - Data validation
abstract class BaseRepository {
  final NetworkService _network;
  final StorageService _storage;

  BaseRepository(this._network, this._storage);

  /// Make a GET request
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    bool useCache = true,
    Duration cacheDuration = const Duration(minutes: 5),
  }) async {
    try {
      // Try to get from cache first
      if (useCache) {
        final cached = await _getFromCache<T>(path, queryParameters);
        if (cached != null) return cached;
      }

      // Make network request
      final response = await _network.get(
        path,
        queryParameters: queryParameters,
      );

      // Parse response
      final data = _parseResponse<T>(response);

      // Cache response
      if (useCache) {
        await _saveToCache(path, queryParameters, data, cacheDuration);
      }

      return data;
    } catch (e) {
      handleError(e);
      rethrow;
    }
  }

  /// Make a POST request
  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    bool invalidateCache = true,
  }) async {
    try {
      final response = await _network.post(
        path,
        data: data,
        queryParameters: queryParameters,
      );

      // Invalidate cache if needed
      if (invalidateCache) {
        await _invalidateCache(path);
      }

      return _parseResponse<T>(response);
    } catch (e) {
      handleError(e);
      rethrow;
    }
  }

  /// Make a PUT request
  Future<T> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    bool invalidateCache = true,
  }) async {
    try {
      final response = await _network.put(
        path,
        data: data,
        queryParameters: queryParameters,
      );

      // Invalidate cache if needed
      if (invalidateCache) {
        await _invalidateCache(path);
      }

      return _parseResponse<T>(response);
    } catch (e) {
      handleError(e);
      rethrow;
    }
  }

  /// Make a DELETE request
  Future<T> delete<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    bool invalidateCache = true,
  }) async {
    try {
      final response = await _network.delete(
        path,
        queryParameters: queryParameters,
      );

      // Invalidate cache if needed
      if (invalidateCache) {
        await _invalidateCache(path);
      }

      return _parseResponse<T>(response);
    } catch (e) {
      handleError(e);
      rethrow;
    }
  }

  /// Get data from cache
  Future<T?> _getFromCache<T>(
    String path,
    Map<String, dynamic>? queryParameters,
  ) async {
    final key = _getCacheKey(path, queryParameters);
    final cached = await _storage.get<Map<String, dynamic>>(key);
    
    if (cached != null) {
      final expiry = DateTime.parse(cached['expiry'] as String);
      if (expiry.isAfter(DateTime.now())) {
        return cached['data'] as T;
      }
    }
    return null;
  }

  /// Save data to cache
  Future<void> _saveToCache<T>(
    String path,
    Map<String, dynamic>? queryParameters,
    T data,
    Duration duration,
  ) async {
    final key = _getCacheKey(path, queryParameters);
    final expiry = DateTime.now().add(duration);
    
    await _storage.set(key, {
      'data': data,
      'expiry': expiry.toIso8601String(),
    });
  }

  /// Invalidate cache for a path
  Future<void> _invalidateCache(String path) async {
    final pattern = RegExp('^$path.*');
    await _storage.removeWhere((key) => pattern.hasMatch(key));
  }

  /// Generate cache key
  String _getCacheKey(String path, Map<String, dynamic>? queryParameters) {
    if (queryParameters?.isEmpty ?? true) return path;
    return '$path?${_serializeQueryParams(queryParameters!)}';
  }

  /// Serialize query parameters
  String _serializeQueryParams(Map<String, dynamic> params) {
    return params.entries
        .map((e) => '${e.key}=${e.value}')
        .join('&');
  }

  /// Parse API response
  T _parseResponse<T>(Response response) {
    try {
      if (response.data == null) {
        throw RepositoryException('Empty response data');
      }
      return response.data as T;
    } catch (e) {
      throw RepositoryException('Failed to parse response: $e');
    }
  }

  /// Handle repository errors
  void handleError(dynamic error) {
    LoggerService.error(
      'Repository error',
      error: error,
      context: runtimeType.toString(),
    );
  }

  /// Validate data
  void validateData<T>(T data) {
    if (data == null) {
      throw RepositoryException('Data cannot be null');
    }
  }
}

/// Repository exception
class RepositoryException implements Exception {
  final String message;
  RepositoryException(this.message);

  @override
  String toString() => 'RepositoryException: $message';
} 