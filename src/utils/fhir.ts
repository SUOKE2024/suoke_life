// FHIR健康数据标准工具（前端TypeScript版）
// 支持健康数据采集、存储、交换的FHIR格式转换与校验
export interface FhirObservation {resourceType: "Observation";
  status: string;
  category: Array<{
    coding: Array<{
      system: string;
      code: string}>;
  }>;
  code: {
    coding: Array<{
      system: string;
      code: string;
      display: string}>;
  };
  subject: {
    reference: string};
  effectiveDateTime?: string;
  valueQuantity: {
    value: number;
    unit: string;
    system: string;
    code: string}
}
// 体温采集转FHIR Observation;
export function toFhirObservationTemperature(;
  userId: string,value: number,unit = "Celsius",effectiveTime?: string;
): FhirObservation {
  return {
    resourceType: "Observation",
    status: "final",
    category: [{
      coding: [{
        system: "http:// terminology.hl7.org/CodeSystem/////    observation-category",
        code: "vital-signs";
      }];
    }],code: {coding: [{system: "http:// loinc.org",code: "8310-5",display: "Body temperature";
      }];
    },subject: { reference: `Patient/////    ${userId}` },effectiveDateTime: effectiveTime,valueQuantity: {value,unit,system: "http:// unitsofmeasure.org",code: unit;
    }
  }
}
// 血压Observation;
export function toFhirObservationBloodPressure(;
  userId: string,systolic: number,diastolic: number,unit = "mmHg",effectiveTime?: string;
): any {
  return {
    resourceType: "Observation",
    status: "final",
    category: [{
      coding: [{
        system: "http:// terminology.hl7.org/CodeSystem/////    observation-category",
        code: "vital-signs"
      }]
    }],
    code: {
      coding: [{
        system: "http:// loinc.org",
        code: "85354-9",
        display: "Blood pressure panel"
      }];
    },subject: { reference: `Patient/////    ${userId}` },effectiveDateTime: effectiveTime,component: [{code: {coding: [{system: "http:// loinc.org",code: "8480-6",display: "Systolic blood pressure";
        }];
      },valueQuantity: {value: systolic,unit,system: "http:// unitsofmeasure.org",code: unit;
      }
    }, {
      code: {
        coding: [{
          system: "http:// loinc.org",
          code: "8462-4",
          display: "Diastolic blood pressure"
        }]
      },
      valueQuantity: {
        value: diastolic,
        unit,
        system: "http:// unitsofmeasure.org",
        code: unit;
      }
    }]
  }
}
// 心率Observation;
export function toFhirObservationHeartRate(;
  userId: string,value: number,unit = "bpm",effectiveTime?: string;
): any {
  return {
    resourceType: "Observation",
    status: "final",
    category: [{
      coding: [{
        system: "http:// terminology.hl7.org/CodeSystem/////    observation-category",
        code: "vital-signs";
      }];
    }],code: {coding: [{system: "http:// loinc.org",code: "8867-4",display: "Heart rate";
      }];
    },subject: { reference: `Patient/////    ${userId}` },effectiveDateTime: effectiveTime,valueQuantity: {value,unit,system: "http:// unitsofmeasure.org",code: unit;
    }
  }
}
// FHIR Observation校验（简化版）
export function validateFhirObservation(obs: any): obs is FhirObservation {
  return (;
    obs &&;
    obs.resourceType === "Observation" &&;
    typeof obs.status === "string" &&;
    obs.code &&;
    obs.subject &&;
    obs.valueQuantity;
  )
}
