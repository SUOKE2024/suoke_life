
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="简单算诊服务器")


@app.get("/")
def root():
    return {"message": "简单算诊服务器运行中"}


def main() -> None:
    """主函数 - 启动简单服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8003)


if __name__ == "__main__":
    main()
