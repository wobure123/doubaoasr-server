# doubaoime-asr-server

> 将[豆包输入法 ASR](https://github.com/starccy/doubaoime-asr) 封装为本地 OpenAI 兼容 HTTP 服务，供 LazyTyper 等工具直接调用。

## 下载即用（推荐）

前往 [Releases](../../releases) 页面，下载最新的 `doubaoime-asr-server.exe`，双击运行即可。无需安装 Python 或任何依赖。

## 配置 LazyTyper

运行 exe 后，在 LazyTyper 的 **OpenAI兼容渠道** 中填写：

| 字段 | 值 |
|------|----|
| 模型名称 | `doubaoime-asr`（任意字符串） |
| API Endpoint | `http://127.0.0.1:5050` |
| API 密钥 | `local`（任意非空字符串） |

## 工作原理

```
麦克风 → LazyTyper → GET /v1/models / POST /v1/audio/transcriptions
                              ↓
                   doubaoime-asr-server (本地 :5050)
                              ↓
                   doubaoime_asr Python 库
                              ↓
                   豆包输入法 ASR 服务（云端）
                              ↓
                   { "text": "识别结果" } → LazyTyper
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ASR_HOST` | `127.0.0.1` | 监听地址 |
| `ASR_PORT` | `5050` | 监听端口 |
| `ASR_CREDENTIAL_PATH` | `%USERPROFILE%\.config\doubaoime-asr\credentials.json` | 凭据缓存路径 |

> 如果接入工具会先请求 `/v1/models` 做密钥校验，请把 API Endpoint 填成 `http://127.0.0.1:5050`。服务同时支持 `/v1/models` 和 `/v1/audio/transcriptions`。

## 自行构建

### 本地构建

```powershell
pip install "git+https://github.com/starccy/doubaoime-asr.git" pyinstaller aiohttp
pyinstaller server.spec --clean --noconfirm
# 输出：dist\doubaoime-asr-server.exe
```

### 通过 GitHub Actions 构建

1. Fork 本仓库
2. 推送一个 `v*` 格式的 Tag（如 `v1.0.0`），Actions 将自动构建并发布 Release：

```bash
git tag v1.0.0
git push origin v1.0.0
```

也可以在 Actions 页面手动触发 **Build & Release Windows EXE**。

## 注意事项

- 本项目基于 [doubaoime-asr](https://github.com/starccy/doubaoime-asr)，属非官方实现，服务端协议可能随时变更。
- 首次运行会联网注册虚拟设备并缓存凭据，此后凭据自动复用。
- 需要保持网络连接，识别在豆包 ASR 云端完成。

## License

MIT
