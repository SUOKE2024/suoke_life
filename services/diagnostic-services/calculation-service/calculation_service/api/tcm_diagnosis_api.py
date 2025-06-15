
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# from ..core.algorithms.tongue_pulse_analysis import TonguePulseAnalyzer

app = FastAPI(title="中医诊断API")


class DiagnosisRequest(BaseModel):
    """诊断请求模型"""
    patient_id: str
    symptoms: list[str] = []

@app.get("/")
def root():
    return {"message": "中医诊断API服务运行中"}


def main() -> None:
    """主函数 - 启动中医诊断API服务"""
    uvicorn.run(app, host="0.0.0.0", port=8004)


if __name__ == "__main__":
    main()
