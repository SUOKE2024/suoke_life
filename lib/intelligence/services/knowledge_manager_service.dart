class KnowledgeManagerService extends GetxService {
  final StorageService _storageService;
  final SecurityManagerService _securityManager;
  final ValidationService _validator;
  final SubscriptionService _subscriptionService;
  final EventTrackingService _eventTracking;
  
  // 知识库配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _knowledgeConfig = {
    SubscriptionPlan.basic: {
      'max_documents': 100,
      'max_file_size': 5 * 1024 * 1024,  // 5MB
      'allowed_types': {'text', 'markdown'},
      'features': {'basic_search', 'tags'},
    },
    SubscriptionPlan.pro: {
      'max_documents': 1000,
      'max_file_size': 20 * 1024 * 1024,  // 20MB
      'allowed_types': {'text', 'markdown', 'pdf', 'doc'},
      'features': {'basic_search', 'advanced_search', 'tags', 'categories'},
    },
    SubscriptionPlan.premium: {
      'max_documents': -1,  // 无限制
      'max_file_size': 100 * 1024 * 1024,  // 100MB
      'allowed_types': {'text', 'markdown', 'pdf', 'doc', 'docx', 'csv', 'json'},
      'features': {'basic_search', 'advanced_search', 'semantic_search', 'tags', 'categories', 'custom_fields'},
    },
  };
  
  // 知识库缓存
  final Map<String, Map<String, KnowledgeDocument>> _documentCache = {};
  final Map<String, Map<String, KnowledgeCollection>> _collectionCache = {};
  
  KnowledgeManagerService({
    required StorageService storageService,
    required SecurityManagerService securityManager,
    required ValidationService validator,
    required SubscriptionService subscriptionService,
    required EventTrackingService eventTracking,
  })  : _storageService = storageService,
        _securityManager = securityManager,
        _validator = validator,
        _subscriptionService = subscriptionService,
        _eventTracking = eventTracking;

  Future<KnowledgeDocument> addDocument(
    String content,
    String title, {
    required String userId,
    required String collectionId,
    String? type,
    List<String>? tags,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 验证权限
      if (!_canAddDocument(userId)) {
        throw AIException(
          '已达到文档数量上限',
          code: 'DOCUMENT_LIMIT_EXCEEDED',
        );
      }

      // 验证内容
      final validationResult = await _validator.validate(
        content,
        'knowledge_content',
        userId: userId,
      );
      if (!validationResult.isValid) {
        throw AIException(
          '文档内容无效',
          code: 'INVALID_DOCUMENT_CONTENT',
          details: validationResult.errors,
        );
      }

      // 创建文档
      final document = KnowledgeDocument(
        id: 'doc_${DateTime.now().millisecondsSinceEpoch}',
        title: title,
        content: validationResult.sanitizedData,
        type: type ?? 'text',
        collectionId: collectionId,
        userId: userId,
        tags: tags,
        metadata: metadata,
      );

      // 保存文档
      await _saveDocument(document);
      
      // 更新缓存
      _updateDocumentCache(document);

      // 记录事件
      await _trackKnowledgeEvent(
        'document_added',
        userId,
        documentId: document.id,
        collectionId: collectionId,
      );

      return document;
    } catch (e) {
      throw AIException(
        '添加文档失败',
        code: 'ADD_DOCUMENT_ERROR',
        details: e,
      );
    }
  }

  Future<KnowledgeCollection> createCollection(
    String name,
    String description, {
    required String userId,
    List<String>? tags,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 创建集合
      final collection = KnowledgeCollection(
        id: 'col_${DateTime.now().millisecondsSinceEpoch}',
        name: name,
        description: description,
        userId: userId,
        tags: tags,
        metadata: metadata,
      );

      // 保存集合
      await _saveCollection(collection);
      
      // 更新缓存
      _updateCollectionCache(collection);

      // 记录事件
      await _trackKnowledgeEvent(
        'collection_created',
        userId,
        collectionId: collection.id,
      );

      return collection;
    } catch (e) {
      throw AIException(
        '创建集合失败',
        code: 'CREATE_COLLECTION_ERROR',
        details: e,
      );
    }
  }

  Future<List<KnowledgeDocument>> searchDocuments(
    String query, {
    required String userId,
    String? collectionId,
    List<String>? tags,
    SearchOptions? options,
  }) async {
    try {
      final searchType = _getSearchType();
      
      switch (searchType) {
        case 'semantic_search':
          return await _semanticSearch(query, userId, collectionId, tags, options);
        case 'advanced_search':
          return await _advancedSearch(query, userId, collectionId, tags, options);
        default:
          return await _basicSearch(query, userId, collectionId, tags, options);
      }
    } catch (e) {
      throw AIException(
        '搜索文档失败',
        code: 'SEARCH_DOCUMENTS_ERROR',
        details: e,
      );
    }
  }

  Future<void> updateDocument(
    KnowledgeDocument document, {
    required String userId,
  }) async {
    try {
      // 验证权限
      if (!_canModifyDocument(document, userId)) {
        throw AIException(
          '无权修改此文档',
          code: 'DOCUMENT_MODIFY_DENIED',
        );
      }

      // 验证内容
      final validationResult = await _validator.validate(
        document.content,
        'knowledge_content',
        userId: userId,
      );
      if (!validationResult.isValid) {
        throw AIException(
          '文档内容无效',
          code: 'INVALID_DOCUMENT_CONTENT',
          details: validationResult.errors,
        );
      }

      // 更新文档
      await _saveDocument(document.copyWith(
        content: validationResult.sanitizedData,
      ));
      
      // 更新缓存
      _updateDocumentCache(document);

      // 记录事件
      await _trackKnowledgeEvent(
        'document_updated',
        userId,
        documentId: document.id,
        collectionId: document.collectionId,
      );
    } catch (e) {
      throw AIException(
        '更新文档失败',
        code: 'UPDATE_DOCUMENT_ERROR',
        details: e,
      );
    }
  }

  Future<void> deleteDocument(
    String documentId, {
    required String userId,
  }) async {
    try {
      final document = await getDocument(documentId, userId: userId);
      
      // 验证权限
      if (!_canModifyDocument(document, userId)) {
        throw AIException(
          '无权删除此文档',
          code: 'DOCUMENT_DELETE_DENIED',
        );
      }

      // 删除文档
      await _storageService.deleteDocument(documentId);
      
      // 从缓存移除
      _removeFromDocumentCache(documentId, userId);

      // 记录事件
      await _trackKnowledgeEvent(
        'document_deleted',
        userId,
        documentId: documentId,
        collectionId: document.collectionId,
      );
    } catch (e) {
      throw AIException(
        '删除文档失败',
        code: 'DELETE_DOCUMENT_ERROR',
        details: e,
      );
    }
  }

  String _getSearchType() {
    final plan = _subscriptionService.currentPlan;
    final features = _knowledgeConfig[plan]!['features'] as Set<String>;
    
    if (features.contains('semantic_search')) {
      return 'semantic_search';
    } else if (features.contains('advanced_search')) {
      return 'advanced_search';
    }
    return 'basic_search';
  }

  Future<List<KnowledgeDocument>> _semanticSearch(
    String query,
    String userId,
    String? collectionId,
    List<String>? tags,
    SearchOptions? options,
  ) async {
    // TODO: 实现语义搜索
    throw UnimplementedError();
  }

  Future<List<KnowledgeDocument>> _advancedSearch(
    String query,
    String userId,
    String? collectionId,
    List<String>? tags,
    SearchOptions? options,
  ) async {
    // TODO: 实现高级搜索
    throw UnimplementedError();
  }

  Future<List<KnowledgeDocument>> _basicSearch(
    String query,
    String userId,
    String? collectionId,
    List<String>? tags,
    SearchOptions? options,
  ) async {
    // TODO: 实现基础搜索
    throw UnimplementedError();
  }

  bool _canAddDocument(String userId) {
    final plan = _subscriptionService.currentPlan;
    final config = _knowledgeConfig[plan]!;
    final maxDocuments = config['max_documents'] as int;
    
    if (maxDocuments == -1) return true;
    
    final currentCount = _documentCache[userId]?.length ?? 0;
    return currentCount < maxDocuments;
  }

  bool _canModifyDocument(KnowledgeDocument document, String userId) {
    return document.userId == userId;
  }

  Future<void> _trackKnowledgeEvent(
    String action,
    String userId, {
    String? documentId,
    String? collectionId,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'knowledge_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      assistantName: 'system',
      type: AIEventType.knowledge,
      data: {
        'action': action,
        'document_id': documentId,
        'collection_id': collectionId,
      },
    ));
  }

  void _updateDocumentCache(KnowledgeDocument document) {
    _documentCache
      .putIfAbsent(document.userId, () => {})
      [document.id] = document;
  }

  void _updateCollectionCache(KnowledgeCollection collection) {
    _collectionCache
      .putIfAbsent(collection.userId, () => {})
      [collection.id] = collection;
  }

  void _removeFromDocumentCache(String documentId, String userId) {
    _documentCache[userId]?.remove(documentId);
  }

  Future<void> _saveDocument(KnowledgeDocument document) async {
    await _storageService.saveDocument(document);
  }

  Future<void> _saveCollection(KnowledgeCollection collection) async {
    await _storageService.saveCollection(collection);
  }
} 