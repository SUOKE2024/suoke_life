import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/ai_agents/rag/hybrid_rag_service.dart';
import 'package:suoke_life/ai_agents/rag/tcm_specialized_rag.dart';
import 'package:suoke_life/core/models/rag_result.dart';
import 'package:suoke_life/core/services/network_service.dart';
import 'package:suoke_life/domain/entities/constitution_data.dart';
import 'package:suoke_life/domain/entities/user_profile.dart';
import 'package:suoke_life/presentation/common/widgets/custom_app_bar.dart';
import 'package:suoke_life/presentation/common/widgets/loading_indicator.dart';
import 'package:suoke_life/presentation/common/widgets/rag_result_card.dart';

// RAG搜索控制器提供者
final ragSearchControllerProvider =
    StateNotifierProvider.autoDispose<RagSearchController, RagSearchState>(
        (ref) {
  final hybridRagService = ref.watch(hybridRagServiceProvider);
  final tcmRagService = ref.watch(tcmRagServiceProvider);
  final networkService = ref.watch(networkServiceProvider);

  return RagSearchController(
    hybridRagService: hybridRagService,
    tcmRagService: tcmRagService,
    networkService: networkService,
  );
});

// RAG搜索状态
class RagSearchState {
  final bool isLoading;
  final String? error;
  final List<RagResult> results;
  final String currentQuery;
  final RagStrategy currentStrategy;
  final String searchMode;

  RagSearchState({
    this.isLoading = false,
    this.error,
    this.results = const [],
    this.currentQuery = '',
    this.currentStrategy = RagStrategy.adaptive,
    this.searchMode = '通用搜索',
  });

  RagSearchState copyWith({
    bool? isLoading,
    String? error,
    List<RagResult>? results,
    String? currentQuery,
    RagStrategy? currentStrategy,
    String? searchMode,
  }) {
    return RagSearchState(
      isLoading: isLoading ?? this.isLoading,
      error: error,
      results: results ?? this.results,
      currentQuery: currentQuery ?? this.currentQuery,
      currentStrategy: currentStrategy ?? this.currentStrategy,
      searchMode: searchMode ?? this.searchMode,
    );
  }
}

// RAG搜索控制器
class RagSearchController extends StateNotifier<RagSearchState> {
  final HybridRagService hybridRagService;
  final TCMRagService tcmRagService;
  final NetworkService networkService;

  RagSearchController({
    required this.hybridRagService,
    required this.tcmRagService,
    required this.networkService,
  }) : super(RagSearchState());

  // 执行通用搜索
  Future<void> search(String query) async {
    if (query.trim().isEmpty) return;

    state = state.copyWith(
      isLoading: true,
      currentQuery: query,
      error: null,
      searchMode: '通用搜索',
    );

    try {
      final results = await hybridRagService.query(
        query,
        strategy: state.currentStrategy,
      );

      state = state.copyWith(
        isLoading: false,
        results: results,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '搜索失败: $e',
      );
    }
  }

  // 执行体质相关搜索
  Future<void> searchByConstitution(
      String query, ConstitutionData constitutionData) async {
    if (query.trim().isEmpty) return;

    state = state.copyWith(
      isLoading: true,
      currentQuery: query,
      error: null,
      searchMode: '体质相关搜索',
    );

    try {
      final results =
          await tcmRagService.queryByConstitution(query, constitutionData);

      state = state.copyWith(
        isLoading: false,
        results: results,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '搜索失败: $e',
      );
    }
  }

  // 执行症状相关搜索
  Future<void> searchBySymptoms(
      String query, List<String> symptoms, UserProfile? userProfile) async {
    if (query.trim().isEmpty) return;

    state = state.copyWith(
      isLoading: true,
      currentQuery: query,
      error: null,
      searchMode: '症状相关搜索',
    );

    try {
      final results =
          await tcmRagService.queryBySymptoms(query, symptoms, userProfile);

      state = state.copyWith(
        isLoading: false,
        results: results,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '搜索失败: $e',
      );
    }
  }

  // 执行养生食疗搜索
  Future<void> searchHealthRegimen(
    String query,
    UserProfile userProfile, {
    String? season,
    String? timeOfDay,
  }) async {
    if (query.trim().isEmpty) return;

    state = state.copyWith(
      isLoading: true,
      currentQuery: query,
      error: null,
      searchMode: '养生食疗搜索',
    );

    try {
      final results = await tcmRagService.queryHealthRegimen(
        query,
        userProfile,
        season: season,
        timeOfDay: timeOfDay,
      );

      state = state.copyWith(
        isLoading: false,
        results: results,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '搜索失败: $e',
      );
    }
  }

  // 执行方剂搜索
  Future<void> searchHerbalFormula(
    String query, {
    List<String>? herbs,
    String? symptom,
    UserProfile? userProfile,
  }) async {
    if (query.trim().isEmpty) return;

    state = state.copyWith(
      isLoading: true,
      currentQuery: query,
      error: null,
      searchMode: '方剂相关搜索',
    );

    try {
      final results = await tcmRagService.queryHerbalFormula(
        query,
        herbs: herbs,
        symptom: symptom,
        userProfile: userProfile,
      );

      state = state.copyWith(
        isLoading: false,
        results: results,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '搜索失败: $e',
      );
    }
  }

  // 更改搜索策略
  void changeStrategy(RagStrategy strategy) {
    state = state.copyWith(currentStrategy: strategy);
  }

  // 提交反馈
  Future<void> submitFeedback(String resultId, bool isHelpful) async {
    // 实际应用中应调用API提交反馈
    debugPrint('提交反馈: 结果ID=$resultId, 有用=$isHelpful');
  }

  // 清除错误
  void clearError() {
    state = state.copyWith(error: null);
  }
}

// 策略选择弹出菜单
class StrategyPopupMenu extends ConsumerWidget {
  const StrategyPopupMenu({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentStrategy = ref.watch(
        ragSearchControllerProvider.select((state) => state.currentStrategy));

    return PopupMenuButton<RagStrategy>(
      icon: const Icon(Icons.tune),
      tooltip: '搜索策略',
      onSelected: (strategy) {
        ref.read(ragSearchControllerProvider.notifier).changeStrategy(strategy);
      },
      itemBuilder: (context) => [
        PopupMenuItem(
          value: RagStrategy.adaptive,
          child: Row(
            children: [
              Icon(
                Icons.auto_awesome,
                color: currentStrategy == RagStrategy.adaptive
                    ? Theme.of(context).primaryColor
                    : null,
                size: 18,
              ),
              const SizedBox(width: 8),
              const Text('自适应策略'),
              if (currentStrategy == RagStrategy.adaptive)
                Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: Icon(
                    Icons.check,
                    color: Theme.of(context).primaryColor,
                    size: 18,
                  ),
                ),
            ],
          ),
        ),
        PopupMenuItem(
          value: RagStrategy.edgeFirst,
          child: Row(
            children: [
              Icon(
                Icons.phonelink,
                color: currentStrategy == RagStrategy.edgeFirst
                    ? Theme.of(context).primaryColor
                    : null,
                size: 18,
              ),
              const SizedBox(width: 8),
              const Text('本地优先'),
              if (currentStrategy == RagStrategy.edgeFirst)
                Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: Icon(
                    Icons.check,
                    color: Theme.of(context).primaryColor,
                    size: 18,
                  ),
                ),
            ],
          ),
        ),
        PopupMenuItem(
          value: RagStrategy.cloudFirst,
          child: Row(
            children: [
              Icon(
                Icons.cloud,
                color: currentStrategy == RagStrategy.cloudFirst
                    ? Theme.of(context).primaryColor
                    : null,
                size: 18,
              ),
              const SizedBox(width: 8),
              const Text('云端优先'),
              if (currentStrategy == RagStrategy.cloudFirst)
                Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: Icon(
                    Icons.check,
                    color: Theme.of(context).primaryColor,
                    size: 18,
                  ),
                ),
            ],
          ),
        ),
        PopupMenuItem(
          value: RagStrategy.hybrid,
          child: Row(
            children: [
              Icon(
                Icons.compare_arrows,
                color: currentStrategy == RagStrategy.hybrid
                    ? Theme.of(context).primaryColor
                    : null,
                size: 18,
              ),
              const SizedBox(width: 8),
              const Text('混合策略'),
              if (currentStrategy == RagStrategy.hybrid)
                Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: Icon(
                    Icons.check,
                    color: Theme.of(context).primaryColor,
                    size: 18,
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

// RAG搜索页面
@RoutePage()
class RagSearchPage extends ConsumerStatefulWidget {
  final String initialQuery;
  final String searchType;

  const RagSearchPage({
    Key? key,
    this.initialQuery = '',
    this.searchType = 'general',
  }) : super(key: key);

  @override
  ConsumerState<RagSearchPage> createState() => _RagSearchPageState();
}

class _RagSearchPageState extends ConsumerState<RagSearchPage> {
  late TextEditingController _searchController;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController(text: widget.initialQuery);

    // 如果有初始查询，执行搜索
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (widget.initialQuery.isNotEmpty) {
        _executeSearch();
      }
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  // 执行搜索
  void _executeSearch() {
    final query = _searchController.text.trim();
    if (query.isEmpty) return;

    switch (widget.searchType) {
      case 'general':
        ref.read(ragSearchControllerProvider.notifier).search(query);
        break;
      // 其他搜索类型在实际应用中实现
      default:
        ref.read(ragSearchControllerProvider.notifier).search(query);
    }
  }

  // 显示详细信息对话框
  void _showDetailDialog(RagResult result) {
    showDialog(
      context: context,
      builder: (context) => RagResultDetailDialog(
        result: result,
        onFeedback: (isHelpful) {
          ref
              .read(ragSearchControllerProvider.notifier)
              .submitFeedback(result.id, isHelpful);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(ragSearchControllerProvider);

    return Scaffold(
      appBar: CustomAppBar(
        title: const Text('知识检索'),
        actions: const [
          StrategyPopupMenu(),
        ],
      ),
      body: Column(
        children: [
          // 搜索框
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: '输入您的健康问题...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                  },
                ),
              ),
              textInputAction: TextInputAction.search,
              onSubmitted: (_) => _executeSearch(),
            ),
          ),

          // 当前搜索模式提示
          if (state.currentQuery.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                children: [
                  Text(
                    '当前模式: ${state.searchMode}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const Spacer(),
                  Text(
                    '搜索策略: ${_getStrategyName(state.currentStrategy)}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),

          // 错误信息
          if (state.error != null)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.error!,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.red),
                      onPressed: () {
                        ref
                            .read(ragSearchControllerProvider.notifier)
                            .clearError();
                      },
                    ),
                  ],
                ),
              ),
            ),

          // 加载中或结果列表
          Expanded(
            child: state.isLoading
                ? const Center(child: LoadingIndicator(message: '正在搜索...'))
                : state.results.isEmpty && state.currentQuery.isNotEmpty
                    ? _buildEmptyResults()
                    : _buildResultsList(state.results),
          ),
        ],
      ),
    );
  }

  // 构建空结果视图
  Widget _buildEmptyResults() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search_off,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '没有找到相关结果',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '尝试使用其他关键词或搜索策略',
            style: TextStyle(
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  // 构建结果列表
  Widget _buildResultsList(List<RagResult> results) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: results.length,
      itemBuilder: (context, index) {
        final result = results[index];
        return RagResultCard(
          result: result,
          showScore: true,
          onTap: () => _showDetailDialog(result),
          onFeedback: (isHelpful) {
            ref
                .read(ragSearchControllerProvider.notifier)
                .submitFeedback(result.id, isHelpful);
          },
        );
      },
    );
  }

  // 获取策略名称
  String _getStrategyName(RagStrategy strategy) {
    switch (strategy) {
      case RagStrategy.adaptive:
        return '自适应';
      case RagStrategy.edgeFirst:
        return '本地优先';
      case RagStrategy.cloudFirst:
        return '云端优先';
      case RagStrategy.hybrid:
        return '混合';
      default:
        return '未知';
    }
  }
}
