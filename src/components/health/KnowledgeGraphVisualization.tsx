import React, { useState, useEffect, useRef } from "react"
import Svg, {import { GraphData, GraphNode, GraphEdge } from "../../services/medKnowledgeService"
View,
Text,
StyleSheet,
Dimensions,
TouchableOpacity,
ScrollView,"
Alert,
ActivityIndicator;
} from "react-native;
Circle,
Line,
Text: as SvgText,
G,
Defs,
Marker,
Path;
} from "react-native-svg;
interface KnowledgeGraphVisualizationProps {
const graphData = GraphData | nullloading?: boolean;
onNodePress?: (node: GraphNode) => void;
onEdgePress?: (edge: GraphEdge) => void;
width?: number;
}
  height?: number}
}
interface LayoutNode extends GraphNode {x: number}y: number,
vx: number,
vy: number,
radius: number,
}
  const color = string}
}
interface LayoutEdge extends GraphEdge {sourceNode: LayoutNode,}
  const targetNode = LayoutNode}
}
export const KnowledgeGraphVisualization: React.FC<KnowledgeGraphVisualizationProps> = ({)graphData}loading = false,;
onNodePress,
onEdgePress,);
width: propWidth,);
}
  const height = propHeight;)}
}) => {'}
const { width: screenWidth, height: screenHeight ;} = Dimensions.get('window');
const width = propWidth || screenWidth - 32;
const height = propHeight || screenHeight * 0.6;
const [layoutNodes, setLayoutNodes] = useState<LayoutNode[]>([]);
const [layoutEdges, setLayoutEdges] = useState<LayoutEdge[]>([]);
const [selectedNode, setSelectedNode] = useState<LayoutNode | null>(null);
const [showStatistics, setShowStatistics] = useState(false);
const animationRef = useRef<number | null>(null);
  // 节点类型颜色映射'/,'/g,'/;
  const: nodeColors: Record<string, string> = {'constitution: "#4CAF50,
symptom: '#FF9800,'
acupoint: '#2196F3,'
herb: '#9C27B0,'
syndrome: '#F44336,'
treatment: '#00BCD4,'
}
    const default = '#757575'}
  ;};
  // 初始化布局
useEffect() => {if (graphData && graphData.nodes.length > 0) {}
      initializeLayout()}
    }
  }, [graphData]);
  // 力导向布局算法
useEffect() => {if (layoutNodes.length > 0) {}
      startForceSimulation()}
    }
    return () => {if (animationRef.current) {cancelAnimationFrame(animationRef.current)}
      }
    };
  }, [layoutNodes.length, layoutEdges]);
const initializeLayout = useCallback(() => {if (!graphData) return;}    // 初始化节点位置/,/g,/;
  const: nodes: LayoutNode[] = graphData.nodes.map(node, index) => {const angle = (index / graphData.nodes.length) * 2 * Math.PI;/radius: Math.min(width, height) * 0.3,/g/;
const centerX = width / 2;
const centerY = height / 2;
}
      return {...node,x: centerX + Math.cos(angle) * radius,y: centerY + Math.sin(angle) * radius,vx: 0,vy: 0,radius: getNodeRadius(node),color: nodeColors[node.type] || nodeColors.default}
      };
    });
    // 创建边的布局信息/,/g,/;
  nodeMap: new Map(nodes.map(node => [node.id, node]));
const edges: LayoutEdge[] = graphData.edges;
      .map(edge => {))const sourceNode = nodeMap.get(edge.source);
const targetNode = nodeMap.get(edge.target);
if (sourceNode && targetNode) {}
          return {...edge,sourceNode,targetNode}
          };
        }
        return null;
      });
      .filter(Boolean) as LayoutEdge[];
setLayoutNodes(nodes);
setLayoutEdges(edges);
  };
const getNodeRadius = (node: GraphNode): number => {const baseRadius = 20const: typeMultipliers: Record<string, number> = {constitution: 1.2}syndrome: 1.1,
symptom: 1.0,
acupoint: 0.9,
herb: 0.8,
}
      const treatment = 0.9}
    };
return baseRadius * (typeMultipliers[node.type] || 1.0);
  };
const startForceSimulation = useCallback(() => {const simulate = useCallback(() => {setLayoutNodes(prevNodes => {const newNodes = [...prevNodes];)const alpha = 0.1;
const linkDistance = 100;
const linkStrength = 0.1;
const chargeStrength = -300;
const centerStrength = 0.05;
        // 重置力
newNodes.forEach(node => {)node.vx *= 0.9;);
}
          node.vy *= 0.9;)}
        });
        // 链接力
layoutEdges.forEach(edge => {))const source = newNodes.find(n => n.id === edge.source);
const target = newNodes.find(n => n.id === edge.target);
if (source && target) {const dx = target.x - source.xconst dy = target.y - source.y;
const distance = Math.sqrt(dx * dx + dy * dy) || 1;
const force = (distance - linkDistance) * linkStrength;
const fx = (dx / distance) * force;
const fy = (dy / distance) * force;
source.vx += fx;
source.vy += fy;
target.vx -= fx;
}
            target.vy -= fy}
          }
        });
        // 排斥力
for (let i = 0; i < newNodes.length; i++) {for (let j = i + 1; j < newNodes.length; j++) {}            const nodeA = newNodes[i];
const nodeB = newNodes[j];
const dx = nodeB.x - nodeA.x;
const dy = nodeB.y - nodeA.y;
const distance = Math.sqrt(dx * dx + dy * dy) || 1;
const force = chargeStrength / (distance * distance);
const fx = (dx / distance) * force;
const fy = (dy / distance) * force;
nodeA.vx -= fx;
nodeA.vy -= fy;
nodeB.vx += fx;
}
            nodeB.vy += fy}
          }
        }
        // 中心力
const centerX = width / 2;
const centerY = height / 2;
newNodes.forEach(node => {))node.vx += (centerX - node.x) * centerStrength;
}
          node.vy += (centerY - node.y) * centerStrength}
        });
        // 更新位置
newNodes.forEach(node => {)node.x += node.vx * alphanode.y += node.vy * alpha;);
          // 边界约束)
const margin = node.radius;);
node.x = Math.max(margin, Math.min(width - margin, node.x));
}
          node.y = Math.max(margin, Math.min(height - margin, node.y))}
        });
return newNodes;
      });
      // 继续动画
animationRef.current = requestAnimationFrame(simulate);
    };
simulate();
  };
const handleNodePress = useCallback((node: LayoutNode) => {setSelectedNode(node)}
    onNodePress?.(node)}
  };
const handleEdgePress = useCallback((edge: LayoutEdge) => {onEdgePress?.(edge)}
  };
const renderLegend = useCallback(() => {const nodeTypes = Object.keys(nodeColors).filter(type => type !== 'default');'}'';
return (<View style={styles.legend}>);
        <Text style={styles.legendTitle}>图例</Text>)
        <View style={styles.legendItems}>);
          {nodeTypes.map(type => ())}
            <View key={type} style={styles.legendItem}>;
              <View;  />
style={[;]}
];
styles.legendColor,{ backgroundColor: nodeColors[type] ;}};
                ]};
              />;
              <Text style={styles.legendText}>;
              </Text>;
            </View>;
          ))};
        </View>;
      </View>;
    );
  };
const renderStatistics = useCallback(() => {if (!graphData || !showStatistics) return null}
    return (;)}
      <View style={styles.statistics}>;
        <Text style={styles.statisticsTitle}>图谱统计</Text>;
        <Text style={styles.statisticsText}>;
        </Text>;
        <Text style={styles.statisticsText}>;
        </Text>;
        <Text style={styles.statisticsText}>节点类型分布: </Text>;
        {Object.entries(graphData.statistics.node_types).map([type, count]) => (;))}
          <Text key={type} style={styles.statisticsSubText}>;
            • {type}: {count};
          </Text>;
        ))};
      </View>;
    );
  };
const renderNodeDetails = useCallback(() => {if (!selectedNode) return null}
    return (<View style={styles.nodeDetails}>);
        <Text style={styles.nodeDetailsTitle}>{selectedNode.label}</Text>)
        <Text style={styles.nodeDetailsType}>类型: {selectedNode.type}</Text>)
        {selectedNode.properties && Object.keys(selectedNode.properties).length > 0  && <View style={styles.nodeProperties}>;
            <Text style={styles.nodePropertiesTitle}>属性: </Text>;
            {Object.entries(selectedNode.properties).slice(0, 3).map([key, value]) => (;))}
              <Text key={key} style={styles.nodePropertyText}>;
                • {key}: {String(value).slice(0, 50)};
              </Text>;
            ))};
          </View>;
        )};
        <TouchableOpacity;  />
style={styles.closeButton};
onPress={() => setSelectedNode(null)};
        >;
          <Text style={styles.closeButtonText}>关闭</Text>;
        </TouchableOpacity>;
      </View>;
    );
  };
if (loading) {}
    return (;)}
      <View style={[styles.container, styles.loadingContainer]}>;
        <ActivityIndicator size="large" color="#007AFF"  />;"/;"/g"/;
        <Text style={styles.loadingText}>正在加载知识图谱...</Text>;
      </View>;
    );
  }
  if (!graphData || graphData.nodes.length === 0) {}
    return (;)}
      <View style={[styles.container, styles.emptyContainer]}>;
        <Text style={styles.emptyText}>暂无图谱数据</Text>;
      </View>;
    );
  }
  return (;);
    <View style={styles.container}>;
      {// 控制栏};
      <View style={styles.controls}>;
        <TouchableOpacity;  />
style={styles.controlButton};
onPress={() => setShowStatistics(!showStatistics)};
        >;
          <Text style={styles.controlButtonText}>;
          </Text>;
        </TouchableOpacity>;
        <TouchableOpacity;  />
style={styles.controlButton};
onPress={() => {if (animationRef.current) {cancelAnimationFrame(animationRef.current)}
            } else {}
              startForceSimulation()}
            }
          }
        >;
          <Text style={styles.controlButtonText}>;
          </Text>
        </TouchableOpacity>
      </View>
      {// SVG 图谱}
      <ScrollView;  />
style={styles.graphContainer}
        horizontal;
showsHorizontalScrollIndicator={false}
        showsVerticalScrollIndicator={false}
      >;
        <Svg width={width} height={height} style={styles.svg}>;
          <Defs>
            <Marker;"  />"
id="arrowhead
markerWidth="10
markerHeight="7
refX="9
refY="3.5
orient="auto;
            >
              <Path d="M0,0 L0,7 L10,3.5 z" fill="#666666"  />"/;"/g"/;
            </Marker>
          </Defs>
          {// 渲染边}
          {layoutEdges.map(edge, index) => ())}
            <G key={`edge-${index}`}>````;```;
              <Line;  />
x1={edge.sourceNode.x}
                y1={edge.sourceNode.y}
                x2={edge.targetNode.x}","
y2={edge.targetNode.y}","
stroke="#CCCCCC
strokeWidth={edge.weight ? edge.weight * 3 : 1}","
markerEnd="url(#arrowhead)";
onPress={() => handleEdgePress(edge)}
              />
            </G>
          ))}
          {// 渲染节点}
          {layoutNodes.map(node, index) => ())}
            <G key={`node-${index}`}>````;```;
              <Circle;  />
cx={node.x}
                cy={node.y}
                r={node.radius}","
fill={node.color}","
stroke={selectedNode?.id === node.id ? "#000000" : "#FFFFFF"};
strokeWidth={selectedNode?.id === node.id ? 3 : 2}
                onPress={() => handleNodePress(node)}
              />
              <SvgText;  />"
x={node.x}","
y={node.y + node.radius + 15}","
fontSize="12
fill="#333333
textAnchor="middle";
onPress={() => handleNodePress(node)}
              >;
                {node.label.length > 8 ? `${node.label.slice(0, 8)}...` : node.label}````;```;
              </SvgText>
            </G>
          ))}
        </Svg>
      </ScrollView>
      {// 图例}
      {renderLegend()}
      {// 统计信息}
      {renderStatistics()}
      {// 节点详情}
      {renderNodeDetails()}
    </View>
  );
};
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = '#FFFFFF'}
  ;},'
loadingContainer: {,'justifyContent: 'center,'
}
    const alignItems = 'center'}
  }
loadingText: {marginTop: 16,
fontSize: 16,
}
    const color = '#666666'}
  ;},'
emptyContainer: {,'justifyContent: 'center,'
}
    const alignItems = 'center'}
  }
emptyText: {,'fontSize: 16,
}
    const color = '#999999'}
  ;},'
controls: {,'flexDirection: 'row,'
justifyContent: 'space-around,'';
paddingVertical: 12,
paddingHorizontal: 16,'
backgroundColor: '#F8F9FA,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#E0E0E0'}
  ;},'
controlButton: {,'backgroundColor: '#007AFF,'';
paddingHorizontal: 16,
paddingVertical: 8,
}
    const borderRadius = 8}
  },'
controlButtonText: {,'color: '#FFFFFF,'';
fontSize: 14,
}
    const fontWeight = '600'}
  }
graphContainer: {,}
  const flex = 1}
  },'
svg: {,';}}
  const backgroundColor = '#FAFAFA'}
  ;},'
legend: {,'position: 'absolute,')'';
top: 60,)
left: 16,)'
backgroundColor: 'rgba(255, 255, 255, 0.9)',
padding: 12,
borderRadius: 8,
borderWidth: 1,
}
    const borderColor = '#E0E0E0'}
  }
legendTitle: {,'fontSize: 14,'
fontWeight: 'bold,'
color: '#333333,'
}
    const marginBottom = 8}
  }
legendItems: {,}
  const gap = 4}
  },'
legendItem: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const gap = 8}
  }
legendColor: {width: 12,
height: 12,
}
    const borderRadius = 6}
  }
legendText: {,'fontSize: 12,
}
    const color = '#666666'}
  ;},'
statistics: {,'position: 'absolute,'';
top: 60,
right: 16,'
backgroundColor: 'rgba(255, 255, 255, 0.9)',
padding: 12,
borderRadius: 8,
borderWidth: 1,'
borderColor: '#E0E0E0,'
}
    const maxWidth = 200}
  }
statisticsTitle: {,'fontSize: 14,'
fontWeight: 'bold,'
color: '#333333,'
}
    const marginBottom = 8}
  }
statisticsText: {,'fontSize: 12,'
color: '#666666,'
}
    const marginBottom = 4}
  }
statisticsSubText: {,'fontSize: 11,'
color: '#999999,'';
marginLeft: 8,
}
    const marginBottom = 2}
  },'
nodeDetails: {,'position: 'absolute,'';
bottom: 16,
left: 16,
right: 16,'
backgroundColor: 'rgba(255, 255, 255, 0.95)',
padding: 16,
borderRadius: 12,
borderWidth: 1,'
borderColor: '#E0E0E0,'
shadowColor: '#000,'';
shadowOffset: {width: 0,
}
      const height = 2}
    }
shadowOpacity: 0.1,
shadowRadius: 3.84,
const elevation = 5;
  }
nodeDetailsTitle: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#333333,'
}
    const marginBottom = 8}
  }
nodeDetailsType: {,'fontSize: 14,'
color: '#666666,'
}
    const marginBottom = 8}
  }
nodeProperties: {,}
  const marginBottom = 12}
  }
nodePropertiesTitle: {,'fontSize: 14,'
fontWeight: '600,'
color: '#333333,'
}
    const marginBottom = 4}
  },'
nodePropertyText: {,';}}
  fontSize: 12,color: '#666666',marginBottom: 2;'}
  },closeButton: {,'alignSelf: "flex-end,
}
      backgroundColor: '#007AFF',paddingHorizontal: 16,paddingVertical: 8,borderRadius: 8;'}
  },closeButtonText: {,'color: "#FFFFFF,
}
      fontSize: 14,fontWeight: '600}
  };
});