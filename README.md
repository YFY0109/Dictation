# 单词听写应用 (Dictation App)

## 简介
这是一个为班级英语教学开发的简易单词听写 Web 应用，支持从 Excel 导入词汇表，提供听写、答案查看和单词编辑功能。

## 功能特性
- **数据导入**：支持从 Excel (`.xls`) 导入人教版词汇表。
- **听写模式**：
    -   按单元选择听写内容。
    -   自动倒计时切换单词。
    -   支持暂停/继续、上/下一个单词控制。
    -   显示词性、翻译或短语提示。
- **答案查看**：听写完成后可查看完整单词列表及翻译。
- **单词编辑**：支持在线新增、修改、删除单词。
- **设置**：自定义单词显示时长（默认 10 秒）。

## 技术栈
- **后端**：Python 3.12+, Flask, SQLite
- **前端**：HTML5, CSS3, JavaScript (原生)

## 安装与运行

### 1. 环境准备
确保已安装 Python 3.12+。建议使用 `uv` 管理虚拟环境。

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖
uv pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python init_db.py
```

### 3. 导入数据
将 `人教版词汇表.xls` 放入项目根目录，运行：
```bash
python import_excel.py
```

### 4. 启动应用
```bash
python app.py
```
访问浏览器：`http://127.0.0.1:5000`

## 目录结构
```
/
├── app.py              # Flask 主应用
├── config.py           # 配置文件
├── init_db.py          # 数据库初始化脚本
├── import_excel.py     # Excel 导入脚本
├── fix_data.py         # 数据修复脚本
├── schema.sql          # 数据库结构 SQL
├── requirements.txt    # 依赖列表
├── static/             # 静态资源 (JS/CSS)
└── templates/          # HTML 模板
```

## 注意事项
- 默认导入的 Excel 文件需符合特定格式（参见 `import_excel.py` 注释）。
- 数据库文件为 `dictation.db`，即使重启应用数据也会保留。
