# 上海科技大学 课程成绩与 GPA 独立分析看板 (Standalone Project)

本文件夹是一个**完全独立、自包含**的课程数据分析子项目。您可以将其整体移动或复制到系统的任何地方独立使用，无需依赖父目录中的其它学生画像或通讯录脚本。

---

## 1. 项目文件清单

* **`index.html`**：主看板页面。严格遵循微软 Fluent Design 2 暗色/亮色规范，提供课程模糊搜索、前缀药丸过滤、给分绩点频数分布直方图、历史绩点均值趋势折线图、修读名单花名册、以及可点击穿透的学生联系人卡片微窗。
* **`chart.local.js`**：本地离线 Chart.js 库，为成绩直方图和历史走势折线图提供本地离线绘制支持。
* **`download_courses.py`**：轻量级、独立的教务系统课程下载脚本。支持分页抓取全量本科生和研究生课程。
* **`README.md`**：本说明文档。
* **初始缓存数据文件** (可由爬虫及外部数据库合并更新)：
  * `undergrad_courses.json`：本科生课程大纲列表缓存。
  * `grad_courses.json`：研究生及本研一体课程大纲列表缓存。
  * `shanghaitech_personnel_master.json`：全量学生学籍画像、联系方式以及课程成绩的大宽表（网页看板将直接在此文件的基础上进行前端计算）。

---

## 2. 快速启动与查看

看板运行不需要任何后台服务支持，只需以静态网页文件或本地 Web 服务加载即可：
1. 打开您的终端，进入本目录：
   ```bash
   cd "/path/to/course_analytics"
   ```
2. 启动 Python 自带的轻量级 Web 服务：
   ```bash
   python3 -m http.server 8000
   ```
3. 在浏览器（推荐使用 Chrome 或 Edge）中打开：
   `http://localhost:8000/`

---

## 3. 如何下载与更新课程数据

### 3.1 本科生课程（免登录公开接口）
* 运行更新脚本时，本科生课程数据会自动抓取并覆盖 `undergrad_courses.json`，无需进行账号配置。

### 3.2 研究生课程（受单点登录 SSO 鉴权保护）
研究生及本研一体课程必须在 Header 中携带您的教务系统登录会话 Cookie 才能拉取。
1. 在浏览器中打开并登录 [上海科技大学教务系统 (EAMS)](https://eams.shanghaitech.edu.cn/)。
2. 登录成功后，按下键盘 <code>F12</code> 键打开开发者工具，切换到 **Console (控制台)**。
3. 在控制台输入并执行指令：
   ```javascript
   copy(document.cookie)
   ```
   *执行后，会话 Cookie 文本会存入您的剪贴板。*
4. 在本目录下新建或编辑名为 **`sso_cookie.txt`** 的纯文本文件。
5. 将复制的内容粘贴并保存进去（只需粘贴那段 `JSESSIONID=xxx; casp-portal=yyy` 格式的字符串即可）。

### 3.3 运行抓取命令
在当前目录下运行抓取脚本：
```bash
python3 download_courses.py
```
脚本将依次完成本科生与研究生课程的爬取更新，生成最新的 `undergrad_courses.json` 和 `grad_courses.json` 供网页看板读取渲染。

---

## 4. 常见问题 (FAQ)

* **点击修读名字无法查看照片或手机号？**
  * 请确保 `shanghaitech_personnel_master.json` 中包含对应学生的信息，且本目录同级存在 `fig/` 文件夹（内存放照片命名格式为 `{学号}-{姓名}.jpg`）。如果没有照片，微窗会自动退化为姓名首字母生成的文字头像。
