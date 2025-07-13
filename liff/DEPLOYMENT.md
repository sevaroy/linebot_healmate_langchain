# LINE LIFF 前端部署指南

本文件提供將 LIFF 前端應用程序部署到 Netlify 或 Vercel 的詳細步驟。

## 準備工作

1. 確保你有有效的 LIFF ID（已在環境變數中設置）
2. 確保所有依賴項都已安裝：`npm install`
3. 測試應用程序可在本地正常運行：`npm run dev`

## 方案 1：部署到 Netlify

### 使用 Netlify CLI

1. 安裝 Netlify CLI：
   ```bash
   npm install -g netlify-cli
   ```

2. 在項目根目錄 (`/liff`) 構建應用程序：
   ```bash
   npm run build
   ```

3. 登錄到 Netlify：
   ```bash
   netlify login
   ```

4. 部署到 Netlify：
   ```bash
   netlify deploy --prod
   ```

### 使用 Netlify 網站

1. 訪問 [Netlify](https://www.netlify.com/) 並登錄
2. 點擊「New site from Git」
3. 選擇你的 Git 供應商（GitHub, GitLab 等）
4. 選擇含有 LIFF 前端的存儲庫和分支
5. 在構建設置中：
   - 構建命令：`npm run build`
   - 發布目錄：`dist`
6. 點擊「Deploy site」

## 方案 2：部署到 Vercel

### 使用 Vercel CLI

1. 安裝 Vercel CLI：
   ```bash
   npm install -g vercel
   ```

2. 登錄到 Vercel：
   ```bash
   vercel login
   ```

3. 部署到 Vercel：
   ```bash
   vercel --prod
   ```

### 使用 Vercel 網站

1. 訪問 [Vercel](https://vercel.com/) 並登錄
2. 點擊「New Project」
3. 匯入你的 Git 存儲庫
4. 配置你的項目：
   - Framework Preset：Vite
   - 根目錄：`liff/`（如果整個存儲庫不只包含前端項目）
5. 在環境變數中添加：
   - `VITE_LIFF_ID`：你的 LIFF ID
6. 點擊「Deploy」

## 部署後配置

1. 獲取部署的 URL（例如：`https://your-app.netlify.app` 或 `https://your-app.vercel.app`）
2. 登錄到 [LINE Developers Console](https://developers.line.biz/)
3. 選擇你的 LIFF 應用
4. 在 LIFF 設置中更新 Endpoint URL 為你的部署 URL
5. 儲存更改

## 測試部署

1. 使用 LINE 掃描 QR 碼或直接在 LINE 中訪問你的 LIFF 應用
2. 確認所有功能正常運作
3. 檢查與後端 API 的連接是否正常

## 故障排除

如果遇到問題，請檢查：

1. 環境變數是否正確設置
2. 前端 API URL 是否指向正確的後端
3. LINE LIFF SDK 是否正確初始化
4. 瀏覽器控制台是否有錯誤
5. Netlify/Vercel 的部署日誌

## 注意事項

- 對於生產環境，請確保將 `VITE_API_URL` 更新為生產後端 API 的 URL
- 確保後端 CORS 設置允許來自你的部署域名的請求
- 考慮設置自定義域名以提高專業性和品牌認同感
