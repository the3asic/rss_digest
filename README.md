## 项目简介

本项目是一个自动化处理和生成新闻通讯的系统。它从 RSS 源获取文章，进行评分和摘要生成，并最终生成包含文章摘要的 HTML 新闻通讯。

## 文件结构

- main.py: 主脚本，依次运行其他脚本。
- rss_digest.py: 从 RSS 源获取文章并保存为 CSV 文件。
- rating-openai.py: 使用自定义 API 对文章进行评分，并将高评分文章复制到指定目录。
- summerize-high-rated.py: 对高评分文章进行摘要生成，并保存摘要。
- make_newsletter.py: 生成包含文章摘要的 HTML 新闻通讯。
- renderpng.py: 将 HTML 新闻通讯渲染为 PNG 图片。
- cleanup.py: 清理生成的文件和目录，并创建归档。

## 环境配置

### 依赖安装

请确保已安装以下依赖项。可以使用以下命令安装：

```bash
pip install -r requirements.txt
```

### 环境变量

在项目根目录下创建一个 `.env` 文件，并添加以下内容：

```
CUSTOM_API_URL=https://api.openai.com/v1/chat/completions  # 自定义 OpenAI 兼容 API 的 URL，用于文章评分和摘要生成
API_KEY=your_api_key  # 访问自定义 API 的密钥
RATING_CRITERIA=your_rating_criteria  # 文章评分的标准或规则
TOP_ARTICLES=5  # 选择评分最高的前几篇文章
NEWSLETTER_TITLE=文章摘要通讯  # 生成的新闻通讯的标题
NEWSLETTER_FONT=Arial, sans-serif  # 新闻通讯中使用的字体
WIDTH=800  # 渲染 HTML 新闻通讯时的宽度
KEYWORDS=keyword1,keyword2  # 用于筛选文章的关键字，多个关键字用逗号分隔
THREADS=10  # 并发处理 RSS 源时使用的线程数
DATE_RANGE_DAYS=7  # 获取 RSS 源文章的日期范围（天数）
```

## 使用方法

### 准备工作

请将您的订阅 OPML 文件保存在当前目录下，并重命名为 `feeds.opml`。

### 运行主脚本

在项目根目录下运行以下命令：

```bash
python3 main.py
```

该命令将依次运行所有子脚本，完成从文章获取、评分、摘要生成到新闻通讯生成的全过程。

## 注意事项

- 请确保在运行脚本前已正确配置环境变量。
- 运行过程中可能需要网络连接以访问 RSS 源和自定义 API。
- 默认使用 OpenAI 的 GPT-3.5-Turbo 模型进行评分，如果需要使用其他模型，请修改 `rating-openai.py` 中的 `model` 变量。
- 默认使用 OpenAI 的 GPT-4o 模型进行摘要生成，如果需要使用其他模型，请修改 `summerize-high-rated.py` 中的 `model` 变量。

## 贡献

欢迎提交 Pull Request 或报告问题。如果有任何建议或改进，请随时联系。

## 许可证

本项目采用 MIT 许可证。详细信息请参阅 LICENSE 文件。