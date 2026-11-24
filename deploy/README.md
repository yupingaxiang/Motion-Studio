# Ubuntu 部署与 GitHub 发布

部署目标：`yupingaxiang/Motion-Studio` 的 `main`，Ubuntu 24.04 x86_64，Docker Compose。首版运行工作台和 API；Remotion 离线渲染和 Whisper 时间戳识别仍在有相应运行时的制作机执行。

1. 在可信电脑生成专用发布密钥（例如 `ssh-keygen -t ed25519 -f motion-studio-deploy -C motion-studio-actions`）。为无人值守发布生成一把独立密钥，不使用个人登录密钥。不要把密钥文件放在仓库目录。
2. 在现有 MobaXterm root 会话里检查 `ss -ltn '( sport = :18000 )'`。端口空闲后，创建专用账号（如 `adduser --disabled-password --gecos '' motion-deploy`），再执行 `usermod -aG docker motion-deploy`。Docker 组权限等同于可取得 root 权限，生产 Environment 应只允许可信的 `main` 发布。在该账号的 `~/.ssh/authorized_keys` 加入刚生成的**公钥**，建议在该行开头加 `restrict `；`.ssh` 权限为 700，文件权限为 600，所有者是 `motion-deploy`。
3. 在既有可信服务器会话内运行 `awk '{print "85.202.207.9 " $1 " " $2}' /etc/ssh/ssh_host_ed25519_key.pub`，取得完整的 SSH 主机公钥行。在仓库 Settings → Environments 建立 `production`，添加四个 Secrets：`DEPLOY_HOST`（`85.202.207.9`）、`DEPLOY_USER`（`motion-deploy`）、`DEPLOY_SSH_KEY`（专用私钥全文）、`DEPLOY_KNOWN_HOSTS`（上面的完整主机公钥行）。私钥只填到 GitHub Secrets，不发到聊天。
4. 将 `Dockerfile`、`.dockerignore`、`deploy/` 和 `.github/workflows/deploy.yml` 提交并推送到 `main`。在 Actions → Deploy Motion Studio → Run workflow，选 `main`，发起部署。每次发布新版本均从这里新开一次运行。
5. 容器只监听服务器本机 `127.0.0.1:18000`。在自己的电脑开 SSH 转发：`ssh -N -L 18000:127.0.0.1:18000 <你现有的服务器登录账号>@85.202.207.9`，或在 MobaXterm 使用 Tunneling。然后打开 `http://127.0.0.1:18000/`。如果后续需要公开访问，先加认证和 HTTPS，再接入现有反向代理。

Compose 使用 `motion-studio_project-data` 和 `motion-studio_shared-assets` 保存项目文件及公共素材。首次部署为空，不把制作机的项目自动传到服务器。发布会检查应用健康，失败会尝试恢复上一版镜像；不要用 `docker compose down -v`，那会删除持久卷。正式迁移现有项目资料前先备份。
