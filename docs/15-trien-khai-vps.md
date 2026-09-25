# Yêu cầu thiết lập VPS

Tài liệu này dành cho **đội IT cấp VPS**. Nó chỉ liệt kê những việc cần IT làm. Phần cài đặt và vận
hành công cụ do team nội dung tự làm sau khi nhận máy.

Công cụ này không phải dịch vụ web. Nó không nhận request nào từ internet, không có database và không
có web server. Nó chỉ chủ động gọi ra Lark, WordPress `muaban.net/blog` và Claude.

---

## 1. Máy

| Hạng mục | Yêu cầu |
|---|---|
| Hệ điều hành | Ubuntu 24.04 LTS, 64-bit |
| CPU | 2 vCPU |
| RAM | 4 GB — agent Claude Code chạy nền, Anthropic khuyến nghị tối thiểu 4 GB |
| Ổ đĩa | 40 GB SSD |
| GPU | Không cần |

## 2. Phần mềm cần cài

```bash
sudo apt update
sudo apt install -y python3 git tmux unzip curl locales fail2ban

# Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

| Gói | Phiên bản |
|---|---|
| Python | 3.10 trở lên (Ubuntu 24.04 có sẵn 3.12). **Không cần cài gói pip nào** |
| Node.js + npm | 20 LTS |
| `git`, `tmux`, `unzip`, `curl`, `locales`, `fail2ban` | Bản của apt |

**Không cần:** Docker, database, web server (nginx/apache).

## 3. Cấu hình hệ thống

```bash
# Locale UTF-8 — bat buoc, noi dung la tieng Viet
sudo locale-gen C.UTF-8
sudo update-locale LANG=C.UTF-8

# Mui gio
sudo timedatectl set-timezone Asia/Ho_Chi_Minh

# User rieng de chay cong cu, khong dung root
sudo adduser --disabled-password --gecos "" contentseo
sudo usermod -aG sudo contentseo      # sudo trong luc cai dat
```

## 4. SSH: vào được từ mọi máy, ở bất cứ đâu

Người vận hành làm việc từ nhiều máy (laptop công ty, máy ở nhà, điện thoại) và từ bất kỳ mạng nào.
Vì vậy **không giới hạn IP** cho port SSH.

Bù lại việc mở cho mọi IP, cấu hình trong `/etc/ssh/sshd_config`:

```
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
```

rồi `sudo systemctl restart ssh` và `sudo systemctl enable --now fail2ban`.

**Khoá SSH:** đặt các public key dưới đây vào `/home/contentseo/.ssh/authorized_keys`, mỗi máy một
dòng, chép **nguyên dòng**:

| Máy | Public key |
|---|---|
| Laptop của Khá | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEhdHf+uzVXZ5HjmVC/QZYNF1mRACYUQW/EWLqfmi6xT lemin@Kha` |

Dấu vân tay để đối chiếu sau khi đặt khoá (`ssh-keygen -lf authorized_keys`):
`SHA256:WfbPGAeJh38SViPaTHsZERtXRfeEg5GOYYdbZgvuPn4`

Lệnh đặt khoá:

```bash
sudo mkdir -p /home/contentseo/.ssh
sudo nano /home/contentseo/.ssh/authorized_keys      # dan cac dong public key
sudo chown -R contentseo:contentseo /home/contentseo/.ssh
sudo chmod 700 /home/contentseo/.ssh
sudo chmod 600 /home/contentseo/.ssh/authorized_keys
```

Về sau người vận hành tự thêm và gỡ khoá trong file này, không cần IT làm lại.

Nếu policy của công ty bắt buộc giới hạn IP, xin cấp **tài khoản VPN** để người vận hành vẫn làm việc
được khi không ở văn phòng.

## 5. Port

| Chiều | Port | Ghi chú |
|---|---|---|
| Vào | **22/TCP** | Mở cho mọi IP, như mục 4 |
| Vào | 80, 443 | **Không mở.** Không cần domain, reverse proxy hay HTTPS |
| Ra | **443/TCP** | Mở ra internet |

Chiều ra nên mở chung, vì agent phải tra văn bản pháp luật và nguồn chính thống trên nhiều trang khác
nhau. Nếu bắt buộc whitelist, các domain tối thiểu là:

| Domain | Dùng cho |
|---|---|
| `*.larksuite.com` | Lark Base, nơi duyệt bài |
| `muaban.net` | Tạo bản nháp WordPress |
| `api.anthropic.com`, `claude.ai` | Agent Claude Code |
| `github.com`, `api.github.com` | Lấy mã nguồn (repo private) |
| `registry.npmjs.org`, `deb.nodesource.com`, kho apt của Ubuntu | Cài gói |
| `commons.wikimedia.org`, `upload.wikimedia.org`, `api.openverse.org` | Tìm ảnh có giấy phép |

## 6. Lưu trữ và sao lưu

Toàn bộ dữ liệu là file trong `/home/contentseo/apps/content-seo`, không có database. Xin
**snapshot định kỳ** theo policy backup chung của server.

## 7. Secret và credential

IT **không cần cấp** mật khẩu hay token nào của công cụ. Mật khẩu ứng dụng WordPress, đăng nhập Lark
và đăng nhập Claude do team nội dung tự cấu hình sau khi nhận máy.

## 8. Bàn giao

Gửi lại cho người yêu cầu: **IP của VPS** và tên user **`contentseo`**. Người yêu cầu sẽ thử
`ssh contentseo@<ip>` từ máy của mình để xác nhận vào được.
