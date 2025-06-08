import React, { useState, useCallback } from 'react';
import {import { KnowledgeQuery } from '../../services/medKnowledgeService';
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Text,
  ScrollView,
  ActivityIndicator;
} from 'react-native';
interface KnowledgeSearchBarProps {
  onSearch: (query: KnowledgeQuery) => void;
  loading?: boolean;
  placeholder?: string;
  showFilters?: boolean;
}
export const KnowledgeSearchBar: React.FC<KnowledgeSearchBarProps> = ({
  onSearch,
  loading = false,
  placeholder = "搜索中医知识...",
  showFilters = true;
}) => {
  const [searchText, setSearchText] = useState('');
  const [selectedType, setSelectedType] = useState<KnowledgeQuery['type']>('general');
  const [showTypeSelector, setShowTypeSelector] = useState(false);
  const searchTypes = [;
    {
      key: "general",
      label: '综合' },{
      key: "symptom",
      label: '症状' },{
      key: "treatment",
      label: '治疗' },{
      key: "medicine",
      label: '中药' },{
      key: "constitution",
      label: '体质' },{
      key: "acupoint",
      label: '穴位' };
  ] as const;
  const handleSearch = useCallback() => {if (searchText.trim()) {const query: KnowledgeQuery = {query: searchText.trim(),type: selectedType;
      };
      onSearch(query);
    }
  }, [searchText, selectedType, onSearch]);
  const handleTypeSelect = (type: KnowledgeQuery['type']) => {setSelectedType(type);
    setShowTypeSelector(false);
    if (searchText.trim()) {
      const query: KnowledgeQuery = {,
  query: searchText.trim(),
        type: type;
      };
      onSearch(query);
    }
  };
  return (
  <View style={styles.container}>
      {// 搜索输入框}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          value={searchText}
          onChangeText={setSearchText}
          placeholder={placeholder}
          placeholderTextColor="#999999"
          returnKeyType="search"
          onSubmitEditing={handleSearch}
          editable={!loading}
        />
        <TouchableOpacity
          style={[styles.searchButton, loading && styles.searchButtonDisabled]}
          onPress={handleSearch}
          disabled={loading || !searchText.trim()}
        >
          {loading ? ()
            <ActivityIndicator size="small" color="#FFFFFF" />
          ) : (
            <Text style={styles.searchButtonText}>搜索</Text>
          )}
        </TouchableOpacity>
      </View>
      {// 搜索类型选择器}
      {showFilters  && <View style={styles.filtersContainer}>
          <TouchableOpacity
            style={styles.typeSelector}
            onPress={() => setShowTypeSelector(!showTypeSelector)}
          >
            <Text style={styles.typeSelectorText}>
              {searchTypes.find(t => t.key === selectedType)?.label}
            </Text>
            <Text style={styles.typeSelectorArrow}>
              {showTypeSelector ? '▲' : '▼'}
            </Text>
          </TouchableOpacity>
          {showTypeSelector  && <View style={styles.typeDropdown}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={styles.typeList}>
                  {searchTypes.map(type) => ()
                    <TouchableOpacity
                      key={type.key}
                      style={{[
                        styles.typeOption,
                        selectedType === type.key && styles.typeOptionSelected;
                      ]}}
                      onPress={() => handleTypeSelect(type.key)}
                    >
                      <Text
                        style={{[
                          styles.typeOptionText,
                          selectedType === type.key && styles.typeOptionTextSelected;
                        ]}}
                      >
                        {type.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </ScrollView>
            </View>
          )};
        </View>;
      )};
      {// 快速搜索建议};
      <ScrollView ;
        horizontal ;
        showsHorizontalScrollIndicator={false};
        style={styles.suggestionsContainer};
      >;
        <View style={styles.suggestions}>;
          {["头痛", "失眠', "消化不良", "疲劳', "焦虑", "感冒'].map((suggestion, index) => (;))
            <TouchableOpacity
              key={index};
              style={styles.suggestionChip};
              onPress={() => {setSearchText(suggestion);
                const query: KnowledgeQuery = {,
  query: suggestion,
                  type: selectedType;
                };
                onSearch(query);
              }}
            >
              <Text style={styles.suggestionText}>{suggestion}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  );
};
const styles = StyleSheet.create({
  container: {,
  backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'
  },
  searchContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12;
  },
  searchInput: {,
  flex: 1,
    height: 44,
    backgroundColor: '#F8F9FA',
    borderRadius: 22,
    paddingHorizontal: 16,
    fontSize: 16,
    color: '#333333',
    marginRight: 12;
  },
  searchButton: {,
  backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 22,
    minWidth: 60,
    alignItems: 'center',
    justifyContent: 'center'
  },
  searchButtonDisabled: {,
  backgroundColor: '#CCCCCC'
  },
  searchButtonText: {,
  color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600'
  },
  filtersContainer: {,
  marginBottom: 12;
  },
  typeSelector: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F8F9FA',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    marginBottom: 8;
  },
  typeSelectorText: {,
  fontSize: 14,
    color: '#333333',
    fontWeight: '500'
  },
  typeSelectorArrow: {,
  fontSize: 12,
    color: '#666666'
  },
  typeDropdown: {,
  backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    padding: 8;
  },
  typeList: {,
  flexDirection: 'row',
    gap: 8;
  },
  typeOption: {,
  paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: '#F5F5F5',
    marginRight: 8;
  },
  typeOptionSelected: {,
  backgroundColor: '#007AFF'
  },
  typeOptionText: {,
  fontSize: 14,
    color: '#666666',
    fontWeight: '500'
  },
  typeOptionTextSelected: {,
  color: '#FFFFFF'
  },
  suggestionsContainer: {,
  maxHeight: 40;
  },
  suggestions: {
      flexDirection: "row",
      gap: 8;
  },suggestionChip: {
      backgroundColor: "#E3F2FD",
      paddingHorizontal: 12,paddingVertical: 6,borderRadius: 16,marginRight: 8;
  },suggestionText: {fontSize: 12,color: '#1976D2',fontWeight: '500';
  };
});