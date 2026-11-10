# bbox

个人命令行工具集。一个 Python 包提供多个独立命令，由 uv 统一管理安装、依赖和卸载。包名是 `saltbo-bbox`，仓库名是 `bbox`。

## 安装

需要 Python 3.11+、uv 和 Git。可直接从公开的 GitHub 仓库安装，无需发布到 PyPI。

```sh
uv tool install git+https://github.com/saltbo/bbox.git
bbox
```

命令入口默认安装到 `~/.local/bin`，工具环境在 `~/.local/share/uv/tools/saltbo-bbox`。可用 `uv tool dir --bin` 查询入口目录。

本地开发推荐：

```sh
git clone https://github.com/saltbo/bbox.git
cd bbox
uv sync
uv tool install --editable .
```

修改 Python 或 Shell 源文件后立即生效；修改依赖或增加命令后重新安装。Git 安装可用 `uv tool upgrade saltbo-bbox` 更新，`uv tool uninstall saltbo-bbox` 卸载全部入口。

## 命令

- Helm：`charts-pull`、`charts-push`、`charts-mirror`（默认读取当前目录的 `mirror.yaml`）。
- 容器：`docker-copy`、`nerdctl-copy`，以及经 Lima 调用的 `buildctl`、`containerd`、`nerdctl`、`runc`。
- Git：`git-cm`、`git-fire`、`git-update-history-author`。
- 其他：`httptun`、`mkcourse`、`bark-notify`、`completion-install`、`dns-flushall`、`goland`、`gpg-pk-update`、`ha-service-do`、`istioctl-vsw`、`kubectl-vsw`、`psh-ipsw`、`psh-sproute`、`with-warp`、`x-browse`、`create-local-script`。

原有命令名和用途保留；部分命令执行网络、系统配置、Git 提交/推送或历史改写，按原用途运行。它们可能依赖 macOS、Homebrew 工具、Lima、Helm、Docker、本机应用或 `~/.env` 中的个人配置。包不包含凭据。

`kubectl-vsw` 和 `istioctl-vsw` 将下载内容保存在 `~/.local/share/bbox/`，只在 `~/.local/bin` 创建活动版本入口；可用 `BBOX_BIN_DIR` 指定该入口目录。补全写入 `~/.local/share/zsh-completions`。`create-local-script` 在本地 bbox 仓库创建源码，默认仓库位置 `~/Develop/bogit/bbox`，可用 `BBOX_SOURCE_DIR` 修改；它会提示需要添加的命令声明。

## 开发

Python 命令放在 `src/bbox/` 并提供 `main()`，在 `pyproject.toml` 的 `[project.scripts]` 注册。Shell 命令放在 `src/bbox/scripts/`，入口声明为 `bbox.shell:main`；启动器通过对应的 shell 执行脚本，保留参数和退出码。

```sh
uv run python -m unittest discover -s tests -v
uv build
```

工具代码从 `saltbo/dotfiles` 的 chezmoi 脚本迁移而来，保留本机已有调整，并纳入此前尚未被 chezmoi 管理的 `mkcourse`、`with-warp` 和 `x-browse`。`git-fire` 原始来源为 <https://github.com/qw3rtman/git-fire>，保留脚本中的出处。
