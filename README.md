# AIAgentLab

## 环境设置

### 创建虚拟环境

使用以下命令以 Python 3.13 创建一个名为 `.venv` 的虚拟环境。

**对于 Windows (命令提示符或 PowerShell):**

```bash
py -3.13 -m venv .venv
```

**对于 macOS/Linux (bash/zsh):**

```bash
python3.13 -m venv .venv
```

### 激活虚拟环境

根据您的操作系统，运行对应的脚本来激活虚拟环境。

**对于 Windows (命令提示符或 PowerShell):**

```bash
.venv\Scripts\activate
```

**对于 macOS/Linux (bash/zsh):**

```bash
source .venv/bin/activate
```

### 生成依赖文件 (requirements.txt)

激活虚拟环境后，使用以下命令将当前环境中所有已安装的 Python 库及其版本记录到 `requirements.txt` 文件中。

```bash
pip freeze > requirements.txt
```

### 从文件安装依赖

当您需要在新环境中快速安装项目所需的所有依赖时，可以运行以下命令：

```bash
pip install -r requirements.txt
```

## 代码版本控制

### 更新本地代码

当 GitHub 上的远程仓库有新的提交记录，而您本地的仓库需要同步这些更新时，请使用以下命令。该命令会从远程仓库拉取最新的代码并合并到您当前的工作分支。

```bash
git pull
```