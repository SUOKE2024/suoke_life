import { EventEmitter } from "events";"";"";

/* 举 *//;/g/;
 */"/;,"/g"/;
export enum TCMKnowledgeType {';,}SYNDROME = 'syndrome',           // 证候'/;,'/g'/;
SYMPTOM = 'symptom',            // 症状'/;,'/g'/;
HERB = 'herb',                  // 中药'/;,'/g'/;
FORMULA = 'formula',            // 方剂'/;,'/g'/;
ACUPOINT = 'acupoint',          // 穴位'/;,'/g'/;
MERIDIAN = 'meridian',          // 经络'/;,'/g'/;
CONSTITUTION = 'constitution',   // 体质'/;,'/g'/;
DISEASE = 'disease',            // 疾病'/;,'/g'/;
TREATMENT = 'treatment',        // 治法'/;,'/g'/;
THEORY = 'theory',              // 理论'/;,'/g'/;
DIAGNOSTIC_METHOD = 'diagnostic_method', // 诊法'/;'/g'/;
}
}
  LIFESTYLE = 'lifestyle'         // 养生'}''/;'/g'/;
}

/* 口 *//;/g/;
 *//;,/g/;
export interface TCMKnowledgeEntity {id: string}name: string,;
type: TCMKnowledgeType,;
aliases: string[],;
description: string,;
properties: Record<string, any>;
relationships: TCMRelationship[],;
sources: string[],;
confidence: number,;
lastUpdated: number,;
metadata: {const category = string;';,'';
subcategory?: string;';,'';
difficulty: 'basic' | 'intermediate' | 'advanced';','';
clinicalRelevance: number,';'';
}
}
    const evidenceLevel = 'high' | 'medium' | 'low';'}'';'';
  };
}

/* 口 *//;/g/;
 *//;,/g/;
export interface TCMRelationship {id: string}fromEntity: string,;
toEntity: string,;
relationshipType: string,';,'';
strength: number,';,'';
const direction = 'bidirectional' | 'unidirectional';';,'';
context?: string;
evidence: string[],;
}
}
  const confidence = number;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface TCMDiagnosisReasoning {syndrome: string}confidence: number,;
supportingSymptoms: string[],;
contradictingSymptoms: string[],;
recommendedFormulas: string[],;
recommendedHerbs: string[],;
recommendedAcupoints: string[],;
treatmentPrinciples: string[],;
lifestyleRecommendations: string[],;
reasoning: {steps: string[],;
evidenceChain: string[],;
alternativeDiagnoses: Array<{syndrome: string,;
confidence: number,;
}
}
      const reasoning = string;}
    }>;
  };
}

/* 口 *//;/g/;
 *//;,/g/;
export interface TCMKnowledgeQuery {;,}const query = string;
type?: TCMKnowledgeType[];
filters?: {category?: string;,}difficulty?: string;
clinicalRelevance?: number;
}
}
    evidenceLevel?: string;}
  };
limit?: number;
includeRelated?: boolean;
language?: string;
}

/* 口 *//;/g/;
 *//;,/g/;
export interface TCMKnowledgeSearchResult {entities: TCMKnowledgeEntity[]}totalCount: number,;
searchTime: number,;
suggestions: string[],;
relatedQueries: string[],;
}
}
  facets: {,};
const types = Array<{ type: string; count: number ;}>;
const categories = Array<{ category: string; count: number ;}>;
const evidenceLevels = Array<{ level: string; count: number ;}>;
  };
}

/* 能 *//;/g/;
 *//;,/g/;
export class ExpandedTCMKnowledgeService extends EventEmitter {;,}private knowledgeGraph: Map<string, TCMKnowledgeEntity> = new Map();
private relationships: Map<string, TCMRelationship> = new Map();
private indexedTerms: Map<string, Set<string>> = new Map();
private synonyms: Map<string, string[]> = new Map();
private categories: Map<string, string[]> = new Map();
private isInitialized: boolean = false;
constructor() {super();}}
    this.initializeKnowledgeBase();}
  }

  /* 库 *//;/g/;
   *//;,/g/;
private async initializeKnowledgeBase(): Promise<void> {try {}      const await = this.loadCoreKnowledge();
const await = this.buildIndexes();
const await = this.loadSynonyms();
this.isInitialized = true;';'';
      ';,'';
this.emit('knowledgeBaseInitialized', {')'';,}entityCount: this.knowledgeGraph.size,);,'';
relationshipCount: this.relationships.size;),;
}
        const timestamp = Date.now()}
      ;});

    } catch (error) {}}
      const throw = error;}
    }
  }

  /* 识 *//;/g/;
   *//;,/g/;
private async loadCoreKnowledge(): Promise<void> {// 加载基础证候/;,}const syndromes = this.getCoreSyndromes();,/g/;
syndromes.forEach(syndrome => this.addEntity(syndrome));

    // 加载常见症状/;,/g/;
const symptoms = this.getCoreSymptoms();
symptoms.forEach(symptom => this.addEntity(symptom));

    // 加载常用中药/;,/g/;
const herbs = this.getCoreHerbs();
herbs.forEach(herb => this.addEntity(herb));

    // 加载经典方剂/;,/g/;
const formulas = this.getCoreFormulas();
formulas.forEach(formula => this.addEntity(formula));

    // 加载重要穴位/;,/g/;
const acupoints = this.getCoreAcupoints();
acupoints.forEach(acupoint => this.addEntity(acupoint));

    // 加载经络系统/;,/g/;
const meridians = this.getCoreMeridians();
meridians.forEach(meridian => this.addEntity(meridian));

    // 加载体质类型/;,/g/;
const constitutions = this.getCoreConstitutions();
constitutions.forEach(constitution => this.addEntity(constitution));

    // 建立关系/;/g/;
}
    const await = this.buildCoreRelationships();}
  }

  /* 候 *//;/g/;
   *//;,/g/;
private getCoreSyndromes(): TCMKnowledgeEntity[] {return [;]';}      {';,}id: 'syndrome_qi_deficiency';','';
type: TCMKnowledgeType.SYNDROME,;
const properties = {}}
}
        ;}
];
relationships: [],;
confidence: 0.95,;
lastUpdated: Date.now(),;
metadata: {,;}';'';
';,'';
difficulty: 'basic';','';
clinicalRelevance: 0.9,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      },';'';
      {';,}id: 'syndrome_blood_stasis';','';
type: TCMKnowledgeType.SYNDROME,;
const properties = {}}
}
        ;}
relationships: [],;
confidence: 0.93,;
lastUpdated: Date.now(),;
metadata: {,;}';'';
';,'';
difficulty: 'intermediate';','';
clinicalRelevance: 0.85,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      },';'';
      {';,}id: 'syndrome_yin_deficiency';','';
type: TCMKnowledgeType.SYNDROME,;
const properties = {}}
}
        ;}
relationships: [],;
confidence: 0.94,;
lastUpdated: Date.now(),;
metadata: {,;}';'';
';,'';
difficulty: 'intermediate';','';
clinicalRelevance: 0.88,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      }
    ];
  }

  /* 状 *//;/g/;
   *//;,/g/;
private getCoreSymptoms(): TCMKnowledgeEntity[] {return [;]';}      {';,}id: 'symptom_fatigue';','';
type: TCMKnowledgeType.SYMPTOM,;
const properties = {}}
}
        ;}
];
relationships: [],;
confidence: 0.96,;
lastUpdated: Date.now(),;
metadata: {,';}';,'';
difficulty: 'basic';','';
clinicalRelevance: 0.9,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      },';'';
      {';,}id: 'symptom_palpitation';','';
type: TCMKnowledgeType.SYMPTOM,;
const properties = {}}
}
        ;}
relationships: [],;
confidence: 0.94,;
lastUpdated: Date.now(),;
metadata: {,';}';,'';
difficulty: 'intermediate';','';
clinicalRelevance: 0.85,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      }
    ];
  }

  /* 药 *//;/g/;
   *//;,/g/;
private getCoreHerbs(): TCMKnowledgeEntity[] {return [;]';}      {';,}id: 'herb_ginseng';','';
type: TCMKnowledgeType.HERB,;
properties: {,;}';'';
';,'';
const dosage = '3-9g';';'';

}
}
        }
];
relationships: [],;
confidence: 0.98,;
lastUpdated: Date.now(),;
metadata: {,;}';'';
';,'';
difficulty: 'basic';','';
clinicalRelevance: 0.95,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      },';'';
      {';,}id: 'herb_angelica';','';
type: TCMKnowledgeType.HERB,;
properties: {,;}';'';
';,'';
const dosage = '6-12g';';'';

}
}
        }
relationships: [],;
confidence: 0.97,;
lastUpdated: Date.now(),;
metadata: {,;}';'';
';,'';
difficulty: 'basic';','';
clinicalRelevance: 0.92,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      }
    ];
  }

  /* 剂 *//;/g/;
   *//;,/g/;
private getCoreFormulas(): TCMKnowledgeEntity[] {return [;]';}      {';,}id: 'formula_sijunzi';','';
type: TCMKnowledgeType.FORMULA,;
properties: {const composition = {}}
}
          ;}

        }
];
relationships: [],;
confidence: 0.98,;
lastUpdated: Date.now(),;
metadata: {,;}';'';
';,'';
difficulty: 'basic';','';
clinicalRelevance: 0.95,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      }
    ];
  }

  /* 位 *//;/g/;
   *//;,/g/;
private getCoreAcupoints(): TCMKnowledgeEntity[] {return [;]';}      {';,}id: 'acupoint_zusanli';','';
type: TCMKnowledgeType.ACUPOINT,;
const properties = {}}
}
        ;}
];
relationships: [],;
confidence: 0.98,;
lastUpdated: Date.now(),;
metadata: {,;}';'';
';,'';
difficulty: 'basic';','';
clinicalRelevance: 0.95,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      }
    ];
  }

  /* 络 *//;/g/;
   *//;,/g/;
private getCoreMeridians(): TCMKnowledgeEntity[] {return [;]';}      {';,}id: 'meridian_lung';','';
type: TCMKnowledgeType.MERIDIAN,;
properties: {const acupointCount = 11;

}
}
        }
];
relationships: [],;
confidence: 0.97,;
lastUpdated: Date.now(),;
metadata: {,;}';'';
';,'';
difficulty: 'intermediate';','';
clinicalRelevance: 0.9,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      }
    ];
  }

  /* 型 *//;/g/;
   *//;,/g/;
private getCoreConstitutions(): TCMKnowledgeEntity[] {return [;]';}      {';,}id: 'constitution_peaceful';','';
type: TCMKnowledgeType.CONSTITUTION,;
properties: {,;}';'';
';'';
}
          const percentage = '32.8%'}'';'';
        ;}
];
relationships: [],;
confidence: 0.96,;
lastUpdated: Date.now(),;
metadata: {,';}';,'';
difficulty: 'basic';','';
clinicalRelevance: 0.85,';'';
}
          const evidenceLevel = 'high'}'';'';
        ;}
      }
    ];
  }

  /* 系 *//;/g/;
   *//;,/g/;
private async buildCoreRelationships(): Promise<void> {// 证候与症状的关系'/;,}this.addRelationship({';,)id: 'rel_qi_deficiency_fatigue';','';,}fromEntity: 'syndrome_qi_deficiency';','';,'/g,'/;
  toEntity: 'symptom_fatigue';','';
relationshipType: 'manifests_as';','';
strength: 0.9,';,'';
direction: 'unidirectional';',)'';'';
);
}
      const confidence = 0.95)}
    ;});

    // 中药与证候的关系'/;,'/g'/;
this.addRelationship({)';,}id: 'rel_ginseng_qi_deficiency';','';
fromEntity: 'herb_ginseng';','';
toEntity: 'syndrome_qi_deficiency';','';
relationshipType: 'treats';','';
strength: 0.95,';,'';
direction: 'unidirectional';',)'';'';
);
}
      const confidence = 0.98)}
    ;});

    // 方剂与证候的关系'/;,'/g'/;
this.addRelationship({)';,}id: 'rel_sijunzi_qi_deficiency';','';
fromEntity: 'formula_sijunzi';','';
toEntity: 'syndrome_qi_deficiency';','';
relationshipType: 'treats';','';
strength: 0.92,';,'';
direction: 'unidirectional';',)'';'';
);
}
      const confidence = 0.96)}
    ;});

    // 穴位与证候的关系'/;,'/g'/;
this.addRelationship({)';,}id: 'rel_zusanli_qi_deficiency';','';
fromEntity: 'acupoint_zusanli';','';
toEntity: 'syndrome_qi_deficiency';','';
relationshipType: 'treats';','';
strength: 0.85,';,'';
direction: 'unidirectional';',)'';'';
);
}
      const confidence = 0.9)}
    ;});
  }

  /* 体 *//;/g/;
   *//;,/g/;
const public = addEntity(entity: TCMKnowledgeEntity): void {this.knowledgeGraph.set(entity.id, entity);,}this.indexEntity(entity);';'';
    ';,'';
this.emit('entityAdded', {';,)entityId: entity.id,);,}name: entity.name,);,'';
type: entity.type,);
}
      const timestamp = Date.now()}
    ;});
  }

  /* 系 *//;/g/;
   *//;,/g/;
const public = addRelationship(relationship: TCMRelationship): void {this.relationships.set(relationship.id, relationship);}    // 更新实体的关系列表/;,/g/;
const fromEntity = this.knowledgeGraph.get(relationship.fromEntity);
if (fromEntity) {}}
      fromEntity.relationships.push(relationship);}
    }';'';
';,'';
this.emit('relationshipAdded', {)';,}relationshipId: relationship.id,;,'';
fromEntity: relationship.fromEntity,);
toEntity: relationship.toEntity,);
type: relationship.relationshipType;),;
}
      const timestamp = Date.now()}
    ;});
  }

  /* 识 *//;/g/;
   *//;,/g/;
const public = async searchKnowledge(query: TCMKnowledgeQuery): Promise<TCMKnowledgeSearchResult> {const startTime = Date.now();,}try {// 预处理查询/;,}const processedQuery = this.preprocessQuery(query.query);/g/;

      // 执行搜索/;,/g,/;
  entities: this.executeSearch(processedQuery, query);

      // 生成建议和相关查询/;,/g/;
const suggestions = this.generateSuggestions(processedQuery);
const relatedQueries = this.generateRelatedQueries(processedQuery);

      // 生成分面统计/;,/g/;
const facets = this.generateFacets(entities);
const searchTime = Date.now() - startTime;
const: result: TCMKnowledgeSearchResult = {entities: entities.slice(0, query.limit || 20),;
const totalCount = entities.length;
searchTime,;
suggestions,;
relatedQueries,;
}
        facets}
      };';'';
';,'';
this.emit('knowledgeSearched', {)';,}query: query.query,);,'';
const resultCount = result.totalCount;);
searchTime,);
}
        const timestamp = Date.now()}
      ;});
return result;
';'';
    } catch (error) {';,}this.emit('knowledgeSearchError', {')'';,}query: query.query,);,'';
error: error instanceof Error ? error.message : String(error),;
}
        const timestamp = Date.now()}
      ;});
const throw = error;
    }
  }

  /* 理 *//;/g/;
   *//;,/g,/;
  public: async diagnosisReasoning(symptoms: string[], context?: any): Promise<TCMDiagnosisReasoning> {try {}      // 症状标准化/;,/g/;
const normalizedSymptoms = this.normalizeSymptoms(symptoms);

      // 查找相关证候/;,/g/;
const candidateSyndromes = this.findCandidateSyndromes(normalizedSymptoms);

      // 计算证候匹配度/;,/g,/;
  syndromeScores: this.calculateSyndromeScores(normalizedSymptoms, candidateSyndromes);

      // 选择最佳证候/;,/g/;
const bestSyndrome = syndromeScores[0];
if (!bestSyndrome) {}}
}
      }

      // 生成推理结果/;,/g,/;
  const: reasoning = await this.generateDiagnosisReasoning(bestSyndrome,);
normalizedSymptoms,);
syndromeScores);
      );';'';
';,'';
this.emit('diagnosisCompleted', {)';,}syndrome: reasoning.syndrome,);,'';
confidence: reasoning.confidence,);
symptomCount: symptoms.length,);
}
        const timestamp = Date.now()}
      ;});
return reasoning;
';'';
    } catch (error) {';,}this.emit('diagnosisError', {')'';,}symptoms,);,'';
error: error instanceof Error ? error.message : String(error),;
}
        const timestamp = Date.now()}
      ;});
const throw = error;
    }
  }

  /* 情 *//;/g/;
   *//;,/g,/;
  public: getEntityDetails(entityId: string, includeRelated: boolean = true): TCMKnowledgeEntity | null {const entity = this.knowledgeGraph.get(entityId);,}if (!entity) return null;
if (includeRelated) {// 添加相关实体信息/;,}const relatedEntities = this.getRelatedEntities(entityId);/g/;
}
      (entity as any).relatedEntities = relatedEntities;}
    }

    return entity;
  }

  /* 计 *//;/g/;
   *//;,/g/;
const public = getKnowledgeStatistics(): {totalEntities: number}totalRelationships: number,;
entityTypes: Record<string, number>;
categories: Record<string, number>;
}
    const lastUpdated = number;}
  } {}
    const entityTypes: Record<string, number> = {;};
const categories: Record<string, number> = {;};
for (const entity of this.knowledgeGraph.values()) {;,}entityTypes[entity.type] = (entityTypes[entity.type] || 0) + 1;
}
      categories[entity.metadata.category] = (categories[entity.metadata.category] || 0) + 1;}
    }

    return {totalEntities: this.knowledgeGraph.size}const totalRelationships = this.relationships.size;
entityTypes,;
categories,;
}
      const lastUpdated = Date.now()}
    ;};
  }

  // 私有方法/;,/g/;
private indexEntity(entity: TCMKnowledgeEntity): void {// 索引实体名称和别名/;,}terms: [entity.name, ...entity.aliases];,/g/;
terms.forEach(term => {);,}const normalizedTerm = term.toLowerCase();
if (!this.indexedTerms.has(normalizedTerm)) {}}
        this.indexedTerms.set(normalizedTerm, new Set());}
      }
      this.indexedTerms.get(normalizedTerm)!.add(entity.id);
    });
  }

  private async buildIndexes(): Promise<void> {// 构建分类索引/;,}for (const entity of this.knowledgeGraph.values()) {;,}const category = entity.metadata.category;,/g/;
if (!this.categories.has(category)) {}}
        this.categories.set(category, []);}
      }
      this.categories.get(category)!.push(entity.id);
    }
  }

  private async loadSynonyms(): Promise<void> {// 加载同义词映射/;,}const  synonymMappings = [;]];/g/;
    ];
synonymMappings.forEach(group => {);,}const primary = group[0];);
const synonyms = group.slice(1);
this.synonyms.set(primary, synonyms);
synonyms.forEach(synonym => {);}}
        this.synonyms.set(synonym, [primary]);}
      });
    });
  }

  private preprocessQuery(query: string): string {// 查询预处理：去除标点、转换同义词等/;,}let processed = query.toLowerCase().trim();/g/;

    // 同义词替换/;,/g/;
for (const [term, synonyms] of this.synonyms) {if (processed.includes(term)) {}};
return term; // 返回标准术语}/;/g/;
      }
      for (const synonym of synonyms) {if (processed.includes(synonym)) {}};
return term; // 返回标准术语}/;/g/;
        }
      }
    }

    return processed;
  }

  private executeSearch(query: string, searchQuery: TCMKnowledgeQuery): TCMKnowledgeEntity[] {}
    const results: Array<{ entity: TCMKnowledgeEntity; score: number ;}> = [];
for (const entity of this.knowledgeGraph.values()) {// 类型过滤/;,}if (searchQuery.type && !searchQuery.type.includes(entity.type)) {}};,/g/;
continue;}
      }

      // 其他过滤条件/;,/g/;
if (searchQuery.filters) {if (searchQuery.filters.category && entity.metadata.category !== searchQuery.filters.category) {}}
          continue;}
        }
        if (searchQuery.filters.difficulty && entity.metadata.difficulty !== searchQuery.filters.difficulty) {}}
          continue;}
        }
        if (searchQuery.filters.clinicalRelevance && entity.metadata.clinicalRelevance < searchQuery.filters.clinicalRelevance) {}}
          continue;}
        }
      }

      // 计算匹配分数/;,/g,/;
  score: this.calculateMatchScore(query, entity);
if (score > 0) {}
        results.push({ entity, score });
      }
    }

    // 按分数排序/;,/g/;
results.sort((a, b) => b.score - a.score);
return results.map(r => r.entity);
  }

  private calculateMatchScore(query: string, entity: TCMKnowledgeEntity): number {let score = 0;}    // 名称匹配/;,/g/;
if (entity.name.toLowerCase().includes(query)) {}}
      score += 10;}
    }

    // 别名匹配/;,/g/;
for (const alias of entity.aliases) {if (alias.toLowerCase().includes(query)) {}};
score += 8;}
      }
    }

    // 描述匹配/;,/g/;
if (entity.description.toLowerCase().includes(query)) {}}
      score += 5;}
    }

    // 属性匹配/;,/g/;
const propertiesStr = JSON.stringify(entity.properties).toLowerCase();
if (propertiesStr.includes(query)) {}}
      score += 3;}
    }

    return score;
  }

  private generateSuggestions(query: string): string[] {const suggestions: string[] = [];}    // 基于索引生成建议/;,/g/;
for (const [term, entityIds] of this.indexedTerms) {;,}if (term.includes(query) && term !== query) {}}
        suggestions.push(term);}
      }
    }

    return suggestions.slice(0, 5);
  }

  private generateRelatedQueries(query: string): string[] {// 生成相关查询建议/;,}const  related = [;]];/g/;
    ];

}
    return related;}
  }

  private generateFacets(entities: TCMKnowledgeEntity[]): any {}
    const types: Record<string, number> = {;};
const categories: Record<string, number> = {;};
const evidenceLevels: Record<string, number> = {;};
entities.forEach(entity => {));,}types[entity.type] = (types[entity.type] || 0) + 1;
categories[entity.metadata.category] = (categories[entity.metadata.category] || 0) + 1;
}
      evidenceLevels[entity.metadata.evidenceLevel] = (evidenceLevels[entity.metadata.evidenceLevel] || 0) + 1;}
    });
return {}
      types: Object.entries(types).map(([type, count]) => ({ type, count ;})),;
categories: Object.entries(categories).map(([category, count]) => ({ category, count ;})),;
evidenceLevels: Object.entries(evidenceLevels).map(([level, count]) => ({ level, count ;}));
    };
  }

  private normalizeSymptoms(symptoms: string[]): string[] {const return = symptoms.map(symptom => {);,}const normalized = symptom.toLowerCase().trim();
      // 同义词标准化/;,/g/;
for (const [standard, synonyms] of this.synonyms) {;,}if (synonyms.includes(normalized) || standard === normalized) {}}
          return standard;}
        }
      }
      return normalized;
    });
  }

  private findCandidateSyndromes(symptoms: string[]): TCMKnowledgeEntity[] {const candidates: TCMKnowledgeEntity[] = [];,}for (const entity of this.knowledgeGraph.values()) {;,}if (entity.type === TCMKnowledgeType.SYNDROME) {// 检查症状匹配/;,}const syndromeSymptoms = entity.properties.mainSymptoms || [];,/g/;
const  hasMatchingSymptom = symptoms.some(symptom => );
syndromeSymptoms.some((ss: string) => ss.includes(symptom) || symptom.includes(ss));
        );
if (hasMatchingSymptom) {}}
          candidates.push(entity);}
        }
      }
    }

    return candidates;
  }

  private calculateSyndromeScores(symptoms: string[], syndromes: TCMKnowledgeEntity[]): Array<{syndrome: TCMKnowledgeEntity,;
score: number,;
}
    const matchingSymptoms = string[];}
  }> {const  scores = useMemo(() => syndromes.map(syndrome => {)      const mainSymptoms = syndrome.properties.mainSymptoms || [];,}const secondarySymptoms = syndrome.properties.secondarySymptoms || [];
let score = 0;
const matchingSymptoms: string[] = [];
      );
      // 主症状匹配)/;,/g/;
symptoms.forEach(symptom => {);,}mainSymptoms.forEach((mainSymptom: string) => {if (mainSymptom.includes(symptom) || symptom.includes(mainSymptom)) {}            score += 10;
}
            matchingSymptoms.push(symptom), []);}
          }
        });

        // 次症状匹配/;,/g/;
secondarySymptoms.forEach((secondarySymptom: string) => {if (secondarySymptom.includes(symptom) || symptom.includes(secondarySymptom)) {}            score += 5;
}
            matchingSymptoms.push(symptom);}
          }
        });
      });
return { syndrome, score, matchingSymptoms };
    });
return scores.sort((a, b) => b.score - a.score);
  }

  private async generateDiagnosisReasoning(bestMatch: { syndrome: TCMKnowledgeEntity; score: number; matchingSymptoms: string[] ;},);
symptoms: string[],);
const allMatches = Array<{ syndrome: TCMKnowledgeEntity; score: number; matchingSymptoms: string[] ;}>);
  ): Promise<TCMDiagnosisReasoning> {const syndrome = bestMatch.syndrome;}    // 查找推荐的治疗方法/;,/g,/;
  recommendedFormulas: this.findRelatedEntities(syndrome.id, TCMKnowledgeType.FORMULA);
recommendedHerbs: this.findRelatedEntities(syndrome.id, TCMKnowledgeType.HERB);
recommendedAcupoints: this.findRelatedEntities(syndrome.id, TCMKnowledgeType.ACUPOINT);
return {syndrome: syndrome.name}confidence: Math.min(bestMatch.score / 100, 1),/;,/g,/;
  supportingSymptoms: bestMatch.matchingSymptoms,;
contradictingSymptoms: symptoms.filter(s => !bestMatch.matchingSymptoms.includes(s)),;
recommendedFormulas: recommendedFormulas.map(f => f.name),;
recommendedHerbs: recommendedHerbs.map(h => h.name),;
recommendedAcupoints: recommendedAcupoints.map(a => a.name),;
treatmentPrinciples: syndrome.properties.treatmentPrinciples || [],;
lifestyleRecommendations: syndrome.properties.lifestyleRecommendations || [],;
reasoning: {const steps = [;]}
}
          `匹配度: ${(bestMatch.score / 100 * 100).toFixed(1);}%````/`;`/g`/`;
];
        ],;
evidenceChain: syndrome.sources,;
alternativeDiagnoses: allMatches.slice(1, 4).map(match => ({));,}syndrome: match.syndrome.name,);
confidence: Math.min(match.score / 100, 1),/;/g/;
}
}
        ;}));
      }
    };
  }

  private findRelatedEntities(entityId: string, targetType: TCMKnowledgeType): TCMKnowledgeEntity[] {const related: TCMKnowledgeEntity[] = [];,}for (const relationship of this.relationships.values()) {;,}if (relationship.fromEntity === entityId || relationship.toEntity === entityId) {const  relatedEntityId = relationship.fromEntity === entityId ?;,}relationship.toEntity : relationship.fromEntity;
const relatedEntity = this.knowledgeGraph.get(relatedEntityId);
if (relatedEntity && relatedEntity.type === targetType) {}}
          related.push(relatedEntity);}
        }
      }
    }

    return related;
  }

  private getRelatedEntities(entityId: string): TCMKnowledgeEntity[] {const related: TCMKnowledgeEntity[] = [];,}for (const relationship of this.relationships.values()) {;,}if (relationship.fromEntity === entityId || relationship.toEntity === entityId) {const  relatedEntityId = relationship.fromEntity === entityId ?;,}relationship.toEntity : relationship.fromEntity;
const relatedEntity = this.knowledgeGraph.get(relatedEntityId);
if (relatedEntity) {}}
          related.push(relatedEntity);}
        }
      }
    }

    return related;
  }
}
';,'';
export default ExpandedTCMKnowledgeService; ''';