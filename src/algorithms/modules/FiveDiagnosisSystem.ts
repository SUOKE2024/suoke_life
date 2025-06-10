import { EventEmitter } from "events";";
export class FiveDiagnosisSystem extends EventEmitter {private lookDiagnosis: LookDiagnosisModule;,}private listenDiagnosis: ListenDiagnosisModule;
private inquiryDiagnosis: InquiryDiagnosisModule;
private pulseDiagnosis: PulseDiagnosisModule;
private palpationDiagnosis: PalpationDiagnosisModule;
private synthesisEngine: DiagnosisSynthesisEngine;
constructor() {super();,}this.lookDiagnosis = new LookDiagnosisModule();
this.listenDiagnosis = new ListenDiagnosisModule();
this.inquiryDiagnosis = new InquiryDiagnosisModule();
this.pulseDiagnosis = new PulseDiagnosisModule();
this.palpationDiagnosis = new PalpationDiagnosisModule();
}
    this.synthesisEngine = new DiagnosisSynthesisEngine();}
  }
  /* " *//;"/g"/;
  */"/"/g"/;