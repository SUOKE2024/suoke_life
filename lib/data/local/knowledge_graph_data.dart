import '../../domain/entities/knowledge_node.dart';
import '../../domain/entities/knowledge_relation.dart';

/// 知识图谱示例数据
class KnowledgeGraphSampleData {
  /// 获取示例节点数据
  static List<KnowledgeNode> getSampleNodes() {
    return [
      // 中医养生主题节点
      KnowledgeNode(
        id: 'n1',
        name: '中医养生',
        type: '主题',
        topic: '中医养生',
        weight: 5,
        description: '中医养生是中国传统医学的重要组成部分，注重整体观念和平衡理念',
      ),
      
      // 概念节点
      KnowledgeNode(
        id: 'n2',
        name: '阴阳平衡',
        type: '概念',
        topic: '中医养生',
        weight: 4,
        description: '阴阳平衡是中医理论的核心，强调人体内阴阳二气的协调平衡',
      ),
      KnowledgeNode(
        id: 'n3',
        name: '五行学说',
        type: '概念',
        topic: '中医养生',
        weight: 4,
        description: '五行学说将万物归纳为金、木、水、火、土五种基本物质，用以解释自然现象和生理病理变化',
      ),
      
      // 方法节点
      KnowledgeNode(
        id: 'n4',
        name: '经络调理',
        type: '方法',
        topic: '中医养生',
        weight: 3,
        description: '通过针灸、推拿等手段疏通经络，调节气血运行',
      ),
      KnowledgeNode(
        id: 'n5',
        name: '食疗养生',
        type: '方法',
        topic: '中医养生',
        weight: 3,
        description: '根据食物的性味和个人体质选择适合的食物，以达到保健养生的目的',
      ),
      
      // 疾病节点
      KnowledgeNode(
        id: 'n6',
        name: '肝郁气滞',
        type: '疾病',
        topic: '中医养生',
        weight: 2,
        description: '肝的疏泄功能失调，气机郁滞不畅的病理状态',
      ),
      
      // 症状节点
      KnowledgeNode(
        id: 'n7',
        name: '胸胁胀痛',
        type: '症状',
        topic: '中医养生',
        weight: 2,
        description: '胸部和肋间区域出现的胀满疼痛感',
      ),
      
      // 健康饮食主题节点
      KnowledgeNode(
        id: 'n8',
        name: '健康饮食',
        type: '主题',
        topic: '健康饮食',
        weight: 5,
        description: '均衡、适量、多样化的饮食方式，满足身体所需的各种营养素',
      ),
      
      // 健康饮食下的概念和方法
      KnowledgeNode(
        id: 'n9',
        name: '膳食均衡',
        type: '概念',
        topic: '健康饮食',
        weight: 3,
        description: '各类食物的合理搭配，保证各种营养素的均衡摄入',
      ),
      KnowledgeNode(
        id: 'n10',
        name: '地中海饮食',
        type: '方法',
        topic: '健康饮食',
        weight: 3,
        description: '以蔬果、全谷物、豆类、坚果、橄榄油和适量鱼类为主的饮食模式',
      ),
    ];
  }
  
  /// 获取示例关系数据
  static List<KnowledgeRelation> getSampleRelations() {
    return [
      // 中医养生主题关系
      KnowledgeRelation(
        id: 'r1',
        sourceId: 'n1',
        targetId: 'n2',
        type: '包含',
        description: '中医养生理论包含阴阳平衡理念',
      ),
      KnowledgeRelation(
        id: 'r2',
        sourceId: 'n1',
        targetId: 'n3',
        type: '包含',
        description: '中医养生理论包含五行学说',
      ),
      KnowledgeRelation(
        id: 'r3',
        sourceId: 'n1',
        targetId: 'n4',
        type: '应用',
        description: '中医养生应用经络调理方法',
      ),
      KnowledgeRelation(
        id: 'r4',
        sourceId: 'n1',
        targetId: 'n5',
        type: '应用',
        description: '中医养生应用食疗养生方法',
      ),
      KnowledgeRelation(
        id: 'r5',
        sourceId: 'n6',
        targetId: 'n7',
        type: '表现为',
        description: '肝郁气滞表现为胸胁胀痛等症状',
      ),
      KnowledgeRelation(
        id: 'r6',
        sourceId: 'n4',
        targetId: 'n6',
        type: '治疗',
        description: '经络调理可用于治疗肝郁气滞',
      ),
      KnowledgeRelation(
        id: 'r7',
        sourceId: 'n5',
        targetId: 'n6',
        type: '预防',
        description: '食疗养生可预防肝郁气滞',
      ),
      
      // 健康饮食关系
      KnowledgeRelation(
        id: 'r8',
        sourceId: 'n8',
        targetId: 'n9',
        type: '基于',
        description: '健康饮食基于膳食均衡原则',
      ),
      KnowledgeRelation(
        id: 'r9',
        sourceId: 'n8',
        targetId: 'n10',
        type: '包含',
        description: '健康饮食包含地中海饮食模式',
      ),
      
      // 跨主题关系
      KnowledgeRelation(
        id: 'r10',
        sourceId: 'n5',
        targetId: 'n8',
        type: '关联',
        description: '食疗养生与健康饮食密切相关',
        isBidirectional: true,
      ),
    ];
  }
} 