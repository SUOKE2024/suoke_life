/* 0 *//;/g/;
 *//;/g/;

// 体质类型枚举/;,/g/;
export enum ConstitutionType {BALANCED = 'balanced',';,}QI_DEFICIENCY = 'qi_deficiency',';,'';
YANG_DEFICIENCY = 'yang_deficiency',';,'';
YIN_DEFICIENCY = 'yin_deficiency',';,'';
PHLEGM_DAMPNESS = 'phlegm_dampness',';,'';
DAMP_HEAT = 'damp_heat',';,'';
BLOOD_STASIS = 'blood_stasis',';,'';
QI_STAGNATION = 'qi_stagnation',';'';
}
}
  SPECIAL_DIATHESIS = 'special_diathesis'}'';'';
}

/* 类 *//;/g/;
 *//;,/g/;
export class TCMOntologyModel {;,}private syndromePatterns: Map<string, SyndromePattern> = new Map();
private constitutionProfiles: Map<ConstitutionType, ConstitutionProfile> = new Map();
private herbDatabase: Map<string, HerbProfile> = new Map();
private formulaDatabase: Map<string, FormulaProfile> = new Map();
private meridianSystem: Map<string, MeridianProfile> = new Map();
private organSystem: Map<string, OrganProfile> = new Map();
constructor() {}}
}
    this.initializeOntology();}
  }

  /* 型 *//;/g/;
   *//;,/g/;
private initializeOntology(): void {this.initializeConstitutionProfiles();,}this.initializeSyndromePatterns();
this.initializeHerbDatabase();
this.initializeFormulaDatabase();
this.initializeMeridianSystem();
}
    this.initializeOrganSystem();}
  }

  /* 案 *//;/g/;
   *//;,/g/;
private initializeConstitutionProfiles(): void {// 平和质/;,}this.constitutionProfiles.set(ConstitutionType.BALANCED, {)      const characteristics = [;]];}      ],;,/g/;
const physicalTraits = {}}
}
      ;}
const psychologicalTraits = {}}
}
      ;}
const adaptationCapacity = {}}
}
      ;}
const healthMaintenance = {);}}
)}
      ;});
    });

    // 气虚质/;,/g/;
this.constitutionProfiles.set(ConstitutionType.QI_DEFICIENCY, {)const characteristics = [;]];}      ],;
const physicalTraits = {}}
}
      ;}
const psychologicalTraits = {}}
}
      ;}
const adaptationCapacity = {}}
}
      ;}
const healthMaintenance = {);}}
)}
      ;});
    });

    // 阳虚质/;,/g/;
this.constitutionProfiles.set(ConstitutionType.YANG_DEFICIENCY, {)const characteristics = [;]];}      ],;
const physicalTraits = {}}
}
      ;}
const psychologicalTraits = {}}
}
      ;}
const adaptationCapacity = {}}
}
      ;}
const healthMaintenance = {);}}
)}
      ;});
    });

    // 阴虚质/;,/g/;
this.constitutionProfiles.set(ConstitutionType.YIN_DEFICIENCY, {)const characteristics = [;]];}      ],;
const physicalTraits = {}}
}
      ;}
const psychologicalTraits = {}}
}
      ;}
const adaptationCapacity = {}}
}
      ;}
const healthMaintenance = {);}}
)}
      ;});
    });
  }

  /* 式 *//;/g/;
   *//;,/g/;
private initializeSyndromePatterns(): void {';}    // 气虚证'/;,'/g'/;
this.syndromePatterns.set('qi_deficiency_syndrome', {';,)const mainSymptoms = [;]];}      ],;,'';
const tongueManifestations = {}}
}
      ;}

);
);
);
    });
';'';
    // 血虚证'/;,'/g'/;
this.syndromePatterns.set('blood_deficiency_syndrome', {)';,}const mainSymptoms = [;]];'';
      ],;
const tongueManifestations = {}}
}
      ;}

);
);
);
    });
  }

  /* 库 *//;/g/;
   *//;,/g/;
private initializeHerbDatabase(): void {// 人参/;}';'/g'/;
';,'';
latinName: 'Panax ginseng';','';'';
';'';
';,'';
dosage: '3-9g';','';
const modernPharmacology = {}}
}
      ;}
    });

    // 当归/;/g/;
';'';
';,'';
latinName: 'Angelica sinensis';','';'';
';'';
';,'';
dosage: '6-12g';','';
incompatibilities: [],;
const modernPharmacology = {}}
}
      ;}
    });
  }

  /* 库 *//;/g/;
   *//;,/g/;
private initializeFormulaDatabase(): void {// 四君子汤/;,}const composition = [;]];/g/;
      ],;
const modifications = [;]{}}
];
const removal = []}
        ;}
        {}}
          const removal = []}
        ;}
      ],;

    });

    // 四物汤/;,/g/;
const composition = [;]];
      ],;
const modifications = [;]{}}
];
const removal = []}
        ;}
        {}}
          const removal = []}
        ;}
      ],;

    });
  }

  /* 统 *//;/g/;
   *//;,/g/;
private initializeMeridianSystem(): void {// 手太阴肺经/;}';'/g'/;
';,'';
abbreviation: 'LU';','';
const keyPoints = [;]}
];
      ]}
    ;});
  }

  /* 统 *//;/g/;
   *//;,/g/;
private initializeOrganSystem(): void {// 心/;}}/g/;
}
    });

    // 肝/;/g/;

    });
  }

  /* 式 *//;/g/;
   *//;,/g/;
const public = analyzeSymptoms(symptoms: SymptomInput[]): PatternAnalysisResult {const patternMatches: PatternMatch[] = [];}    // 遍历所有证候模式进行匹配/;,/g/;
for (const [patternId, pattern] of this.syndromePatterns) {;,}matchResult: this.matchPattern(symptoms, pattern);
if (matchResult.score > 0.3) {// 设置最低匹配阈值/;,}patternMatches.push({)          patternId}pattern,;,/g,/;
  score: matchResult.score,);
matchedSymptoms: matchResult.matchedSymptoms,);
}
          const confidence = matchResult.confidence)}
        ;});
      }
    }

    // 按分数排序/;,/g/;
patternMatches.sort((a, b) => b.score - a.score);
const recommendations: TreatmentRecommendation[] = [];
if (patternMatches.length > 0) {const primaryPattern = patternMatches[0];}      // 添加治疗原则建议'/;,'/g'/;
recommendations.push({';,)type: 'principle';','';})';,'';
content: primaryPattern.pattern.treatmentPrinciple,)';'';
}
        const priority = 'high')'}'';'';
      ;});

      // 添加方剂建议/;,/g/;
primaryPattern.pattern.recommendedFormulas.forEach(formula => {)';,}recommendations.push({';,)type: 'formula';','';})';,'';
content: formula,)';'';
}
          const priority = 'high')'}'';'';
        ;});
      });

      // 添加禁忌症/;,/g/;
if (primaryPattern.pattern.contraindications.length > 0) {';,}recommendations.push({';,)type: 'contraindication';','';})';'';
)';'';
}
          const priority = 'medium')'}'';'';
        ;});
      }
    }

    return {primaryPattern: patternMatches.length > 0 ? patternMatches[0] : null}alternativePatterns: patternMatches.slice(1, 4), // 取前3个备选/;,/g/;
const confidence = patternMatches.length > 0 ? patternMatches[0].confidence : 0;
recommendations,;
}
      const timestamp = new Date()}
    ;};
  }

  /* 式 *//;/g/;
   *//;,/g/;
private matchPattern(symptoms: SymptomInput[], pattern: SyndromePattern): PatternMatchResult {const matchedSymptoms: MatchedSymptom[] = [];,}let totalScore = 0;
let maxPossibleScore = 0;

    // 计算症状匹配度/;,/g/;
pattern.mainSymptoms.forEach(patternSymptom => {);,}maxPossibleScore += patternSymptom.weight;);
      );
const userSymptom = symptoms.find(s => s.name === patternSymptom.name);
if (userSymptom) {const score = patternSymptom.weight * (userSymptom.severity / 10);/;,}totalScore += score;,/g/;
matchedSymptoms.push({)          symptomName: patternSymptom.name}userSeverity: userSymptom.severity,);
const patternWeight = patternSymptom.weight;);
}
          score)}
        });
      } else if (patternSymptom.required) {// 必需症状缺失，降低匹配度/;}}/g/;
        totalScore -= patternSymptom.weight * 0.5;}
      }
    });
const score = maxPossibleScore > 0 ? totalScore / maxPossibleScore : 0;/;,/g,/;
  confidence: Math.min(score * (matchedSymptoms.length / pattern.mainSymptoms.length), 1);/;,/g/;
return {score: Math.max(score, 0)}matchedSymptoms,;
}
      confidence: Math.max(confidence, 0)}
    ;};
  }

  /* 案 *//;/g/;
   *//;,/g/;
const public = getConstitutionProfile(constitution: ConstitutionType): ConstitutionProfile | null {}}
    return this.constitutionProfiles.get(constitution) || null;}
  }

  /* 式 *//;/g/;
   *//;,/g/;
const public = getSyndromePattern(patternId: string): SyndromePattern | null {}}
    return this.syndromePatterns.get(patternId) || null;}
  }

  /* 息 *//;/g/;
   *//;,/g/;
const public = getHerbProfile(herbName: string): HerbProfile | null {}}
    return this.herbDatabase.get(herbName) || null;}
  }

  /* 息 *//;/g/;
   *//;,/g/;
const public = getFormulaProfile(formulaName: string): FormulaProfile | null {}}
    return this.formulaDatabase.get(formulaName) || null;}
  }

  /* 息 *//;/g/;
   *//;,/g/;
const public = getMeridianProfile(meridianName: string): MeridianProfile | null {}}
    return this.meridianSystem.get(meridianName) || null;}
  }

  /* 息 *//;/g/;
   *//;,/g/;
const public = getOrganProfile(organName: string): OrganProfile | null {}}
    return this.organSystem.get(organName) || null;}
  }
}

// 接口定义/;,/g/;
export interface SyndromePattern {name: string}category: string,;
pathogenesis: string,;
mainSymptoms: PatternSymptom[],;
tongueManifestations: TongueManifestations,;
pulseManifestations: string[],;
treatmentPrinciple: string,;
recommendedFormulas: string[],;
contraindications: string[],;
prognosis: string,;
}
}
  const differentialDiagnosis = string[];}
}

export interface PatternSymptom {name: string}weight: number,;
}
}
  const required = boolean;}
}

export interface TongueManifestations {tongueBody: string,;}}
}
  const tongueCoating = string;}
}

export interface ConstitutionProfile {name: string}characteristics: string[],;
physicalTraits: PhysicalTraits,;
psychologicalTraits: PsychologicalTraits,;
susceptibleDiseases: string[],;
adaptationCapacity: AdaptationCapacity,;
}
}
  const healthMaintenance = HealthMaintenance;}
}

export interface PhysicalTraits {complexion: string}bodyType: string,;
energy: string,;
sleep: string,;
}
}
  const appetite = string;}
}

export interface PsychologicalTraits {personality: string}emotion: string,;
}
}
  const stress = string;}
}

export interface AdaptationCapacity {climate: string}season: string,;
}
}
  const environment = string;}
}

export interface HealthMaintenance {diet: string}exercise: string,;
lifestyle: string,;
}
}
  const emotion = string;}
}

export interface HerbProfile {name: string}latinName: string,;
category: string,;
subCategory: string,;
nature: string,;
flavor: string[],;
meridians: string[],;
functions: string[],;
indications: string[],;
dosage: string,;
contraindications: string[],;
incompatibilities: string[],;
processing: string[],;
}
}
  const modernPharmacology = ModernPharmacology;}
}

export interface ModernPharmacology {activeComponents: string[]}pharmacologicalEffects: string[],;
}
}
  const clinicalApplications = string[];}
}

export interface FormulaProfile {name: string}category: string,;
subCategory: string,;
composition: FormulaComponent[],;
functions: string[],;
indications: string[],;
contraindications: string[],;
modifications: FormulaModification[],;
preparation: string,;
dosage: string,;
}
}
  const modernApplications = string[];}
}

export interface FormulaComponent {herb: string}dosage: string,;
}
}
  const role = string;}
}

export interface FormulaModification {condition: string}addition: string[],;
}
}
  const removal = string[];}
}

export interface MeridianProfile {name: string}abbreviation: string,;
type: string,;
pairedOrgan: string,;
flowDirection: string,;
peakTime: string,;
mainFunctions: string[],;
pathology: string[],;
}
}
  const keyPoints = AcupointProfile[];}
}

export interface AcupointProfile {name: string}location: string,;
}
}
  const functions = string[];}
}

export interface OrganProfile {name: string}category: string,;
element: string,;
season: string,;
emotion: string,;
tissue: string,;
sensoryOrgan: string,;
fluid: string,;
mainFunctions: string[],;
physiologicalCharacteristics: string[],;
pathologicalManifestations: string[],;
}
}
  const commonSyndromes = string[];}
}

export interface SymptomInput {name: string}const severity = number;
duration?: string;
}
}
  frequency?: string;}
}

export interface PatternAnalysisResult {primaryPattern: PatternMatch | null}alternativePatterns: PatternMatch[],;
confidence: number,;
recommendations: TreatmentRecommendation[],;
}
}
  const timestamp = Date;}
}

export interface PatternMatch {patternId: string}pattern: SyndromePattern,;
score: number,;
matchedSymptoms: MatchedSymptom[],;
}
}
  const confidence = number;}
}

export interface PatternMatchResult {score: number}matchedSymptoms: MatchedSymptom[],;
}
}
  const confidence = number;}
}

export interface MatchedSymptom {symptomName: string}userSeverity: number,;
patternWeight: number,;
}
}
  const score = number;}
}
';,'';
export interface TreatmentRecommendation {';,}type: 'formula' | 'principle' | 'contraindication' | 'lifestyle';','';
title: string,';,'';
content: string,';'';
}
}
  const priority = 'high' | 'medium' | 'low';'}'';'';
}

export default TCMOntologyModel;';'';
''';