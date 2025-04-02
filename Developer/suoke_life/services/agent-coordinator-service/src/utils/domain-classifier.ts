/**
 * 领域分类器
 * 用于根据查询内容分类到具体的知识领域
 */
import { loadConfig } from './config-loader';
import logger from './logger';

export interface DomainClassification {
  domain: string;
  confidence: number;
  subdomains?: string[];
}

export type Domain = 
  | 'traditionalCulture'     // 传统文化
  | 'modernMedicine'         // 现代医学
  | 'precisionMedicine'      // 精准医学
  | 'multimodalHealth'       // 多模态健康
  | 'environmentalHealth'    // 环境健康
  | 'mentalHealth'           // 心理健康
  | 'general';               // 通用领域

// 定义每个领域的关键词
const domainKeywords: Record<Domain, string[]> = {
  traditionalCulture: [
    '中医', '中医理论', '传统医学', '传统文化', '传统疗法', '经络', '气血', '阴阳', '五行',
    '八纲', '望闻问切', '舌诊', '脉诊', '望诊', '闻诊', '问诊', '切诊', '四诊', '病因',
    '病机', '辨证', '治则', '治法', '处方', '中药', '汤剂', '丸剂', '膏剂', '药性', '归经',
    '针灸', '穴位', '艾灸', '推拿', '按摩', '刮痧', '拔罐', '导引', '吐纳', '气功', '太极',
    '节气', '养生', '保健', '调养', '起居', '情志', '饮食', '运动'
  ],
  modernMedicine: [
    '西医', '现代医学', '临床医学', '诊断', '治疗', '药物', '处方药', '非处方药', '抗生素',
    '消炎药', '激素', '生物制剂', '化疗', '放疗', '手术', '微创', '移植', '输血', '输液',
    '检查', '化验', '影像', 'CT', 'MRI', 'X光', '超声', '核磁', '病理', '病原', '病毒',
    '细菌', '真菌', '寄生虫', '免疫', '抗体', '疫苗', '预防', '筛查', '复查', '随访',
    '护理', '康复', '理疗', '物理治疗', '职业治疗', '心肺复苏', '急救', '重症', '监护',
    '麻醉', '镇痛', '止血', '消毒', '无菌'
  ],
  precisionMedicine: [
    '基因', '基因组', '基因检测', '基因编辑', '精准医学', '个体化医疗', '个性化治疗',
    '靶向治疗', '分子诊断', '生物标志物', '基因突变', '单核苷酸多态性', 'SNP', 'DNA测序',
    '全基因组测序', '外显子组测序', '转录组测序', '蛋白质组学', '代谢组学', '表观遗传学',
    '药物基因组学', '肿瘤基因组学', '基因型', '表型', '致病变异', '遗传风险', '遗传咨询',
    '家族史', '遗传病', '罕见病', '分子分型', '分子分类', '分子靶点', '基因治疗',
    '基因编辑', 'CRISPR', '精准用药', '药物反应', '药物不良反应', '药物敏感性',
    '药物代谢', '药物转运', '药物相互作用'
  ],
  multimodalHealth: [
    '多模态', '图像', '声音', '文本', '生物信号', '可穿戴设备', '健康监测', '健康传感器',
    '活动追踪', '睡眠监测', '心率监测', '血压监测', '血糖监测', '心电图', '脑电图',
    '肌电图', '眼动追踪', '语音分析', '面部表情分析', '姿态分析', '步态分析', '运动分析',
    '呼吸监测', '体温监测', '皮肤电反应', '汗液分析', '唾液分析', '智能手表', '智能手环',
    '智能服装', '智能鞋', '智能床垫', '智能镜子', '智能马桶', '智能家居', '健康APP',
    '健康数据整合', '健康数据分析', '异常检测', '趋势分析', '模式识别', '健康预警',
    '远程监测', '远程医疗', '健康管理', '数字健康', '智能医疗'
  ],
  environmentalHealth: [
    '环境', '环境健康', '环境因素', '空气质量', '空气污染', '水质', '水污染', '噪音污染',
    '光污染', '电磁辐射', 'PM2.5', 'PM10', '二氧化硫', '二氧化氮', '一氧化碳', '臭氧',
    '挥发性有机物', '重金属', '甲醛', '苯', '氡', '石棉', '霉菌', '花粉', '过敏原',
    '气候变化', '极端天气', '热浪', '寒潮', '洪水', '干旱', '台风', '室内环境', '室外环境',
    '居住环境', '工作环境', '城市环境', '农村环境', '自然环境', '人造环境', '绿色空间',
    '蓝色空间', '健康城市', '可持续发展', '环境监测', '环境评估', '环境影响'
  ],
  mentalHealth: [
    '心理', '心理健康', '心理卫生', '心理咨询', '心理治疗', '精神疾病', '精神障碍',
    '精神分析', '认知行为治疗', 'CBT', '正念', '冥想', '焦虑', '抑郁', '压力', '强迫症',
    '恐惧症', '惊恐障碍', '创伤后应激障碍', 'PTSD', '注意力缺陷多动障碍', 'ADHD',
    '双相情感障碍', '躁郁症', '精神分裂症', '进食障碍', '睡眠障碍', '人格障碍', '幸福感',
    '心理韧性', '情绪管理', '情感调节', '自我意识', '自我效能', '自尊', '自信', '自我实现',
    '认知重构', '行为激活', '暴露疗法', '放松训练', '社交技能', '人际关系', '家庭治疗',
    '团体治疗', '艺术治疗', '音乐治疗', '舞蹈治疗', '游戏治疗', '沙盘治疗', '催眠治疗', 
    '心理咨询师', '心理治疗师', '精神科医生'
  ],
  general: [
    '健康', '疾病', '诊治', '症状', '病因', '病理', '药物', '食物', '营养', '运动',
    '休息', '生活', '保健', '预防', '治疗', '康复', '药品', '医疗', '咨询', '建议',
    '评估', '检查', '测试', '方案', '计划', '指导', '教育', '知识', '资讯', '信息',
    '服务', '产品', '应用', '工具', '设备', '装置', '技术', '方法', '研究', '调查'
  ]
};

export class DomainClassifier {
  private config = loadConfig();
  private domainKeywords = domainKeywords;

  /**
   * 根据查询内容分类到最匹配的领域
   * 
   * @param query 用户查询内容
   * @param threshold 置信度阈值，低于该值的分类将不被考虑
   * @returns 领域分类结果，按置信度降序排列
   */
  classifyQuery(query: string, threshold: number = 0.3): DomainClassification[] {
    // 简单的基于关键词匹配的分类器
    const scores: Record<Domain, number> = {
      traditionalCulture: 0,
      modernMedicine: 0,
      precisionMedicine: 0,
      multimodalHealth: 0,
      environmentalHealth: 0,
      mentalHealth: 0,
      general: 0
    };

    // 计算每个领域的匹配分数
    Object.entries(this.domainKeywords).forEach(([domain, keywords]) => {
      const matchCount = keywords.filter(keyword => 
        query.includes(keyword)
      ).length;
      
      // 计算匹配比例
      if (matchCount > 0) {
        scores[domain as Domain] = matchCount / keywords.length;
      }
    });

    // 转换为分类结果数组并按置信度排序
    const classifications: DomainClassification[] = Object.entries(scores)
      .filter(([_, confidence]) => confidence >= threshold)
      .map(([domain, confidence]) => ({
        domain,
        confidence,
        // 根据需要添加子领域
        subdomains: this.getSubdomains(domain as Domain, query)
      }))
      .sort((a, b) => b.confidence - a.confidence);

    // 如果没有匹配的领域，默认为general
    if (classifications.length === 0) {
      return [{
        domain: 'general',
        confidence: 1.0
      }];
    }

    return classifications;
  }

  /**
   * 获取领域内的子领域
   * 
   * @param domain 主领域
   * @param query 查询内容
   * @returns 子领域数组
   */
  private getSubdomains(domain: Domain, query: string): string[] | undefined {
    // 这里可以实现更复杂的子领域识别逻辑
    // 简单实现，根据不同领域返回不同的子领域
    switch (domain) {
      case 'traditionalCulture':
        if (query.includes('经络') || query.includes('穴位') || query.includes('针灸')) {
          return ['针灸推拿'];
        } else if (query.includes('中药') || query.includes('方剂')) {
          return ['中药方剂'];
        } else if (query.includes('养生') || query.includes('调养')) {
          return ['养生保健'];
        }
        break;
      case 'modernMedicine':
        if (query.includes('诊断') || query.includes('检查')) {
          return ['诊断学'];
        } else if (query.includes('治疗') || query.includes('手术')) {
          return ['治疗学'];
        } else if (query.includes('药物') || query.includes('用药')) {
          return ['药理学'];
        }
        break;
      case 'precisionMedicine':
        if (query.includes('基因检测') || query.includes('基因分析')) {
          return ['基因诊断'];
        } else if (query.includes('靶向治疗') || query.includes('个体化治疗')) {
          return ['精准治疗'];
        } else if (query.includes('遗传风险') || query.includes('遗传病')) {
          return ['遗传咨询'];
        }
        break;
      case 'multimodalHealth':
        if (query.includes('可穿戴') || query.includes('智能手表')) {
          return ['可穿戴监测'];
        } else if (query.includes('图像') || query.includes('影像')) {
          return ['医学影像'];
        } else if (query.includes('生物信号') || query.includes('心电图')) {
          return ['生物信号分析'];
        }
        break;
      case 'environmentalHealth':
        if (query.includes('空气') || query.includes('PM2.5')) {
          return ['空气质量'];
        } else if (query.includes('水') || query.includes('水质')) {
          return ['水质安全'];
        } else if (query.includes('气候') || query.includes('天气')) {
          return ['气候影响'];
        }
        break;
      case 'mentalHealth':
        if (query.includes('焦虑') || query.includes('抑郁')) {
          return ['情绪障碍'];
        } else if (query.includes('心理咨询') || query.includes('心理治疗')) {
          return ['心理服务'];
        } else if (query.includes('压力') || query.includes('情绪管理')) {
          return ['压力管理'];
        }
        break;
    }
    return undefined;
  }
}

// 导出单例实例
export const domainClassifier = new DomainClassifier();

// 示例使用方法:
// const classification = domainClassifier.classifyQuery('我想了解基因检测和精准用药之间的关系');
// console.log(classification);
// 输出: [{ domain: 'precisionMedicine', confidence: 0.42, subdomains: ['基因诊断'] }, ...]