# Cài đặt và vận hành công cụ trên VPS

Tài liệu này dành cho **team nội dung**, sau khi IT đã cấp VPS theo `docs/15-trien-khai-vps.md`.
Nó nói những việc mình tự làm: cài công cụ, đăng nhập, chạy hằng ngày, và xử lý lỗi.

---

## 1. Cái gì chạy trên VPS

| Phần | Bản chất |
|---|---|
| Bộ kiểm (`scripts/*.py`) | Python thuần, không cài gói ngoài |
| Đồng bộ Lark (`scripts/lark/`) | Gọi `@larksuite/cli` qua Node.js |
| Bản nháp WordPress (`scripts/wp/`) | Gọi REST API bằng application password |
| Viết nội dung | **Agent Claude Code** đọc `CLAUDE.md` và các skill rồi viết |

Phần viết bài **không phải một script**: không có lệnh nào sinh bài tự động. Agent Claude Code chạy nền
trong `tmux` trên VPS, nên biên tập duyệt trên Lark xong là agent làm tiếp. Hai cổng duyệt vẫn cần
**người thật** bấm trên Lark, và chi phí token tính theo tài khoản Claude (khoảng 20–55 triệu token
mỗi bài).

---

## 2. Cài đặt lần đầu

```bash
ssh contentseo@<ip-vps>

# Ma nguon
mkdir -p ~/apps && cd ~/apps
git clone https://github.com/khale125/content-seo.git
cd content-seo

# Locale cho moi phien
echo 'export LANG=C.UTF-8 PYTHONIOENCODING=utf-8' >> ~/.bashrc && source ~/.bashrc

# Lark CLI va Claude Code
sudo npm install -g @larksuite/cli @anthropic-ai/claude-code

# Kiem may + tao .env
bash install.sh
```

`install.sh` phải in **`Du dieu kien chay.`** và thoát mã 0. Nó chạy `scripts/preflight.py`: 19 mục
kiểm cộng bốn fixture hồi quy.

Repo là private nên `git clone` sẽ hỏi đăng nhập GitHub. Cách gọn nhất: cài `gh`
(`sudo apt install gh`), chạy `gh auth login`, rồi clone lại.

---

## 3. Mật khẩu và biến môi trường

Điền vào file `.env` mà `install.sh` vừa tạo, rồi `chmod 600 .env`. File này nằm trong `.gitignore`.

| Biến | Lấy ở đâu |
|---|---|
| `MBWP_USER` | Tên đăng nhập WordPress của biên tập viên |
| `MBWP_APP_PASSWORD` | WP Admin → Users → Profile → **Application Passwords**. Không phải mật khẩu đăng nhập |
| `LARK_NODE`, `LARK_CLI_ENTRY` | Tùy chọn, chỉ khi công cụ không tự tìm ra Node hoặc Lark CLI |

`wp_draft.py` tìm thông tin đăng nhập WordPress theo thứ tự: biến môi trường, rồi `.env`, rồi
`~/.muaban-wp.json`. Nguồn nào có trước thì thắng.

Về application password: nó bỏ qua xác thực hai lớp, thu hồi độc lập với mật khẩu chính, và chỉ hiện
một lần lúc tạo. Nên tạo **một cái riêng cho VPS**, để khi cần chặn máy chủ thì chỉ thu hồi đúng cái
đó. Đổi ngay cái nào đã từng bị dán vào chat hay ảnh chụp màn hình.

Hồ sơ đăng nhập Lark nằm ở `~/.lark-cli/`, trong đó có `appSecret` và token người dùng. Coi cả thư
mục đó như mật khẩu: không đưa vào git, không chép qua kênh không mã hoá.

---

## 4. Đăng nhập Lark trên máy không có màn hình

`lark auth login` mở một URL và chờ trình duyệt gọi ngược về `localhost` trên VPS. VPS không có
trình duyệt, nên phải chuyển tiếp cổng qua SSH từ máy cá nhân:

```bash
# tren may ca nhan
ssh -L 3000:localhost:3000 contentseo@<ip-vps>
# trong phien ssh do
lark auth login          # mo URL no in ra bang trinh duyet cua may ca nhan
```

Cổng thực tế do CLI quyết định. Nếu URL nó in ra không dùng cổng 3000, bạn mở lại tunnel đúng cổng
đó. Đăng nhập một lần là đủ, CLI tự làm mới token.

Cách khác là chép `~/.lark-cli/` từ máy đã đăng nhập sang VPS bằng `scp`, rồi `chmod 700`. Nhanh hơn,
nhưng VPS từ đó hành động dưới tên người đã đăng nhập: mọi dòng Nhật ký trên Base sẽ ghi tên người đó.

Kiểm bằng `python3 scripts/preflight.py --lark` và `python3 scripts/lark/lark_sync.py status`.

---

## 5. Cấu hình Lark Base

`scripts/lark/config.json` trỏ tới Base đang chạy thật của team. Giữ nguyên nếu VPS tiếp tục công việc
đang dở.

Muốn dựng một Base riêng để thử thì sao `config.example.json` thành `config.json`, rồi chạy:

```bash
python3 scripts/lark/lark_setup.py --title "Content SEO — thử nghiệm"
python3 scripts/lark/lark_setup.py --verify
```

**Đừng sửa tên cột bằng tay trên Base.** Sửa `scripts/lark/schema.py` rồi chạy
`lark_setup.py --rebuild`. Trước khi `--rebuild` trên dữ liệu thật, nên chụp lại Base.

---

## 6. Chạy agent nền và chạy hằng ngày

Mở agent trong `tmux` để nó sống tiếp khi bạn thoát SSH:

```bash
tmux new -s content          # lan dau
tmux attach -t content       # nhung lan sau
cd ~/apps/content-seo && claude --permission-mode auto
```

**Phải chạy với `--permission-mode auto`.** Không có cờ này, mỗi lần agent chạy một lệnh là nó dừng lại chờ người bấm cho phép, và trên VPS không có ai ngồi đó. Đây là chế độ bạn đang dùng trên máy mình. Đừng dùng `--dangerously-skip-permissions`: cờ đó tắt hết mọi kiểm soát, kể cả những lệnh nên hỏi lại.

**Chi phí khi để agent trực liên tục.** Kênh theo dõi Lark hết hạn mỗi 29 phút và agent phải tự bật lại, mỗi lần như vậy là một lượt gọi đọc lại toàn bộ hội thoại. Để phiên chạy cả ngày thì hội thoại cứ dài thêm và mỗi lượt đắt dần. Nên mở phiên mới (`/clear`) sau khi xong mỗi bài, đúng như cách tiết kiệm token đã đo: chia phiên theo cổng duyệt rẻ hơn khoảng một nửa.

Thoát ra mà để agent chạy tiếp: `Ctrl+B` rồi `D`. Lần đầu mở `claude`, bạn cần đăng nhập tài khoản
Claude; làm giống cách đăng nhập Lark ở mục 4 nếu nó cần trình duyệt.

Các lệnh tay hay dùng:

```bash
python3 scripts/lark/lark_sync.py status               # xem toan bo bai
python3 scripts/lark/lark_watch.py --todo              # ma thoat 3 = dang co viec cho
python3 scripts/lark/lark_sync.py intake               # keo tu khoa moi tu Base
python3 scripts/run_qa.py work/<slug>/article.md       # kiem mot bai
python3 scripts/lark/lark_sync.py push work/<slug>     # day len Base cho nguoi duyet
python3 scripts/wp/wp_draft.py work/<slug>             # tao BAN NHAP sau khi bai da duyet
```

`wp_draft.py` chỉ tạo bản nháp: `status: draft` cố định trong code, và nó tự dừng nếu bài chưa được
duyệt trên Lark. **Bấm Publish là việc của người thật.**

---

## 7. Đặt lịch bằng cron

Chỉ đặt lịch những việc chỉ đọc hoặc chỉ kiểm:

```cron
# Suc khoe kho tri thuc, 6h sang moi ngay
0 6 * * * cd /home/contentseo/apps/content-seo && LANG=C.UTF-8 python3 scripts/wiki_lint.py >> logs/wiki-lint.log 2>&1
# Ban luu, 1h sang
0 1 * * * tar -czf /home/contentseo/backup/content-seo-$(date +\%F).tar.gz -C /home/contentseo/apps content-seo
```

**Không** đặt lịch cho `wp_draft.py` (nó ghi ra blog thật) và `lark_setup.py --rebuild` (nó sửa cấu
trúc Base).

---

## 8. Sao lưu

Ngoài snapshot của IT, ba thư mục sau quan trọng nhất và đều đã có trên GitHub, nên bạn nhớ `git push`
thường xuyên:

| Đường dẫn | Mất thì sao |
|---|---|
| `work/` | Mất các bài đang làm |
| `wiki/` | Bài sau phải tra nguồn lại từ đầu |
| `reference/` | Mọi ngưỡng giọng văn đo từ đây; mất là bộ kiểm hết cơ sở |

---

## 9. Bốn điều không làm

1. **Không tự động hoá bước Publish.** Bản nháp là điểm dừng cuối của máy.
2. **Không để script nào ghi "Đồng ý" vào ô Kết quả duyệt.** Chỉ người thật duyệt được.
3. **Không nới ngưỡng trong `scripts/lexicon/` để bài qua cửa.** Muốn đổi thì thêm bài thật vào
   `reference/muaban-blog/` rồi chạy lại `python3 scripts/house_voice_profile.py`.
4. **Không commit `.env`, `~/.muaban-wp.json` hay `~/.lark-cli/`.**

---

## 10. Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Xử lý |
|---|---|---|
| `UnicodeEncodeError` giữa chừng | Locale không phải UTF-8 | `export LANG=C.UTF-8 PYTHONIOENCODING=utf-8` |
| `Khong tim thay node` | Node không trong `PATH` | `export LARK_NODE=$(which node)` |
| `Khong tim thay @larksuite/cli` | Chưa cài toàn cục | `sudo npm i -g @larksuite/cli` |
| Lark báo `missing_scope` | App thiếu quyền Base | Xin cấp scope Bitable rồi đăng nhập lại |
| Lark báo `unauthorized` | Phiên đăng nhập hết hạn | `lark auth login` lại theo mục 4 |
| `wp_draft` báo 401 | Sai application password | Tạo application password mới |
| `wp_draft` báo cổng chưa mở | Bài chưa được duyệt, hoặc đã sửa sau khi duyệt | Duyệt lại trên Lark |
| Agent dừng khi thoát SSH | Chạy `claude` ngoài `tmux` | Mở lại trong `tmux` theo mục 6 |

---

## 11. Cần xin quyền từ đâu

| Cần | Xin ai |
|---|---|
| VPS | IT — theo `docs/15-trien-khai-vps.md` |
| Quyền vào Lark Base và scope Bitable | Quản trị Larksuite |
| Application password WordPress riêng cho VPS | Quản trị `muaban.net/blog` |
| Tài khoản Claude để chạy agent | Người quyết chi phí |
| Quyền vào repo GitHub | Người quản trị repo |
