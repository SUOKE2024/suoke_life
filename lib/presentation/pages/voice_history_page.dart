import 'package:flutter/material.dart';
import 'package:shared_preferences.dart';
import 'package:timeago/timeago.dart' as timeago;
import '../../models/voice_record.dart';
import '../../services/voice_service.dart';

class VoiceHistoryPage extends StatefulWidget {
  const VoiceHistoryPage({super.key});

  @override
  State<VoiceHistoryPage> createState() => _VoiceHistoryPageState();
}

class _VoiceHistoryPageState extends State<VoiceHistoryPage> {
  late final VoiceService _voiceService;
  final _searchController = TextEditingController();
  List<VoiceRecord> _records = [];
  List<VoiceRecord> _filteredRecords = [];
  bool _isLoading = true;
  String _selectedType = 'all';

  @override
  void initState() {
    super.initState();
    _initializeService();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _initializeService() async {
    final prefs = await SharedPreferences.getInstance();
    _voiceService = VoiceService(
      nasBasePath: 'voice_records',
      prefs: prefs,
    );
    await _loadHistory();
  }

  void _filterRecords() {
    final searchText = _searchController.text.toLowerCase();
    setState(() {
      _filteredRecords = _records.where((record) {
        if (_selectedType != 'all' && record.type != _selectedType) {
          return false;
        }
        return record.content.toLowerCase().contains(searchText);
      }).toList();
    });
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);
    try {
      final records = await _voiceService.getVoiceHistory();
      setState(() => _records = records);
      _filterRecords();
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _playRecord(VoiceRecord record) async {
    await _voiceService.speak(record.content);
  }

  Widget _buildRecordItem(VoiceRecord record) {
    final theme = Theme.of(context);
    final isVoiceToText = record.type == 'voice_to_text';

    return Card(
      margin: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 4,
      ),
      child: ListTile(
        leading: Icon(
          isVoiceToText ? Icons.mic : Icons.volume_up,
          color: theme.colorScheme.primary,
        ),
        title: Text(record.content),
        subtitle: Text(
          timeago.format(record.timestamp, locale: 'zh'),
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.textTheme.bodySmall?.color?.withOpacity(0.6),
          ),
        ),
        trailing: IconButton(
          icon: const Icon(Icons.play_arrow),
          onPressed: () => _playRecord(record),
        ),
      ),
    );
  }

  Widget _buildFilterChip(String label, String value) {
    return FilterChip(
      label: Text(label),
      selected: _selectedType == value,
      onSelected: (selected) {
        setState(() => _selectedType = selected ? value : 'all');
        _filterRecords();
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('语音历史'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadHistory,
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: const InputDecoration(
                hintText: '搜索语音记录',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: (_) => _filterRecords(),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Wrap(
              spacing: 8,
              children: [
                _buildFilterChip('全部', 'all'),
                _buildFilterChip('语音转文字', 'voice_to_text'),
                _buildFilterChip('文字转语音', 'text_to_voice'),
              ],
            ),
          ),
          const Divider(height: 32),
          Expanded(
            child: _filteredRecords.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.history,
                          size: 64,
                          color: Colors.grey[400],
                        ),
                        const SizedBox(height: 16),
                        Text(
                          '暂无语音记录',
                          style: TextStyle(
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    itemCount: _filteredRecords.length,
                    itemBuilder: (context, index) => 
                        _buildRecordItem(_filteredRecords[index]),
                  ),
          ),
        ],
      ),
    );
  }
} 