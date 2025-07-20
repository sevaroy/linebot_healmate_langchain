# 安全性說明

## API Key 管理

### ⚠️ 重要安全提醒

- **絕對不要** 將 API key 直接寫入程式碼或配置文件
- **絕對不要** 將包含 API key 的文件提交到 Git 版本控制
- 所有敏感信息都應該通過環境變數傳遞

### 環境變數設定

系統使用以下環境變數：

```bash
# OpenAI API (主要用於 GraphRAG)
OPENAI_API_KEY="your_openai_api_key_here"

# DeepSeek API (備用選項)
DEEPSEEK_API_KEY="your_deepseek_api_key_here"

# LINE Bot
LINE_CHANNEL_SECRET="your_line_channel_secret_here"
LINE_CHANNEL_ACCESS_TOKEN="your_line_channel_access_token_here"
```

### GraphRAG 安全實作

1. **配置文件安全**：
   - 使用 `graphrag init` 建立基本配置
   - 透過環境變數 `GRAPHRAG_API_KEY` 傳遞 API key
   - 配置文件不包含任何敏感信息

2. **文件忽略**：
   - `.gitignore` 已設定忽略所有 GraphRAG 相關敏感文件
   - 包括 `settings.yaml`、`cache/`、`output/` 等目錄

3. **執行時安全**：
   - API key 只在程序執行時通過環境變數傳遞
   - 不會永久儲存在文件系統中

## 安全檢查清單

- [ ] 確認 `.env` 文件在 `.gitignore` 中
- [ ] 確認沒有硬編碼的 API key
- [ ] 確認 GraphRAG 配置文件不包含敏感信息
- [ ] 定期檢查是否有意外洩露的敏感信息

## 如果發生 API Key 洩露

1. **立即撤銷** 洩露的 API key
2. **生成新的** API key
3. **更新環境變數** 
4. **檢查 Git 歷史** 是否需要清理
5. **重新部署** 系統

## 聯絡信息

如果發現安全問題，請立即報告給開發團隊。