import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";";
import {;,}FlatList,;
VirtualizedList: as RNVirtualizedList,;
Dimensions,;
View,;
Text,;
StyleSheet,";"";
}
  RefreshControl,'}'';
ActivityIndicator} from "react-native";";
import SkeletonLoader from "./SkeletonLoader";""/;,"/g"/;
const { height: screenHeight ;} = Dimensions.get('window');';'';
// 虚拟化列表配置/;,/g/;
interface VirtualizedListConfig {const itemHeight = number;,}estimatedItemSize?: number;
windowSize?: number;
initialNumToRender?: number;
maxToRenderPerBatch?: number;
updateCellsBatchingPeriod?: number;
removeClippedSubviews?: boolean;
getItemLayout?: boolean;
}
}
  keyExtractor?: (item: any; index: number) => string;}
}
// 列表项接口/;,/g/;
interface ListItem {const id = string;}}
}
  [key: string]: any;}
}
// 虚拟化列表属性/;,/g/;
interface VirtualizedListProps<T extends ListItem> {}}
  data: T[],}
  renderItem: ({ item, index ;}: { item: T; index: number ;}) => React.ReactElement;
config?: Partial<VirtualizedListConfig>;
loading?: boolean;
refreshing?: boolean;
onRefresh?: () => void;
onEndReached?: () => void;
onEndReachedThreshold?: number;
ListHeaderComponent?: React.ComponentType<any> | React.ReactElement;
ListFooterComponent?: React.ComponentType<any> | React.ReactElement;
ListEmptyComponent?: React.ComponentType<any> | React.ReactElement;
style?: any;
contentContainerStyle?: any;
showsVerticalScrollIndicator?: boolean;
bounces?: boolean;';,'';
enableVirtualization?: boolean;';,'';
skeletonType?: 'list' | 'card' | 'chat' | 'profile';';'';
}
// 默认配置/;,/g,/;
  const: DEFAULT_CONFIG: VirtualizedListConfig = {itemHeight: 60,;
estimatedItemSize: 60,;
windowSize: 10,;
initialNumToRender: 10,;
maxToRenderPerBatch: 5,;
updateCellsBatchingPeriod: 50,;
}
  removeClippedSubviews: true,}
  const getItemLayout = true;};
// 性能优化的虚拟化列表/;,/g/;
export const VirtualizedList = <T extends ListItem>({)data,;}}
  renderItem,};
config: userConfig = {;}
loading = false,;
refreshing = false,;
onRefresh,;
onEndReached,;
onEndReachedThreshold = 0.1,;
ListHeaderComponent,;
ListFooterComponent,;
ListEmptyComponent,;
style,;
contentContainerStyle,;
showsVerticalScrollIndicator = true,);
bounces = true,)';,'';
enableVirtualization = true,)';,'';
skeletonType = 'list'}: VirtualizedListProps<T>) => {'}'';
config: { ...DEFAULT_CONFIG, ...userConfig };
const [isLoadingMore, setIsLoadingMore] = useState(false);
const flatListRef = useRef<FlatList<T>>(null);
  // 优化的keyExtractor;/;,/g,/;
  const: keyExtractor = useCallback(item: T, index: number) => {}}
    return config.keyExtractor ? config.keyExtractor(item, index) : item.id || index.toString();}
  }, [config.keyExtractor]);
  // 优化的getItemLayout;/;,/g/;
const  getItemLayout = useMemo() => {if (!config.getItemLayout) return undefined;,}return (data: T[] | null | undefined, index: number) => ({)}length: config.itemHeight,;
}
      const offset = config.itemHeight * index;}
      index});
  }, [config.getItemLayout, config.itemHeight]);
  // 优化的renderItem;/;,/g,/;
  optimizedRenderItem: useCallback({ item, index }: { item: T; index: number ;}) => {}
    MemoizedItem: React.memo() => renderItem({ item, index }));
return <MemoizedItem  />;/;/g/;
  }, [renderItem]);
  // 处理加载更多/;,/g/;
const  handleEndReached = useCallback() => {if (!isLoadingMore && onEndReached) {}      setIsLoadingMore(true);
onEndReached();
      // 模拟加载完成/;/g/;
}
      setTimeout() => setIsLoadingMore(false), 1000);}
    }
  }, [isLoadingMore, onEndReached]);
  // 加载更多指示器/;,/g/;
const  renderFooter = useCallback() => {if (ListFooterComponent) {}      const return = React.isValidElement(ListFooterComponent);
        ? ListFooterComponent;
}
        : React.createElement(ListFooterComponent);}
    }
    if (isLoadingMore) {}';,'';
return (<View style={styles.loadingFooter}>';)          <ActivityIndicator size="small" color="#007AFF"  />")""/;"/g"/;
          <Text style={styles.loadingText}>加载更多...</Text>)/;/g/;
        </View>)/;/g/;
      );
    }
    return null;
  }, [ListFooterComponent, isLoadingMore]);
  // 空列表组件/;,/g/;
const  renderEmpty = useCallback() => {}}
    if (loading) {}
      return <SkeletonLoader type={skeletonType} count={8}  />;/;/g/;
    }
    if (ListEmptyComponent) {const return = React.isValidElement(ListEmptyComponent);}        ? ListEmptyComponent;
}
        : React.createElement(ListEmptyComponent);}
    }
    return (<View style={styles.emptyContainer}>);
        <Text style={styles.emptyText}>暂无数据</Text>)/;/g/;
      </View>)/;/g/;
    );
  }, [loading, ListEmptyComponent, skeletonType]);
  // 下拉刷新控制/;,/g/;
const  refreshControl = useMemo() => {if (!onRefresh) return undefined;}}
        return (<RefreshControl;}  />/;,)refreshing={refreshing}";,"/g"/;
onRefresh={onRefresh}";,"";
colors={['#007AFF']}';,'';
tintColor="#007AFF"";"";
")";
titleColor="#666")"";"";
      />)/;/g/;
    );
  }, [refreshing, onRefresh]);
  // 如果启用虚拟化且数据量大，使用FlatList;/;,/g/;
if (enableVirtualization && data.length > 50) {}}
    return (<FlatList;}  />/;,)ref={flatListRef}/g/;
        data={data}
        renderItem={optimizedRenderItem}
        keyExtractor={keyExtractor}
        getItemLayout={getItemLayout}
        initialNumToRender={config.initialNumToRender}
        maxToRenderPerBatch={config.maxToRenderPerBatch}
        updateCellsBatchingPeriod={config.updateCellsBatchingPeriod}
        windowSize={config.windowSize}
        removeClippedSubviews={config.removeClippedSubviews}
        onEndReached={handleEndReached}
        onEndReachedThreshold={onEndReachedThreshold}
        ListHeaderComponent={ListHeaderComponent}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={renderEmpty}
        refreshControl={refreshControl}
        style={[styles.container, style]}
        contentContainerStyle={}[;]}
          data.length === 0 && styles.emptyContentContainer,}
];
contentContainerStyle]}
        showsVerticalScrollIndicator={showsVerticalScrollIndicator}
        bounces={bounces}
        // 性能优化属性/;,/g/;
disableVirtualization={false}
        legacyImplementation={false}
        maintainVisibleContentPosition={}}
          minIndexForVisible: 0,)}
          const autoscrollToTopThreshold = 10;}});
      />)/;/g/;
    );
  }
  // 对于小数据集，使用普通的ScrollView渲染/;,/g/;
return (<View style={[styles.container, style]}>);
      {loading ? ()}
        <SkeletonLoader type={skeletonType} count={8}  />/;/g/;
      ) : (<FlatList;  />/;,)data={data}/g/;
          renderItem={optimizedRenderItem}
          keyExtractor={keyExtractor}
          ListHeaderComponent={ListHeaderComponent}
          ListFooterComponent={renderFooter}
          ListEmptyComponent={renderEmpty}
          refreshControl={refreshControl}
          contentContainerStyle={}[;]}
            data.length === 0 && styles.emptyContentContainer,}
];
contentContainerStyle]}
          showsVerticalScrollIndicator={showsVerticalScrollIndicator}
          bounces={bounces}
          onEndReached={handleEndReached});
onEndReachedThreshold={onEndReachedThreshold});
        />)/;/g/;
      )}
    </View>/;/g/;
  );
};
// 高性能聊天列表组件/;,/g/;
export const ChatVirtualizedList = <T extends ListItem & { message: string; timestamp: number ;}>({)data,);,}renderItem,)";"";
}
  ...props;)"}"";"";
}: Omit<VirtualizedListProps<T>, 'config' | 'skeletonType'>) => {';,}const: chatConfig: VirtualizedListConfig = {itemHeight: 80,;,'';
estimatedItemSize: 80,;
windowSize: 15,;
initialNumToRender: 15,;
maxToRenderPerBatch: 8,;
updateCellsBatchingPeriod: 30,;
removeClippedSubviews: true,;
}
    getItemLayout: true,}
    keyExtractor: (item, index) => `chat-${item.id;}-${item.timestamp}`};````;,```;
return (<VirtualizedList;  />/;,)data={data}/g/;
      renderItem={renderItem}';,'';
config={chatConfig}';,'';
skeletonType="chat")"";"";
      {...props});
    />)/;/g/;
  );
};
// 高性能卡片列表组件/;,/g/;
export const CardVirtualizedList = <T extends ListItem>({)data,);,}renderItem,)";"";
}
  ...props;)"}"";"";
}: Omit<VirtualizedListProps<T>, 'config' | 'skeletonType'>) => {';,}const: cardConfig: VirtualizedListConfig = {itemHeight: 200,;,'';
estimatedItemSize: 200,;
windowSize: 8,;
initialNumToRender: 6,;
maxToRenderPerBatch: 3,;
updateCellsBatchingPeriod: 100,;
}
    removeClippedSubviews: true,}
    const getItemLayout = true;};
return (<VirtualizedList;  />/;,)data={data}/g/;
      renderItem={renderItem}';,'';
config={cardConfig}';,'';
skeletonType="card")"";"";
      {...props});
    />)/;/g/;
  );
};
// 无限滚动Hook;/;,/g/;
export const useInfiniteScroll = <T extends ListItem>();
fetchData: (page: number) => Promise<T[]>,;
pageSize: number = 20;
) => {const [data, setData] = useState<T[]>([]);,}const [loading, setLoading] = useState(false);
const [refreshing, setRefreshing] = useState(false);
const [hasMore, setHasMore] = useState(true);
const [page, setPage] = useState(1);
const: loadData = useCallback(async (pageNum: number, isRefresh = false) => {if (loading) return;,}setLoading(true);
if (isRefresh) {}}
      setRefreshing(true);}
    }
    try {const newData = await fetchData(pageNum);,}if (isRefresh) {setData(newData);}}
        setPage(2);}
      } else {setData(prev => [...prev, ...newData]);}}
        setPage(pageNum + 1);}
      }
      setHasMore(newData.length === pageSize);";"";
    } catch (error) {";}}"";
      console.error('Failed to load data:', error);'}'';'';
    } finally {setLoading(false);}}
      setRefreshing(false);}
    }
  }, [fetchData, pageSize, loading]);
  // 初始加载/;,/g/;
useEffect() => {}}
    loadData(1, true);}
  }, [loadData]);
const  refresh = useCallback() => {}}
    loadData(1, true);}
  }, [loadData]);
const  loadMore = useCallback() => {if (hasMore && !loading) {}}
      loadData(page);}
    }
  }, [hasMore, loading, page, loadData]);
return {data}loading,;
refreshing,;
hasMore,;
}
    refresh,}
    loadMore};
};
const  styles = StyleSheet.create({)}
  container: {,}
  flex: 1;}
emptyContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';'';
}
    alignItems: 'center';','}'';
paddingVertical: 50;}
emptyContentContainer: {,}
  flexGrow: 1;}
emptyText: {,';,}fontSize: 16,';'';
}
    color: '#999';','}';,'';
textAlign: 'center';},';,'';
loadingFooter: {,';,}flexDirection: 'row';','';
justifyContent: 'center';','';'';
}
    alignItems: 'center';','}'';
paddingVertical: 20;}
loadingText: {,);,}marginLeft: 10,)';'';
}
    fontSize: 14;),'}'';
const color = '#666';}});';,'';
export default VirtualizedList;