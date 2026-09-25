# Triển khai trên VPS

Tài liệu này viết cho **đội IT nhận bàn giao**, không phải cho người viết nội dung. Nó trả lời ba
câu: máy chủ cần gì, cài thế nào, và cái gì trong dự án này **không** tự chạy được trên máy chủ.

Các tài liệu còn lại trong `docs/` mô tả *quy tắc nội dung*. Bạn không cần đọc chúng để dựng máy.

---

## 1. Dự án này thật sự là cái gì

Một quy trình sản xuất bài blog SEO cho `muaban.net/blog`, gồm bốn phần rời nhau:

| Phần | Bản chất | Chạy trên VPS được không |
|---|---|---|
| **Bộ kiểm** (`scripts/*.py`) | Python thuần, không cài gói ngoài | Được, không vướng gì |
| **Đồng bộ Lark** (`scripts/lark/`) | Gọi `@larksuite/cli` qua Node.js | Được, nhưng phải đăng nhập — xem mục 6 |
| **Bản nháp WordPress** (`scripts/wp/`) | Gọi REST API bằng application password | Được, cần biến môi trường |
| **Viết nội dung** | **Một agent AI (Claude Code) đọc quy tắc rồi viết** | Xem ngay dưới đây |

**Điều phải nói trước mọi thứ khác: phần viết bài không phải một script.** Không có
`python generate_article.py` trong dự án này và cũng không thể có — nội dung do một agent AI sinh ra
khi đọc `CLAUDE.md` cùng các skill trong `.claude/skills/`. Vì vậy có hai phạm vi triển khai, và bạn
cần biết cấp trên đang hỏi phạm vi nào:

**Phạm vi A — máy chủ làm hạ tầng (dựng trong một buổi).** VPS chạy bộ kiểm, đồng bộ Lark, tạo bản
nháp WordPress, giữ kho dữ liệu và bản lưu. Người viết vẫn mở Claude Code trên máy cá nhân để viết.
Đây là phạm vi **khuyến nghị**, và phần lớn tài liệu này nói về nó.

**Phạm vi B — máy chủ chạy cả agent.** Cài thêm Claude Code CLI trên VPS cùng một tài khoản
Anthropic, rồi người viết làm việc qua SSH. Khả thi, nhưng ba điều không mất đi: hai cổng duyệt vẫn
cần **người thật** bấm trên Lark, chi phí token vẫn tính theo tài khoản Anthropic (khoảng 20–55 triệu
token mỗi bài), và không có lịch cron nào thay được người viết. Mục 8 nói rõ cái gì đặt lịch được.

---

## 2. Yêu cầu máy chủ

Nhẹ. Đây là công cụ xử lý văn bản, không phải dịch vụ web.

| Hạng mục | Mức tối thiểu | Ghi chú |
|---|---|---|
| OS | Ubuntu 22.04 / Debian 12 | Bất kỳ Linux có Python 3.10+ |
| CPU / RAM | 1 vCPU / 1 GB | Bộ kiểm nặng nhất chạy dưới 10 giây |
| Đĩa | 2 GB | Dự án 2,5 MB; chỗ còn lại cho ảnh và bản lưu |
| Python | **3.10 trở lên** | **Không cần `pip install` gì cả** — toàn bộ dùng thư viện chuẩn |
| Node.js | 18 LTS trở lên | Chỉ để chạy `@larksuite/cli` |
| Locale | `C.UTF-8` hoặc `vi_VN.UTF-8` | **Bắt buộc.** Locale POSIX làm script vỡ khi in tiếng Việt |
| Mạng ra | HTTPS tới `larksuite.com`, `muaban.net` | Chiều ra cần 443 |
| Mạng vào | Chỉ port 22 (SSH), mở cho mọi IP | Người vận hành làm việc cả ở nhà. Bù lại: chỉ đăng nhập bằng SSH key, tắt mật khẩu, tắt root, bật `fail2ban` |

Không có cơ sở dữ liệu, không có web server, không có tiến trình thường trú. Mọi trạng thái nằm
trong file dưới thư mục dự án.

---

## 3. Cài đặt

```bash
# 1. Gói hệ thống
sudo apt update
sudo apt install -y python3 python3-venv nodejs npm git locales

# 2. Locale UTF-8 — bỏ bước này là script vỡ giữa đường
sudo locale-gen C.UTF-8 vi_VN.UTF-8
sudo update-locale LANG=C.UTF-8

# 3. Tài khoản chạy riêng, đừng chạy bằng root
sudo useradd -m -s /bin/bash contentseo
sudo su - contentseo

# 4. Giải nén dự án
mkdir -p ~/apps && cd ~/apps
unzip /tmp/content-seo-vps-<ngày>.zip      # ra thư mục content-seo/
cd content-seo

# 5. Lark CLI
sudo npm install -g @larksuite/cli
lark --version

# 6. Kiểm máy — đây là bước xác nhận, không phải bước trang trí
python3 scripts/preflight.py
```

`preflight.py` kiểm 19 mục: phiên bản Python, xử lý UTF-8, quyền ghi, kho dữ liệu đo lường, và chạy
lại bốn fixture hồi quy. Nó phải in **`Du dieu kien chay.`** và thoát mã 0. Mã thoát 1 kèm danh sách
mục phải sửa.

Thêm vào `~/.bashrc` của tài khoản đó:

```bash
export LANG=C.UTF-8
export PYTHONIOENCODING=utf-8
```

---

## 4. Bí mật và biến môi trường

**Trong gói bàn giao không có mật khẩu, token hay key nào.** Đó là chủ ý, và xin giữ nguyên như vậy.

Sao `.env.example` thành `.env`, điền giá trị, rồi `chmod 600 .env`. File `.env` đã nằm trong
`.gitignore`.

| Biến | Dùng cho | Lấy ở đâu |
|---|---|---|
| `MBWP_USER` | Đăng nhập WordPress | Tên đăng nhập của biên tập viên |
| `MBWP_APP_PASSWORD` | Đăng nhập WordPress | WP Admin → Users → Profile → **Application Passwords**. Đây **không** phải mật khẩu đăng nhập |
| `LARK_NODE` | Tùy chọn | Đường dẫn `node` nếu không nằm trong `PATH` |
| `LARK_CLI_ENTRY` | Tùy chọn | Đường dẫn `.../@larksuite/cli/scripts/run.js` nếu tự dò không ra |

`wp_draft.py` tìm thông tin đăng nhập WordPress theo **đúng ba nguồn, theo thứ tự này**:

1. Biến môi trường `MBWP_USER` + `MBWP_APP_PASSWORD` — dùng cho cron và CI, nơi không nên có file
2. File `.env` ở gốc dự án — dùng cho máy người thật, tiện nhất
3. File `~/.muaban-wp.json` với `chmod 600`:

```json
{ "site": "https://muaban.net/blog", "user": "<tên đăng nhập>", "app_password": "<app password>" }
```

Nguồn nào có trước thì thắng. `.env` **không** được nạp vào `os.environ`, nên mật khẩu không lan sang
tiến trình con — và `wp_draft.py` có gọi `run_qa.py` cùng `lark_sync.py` bằng subprocess.

Ba điều về application password, xin đọc hết: nó **bỏ qua xác thực hai lớp**, nó **thu hồi độc lập**
với mật khẩu chính (thu hồi một cái không ảnh hưởng cái kia), và nó chỉ hiện **một lần** lúc tạo.
Cấp một cái **riêng cho máy chủ** thay vì dùng lại cái của người khác — để khi cần chặn máy chủ thì
thu hồi đúng một dòng. Và đổi ngay bất kỳ application password nào đã từng bị dán vào chat, ảnh chụp
màn hình hay email.

Hồ sơ đăng nhập của Lark CLI nằm ở `~/.lark-cli/`, và **file `~/.lark-cli/config.json` chứa
`appSecret` cùng token người dùng**. Coi cả thư mục đó như bí mật: không đưa vào git, không nén vào
bản lưu dùng chung, không sao chép qua kênh không mã hóa.

---

## 5. Cấu hình Lark Base

`scripts/lark/config.json` trỏ tới Base **đang chạy thật** của đội nội dung: `app_token`, id bốn
bảng, id thư mục Drive, id nhóm chat báo tin. Không có secret trong file này, chỉ là các định danh.

**Chọn một trong hai:**

*Dùng chung Base đang chạy* — giữ nguyên `config.json`. Máy chủ sẽ đọc và ghi vào đúng các bản ghi
người thật đang duyệt. Đây là điều mong muốn nếu máy chủ tiếp tục công việc đang dở.

*Dựng Base riêng để thử* — sao `config.example.json` thành `config.json` rồi chạy:

```bash
python3 scripts/lark/lark_setup.py --title "Content SEO — thử nghiệm"
python3 scripts/lark/lark_setup.py --verify      # phải thoát 0, không còn dòng [COT]/[OPTION]
```

Lệnh này tự tạo Base, bốn bảng, mọi cột và mọi trạng thái. **Đừng sửa tên cột bằng tay trên Base** —
sửa `scripts/lark/schema.py` rồi chạy `lark_setup.py --rebuild`, vì code dùng khóa nội bộ ASCII còn
Base hiển thị tiếng Việt.

Một cảnh báo đã trả giá: `--rebuild` từng **xóa mất giá trị** ô Trạng thái của một bản ghi đang chạy,
vì nó gửi lại danh sách lựa chọn mà không kèm `id` của các lựa chọn cũ nên Lark coi chúng là mới. Lỗi
đã sửa, nhưng nguyên tắc còn đó: **chụp lại Base trước khi `--rebuild` trên dữ liệu thật.**

---

## 6. Đăng nhập Lark trên máy không có màn hình

Đây là chỗ khó duy nhất của cả việc triển khai, nên đọc kỹ.

`@larksuite/cli` xác thực bằng **OAuth qua trình duyệt**: nó mở một URL và chờ callback về
`localhost`. VPS không có trình duyệt, nên `lark auth login` chạy trần sẽ treo.

**Cách 1 — chuyển tiếp cổng qua SSH (khuyến nghị).** Đăng nhập từ máy có trình duyệt, tunnel cổng
callback về máy đó:

```bash
# tren may ca nhan
ssh -L 3000:localhost:3000 contentseo@<ip-vps>
# trong phien ssh do
lark auth login          # mo URL no in ra, bang trinh duyet cua may ca nhan
```

Cổng callback thực tế do CLI quyết định — đọc URL nó in ra, nếu không phải 3000 thì mở lại tunnel
đúng cổng đó. Đăng nhập một lần, hồ sơ nằm lại ở `~/.lark-cli/`, và CLI tự làm mới token.

**Cách 2 — sao chép hồ sơ đã đăng nhập.** Chép `~/.lark-cli/` từ máy đã login sang VPS. Nhanh, nhưng
đang bê `appSecret` và token người dùng qua mạng: chỉ dùng `scp`, đặt `chmod 700`, và hiểu rằng
máy chủ từ đó hành động **dưới danh nghĩa người đã đăng nhập** — mọi dòng Nhật ký trên Base sẽ ghi
tên người đó.

**Cách 3 — chuyển sang Lark custom app (`app_id` + `app_secret`).** Đây là cách đúng cho một máy chủ
không người trực, vì token cấp theo ứng dụng chứ không theo người. Nhưng nó **cần sửa code**:
`scripts/lark/lark_cli.py` hiện gọi CLI qua `subprocess`, phải viết lại thành gọi REST API
`open.larksuite.com` kèm `tenant_access_token`. Khoảng một ngày công cho một người biết việc, cộng
thời gian xin cấp scope cho app. Ba việc phải giữ nguyên khi làm: mọi lệnh Lark vẫn đi qua một chỗ
duy nhất, `gate` vẫn là hàm quyết định cổng đã mở, và agent vẫn **không bao giờ** được ghi "Đồng ý"
vào ô Kết quả duyệt.

Kiểm bằng:

```bash
python3 scripts/preflight.py --lark
python3 scripts/lark/lark_sync.py status
```

---

## 7. Chạy hằng ngày

```bash
cd ~/apps/content-seo

# Doc trang thai — an toan, khong sua gi
python3 scripts/lark/lark_sync.py status
python3 scripts/lark/lark_watch.py --todo        # ma thoat 3 = dang co viec cho

# Keo tu khoa moi da tich cong tac tu Base xuong may
python3 scripts/lark/lark_sync.py intake

# Kiem mot bai
python3 scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json
python3 scripts/house_voice_check.py work/<slug>/article.md
python3 scripts/wiki_lint.py

# Day goi ban giao len Base cho nguoi that duyet
python3 scripts/lark/lark_sync.py push work/<slug>

# Sau khi cong duyet bai da mo: tao BAN NHAP tren WordPress
python3 scripts/wp/wp_draft.py work/<slug> --dry-run
python3 scripts/wp/wp_draft.py work/<slug>
```

Mã thoát theo quy ước quen thuộc: `0` là đạt, `1` là còn lỗi chặn, `2` là sai cách gọi, `3` ở
`lark_watch --todo` nghĩa là đang có việc chờ.

**`wp_draft.py` chỉ tạo bản nháp.** Chuỗi `"status": "draft"` cố định trong code, không có cờ dòng
lệnh nào đổi được, và script tự dừng nếu bài trên WordPress đã ở trạng thái `publish`. Nó cũng tự
kiểm ba điều trước khi gửi: QA chạy lại tại chỗ phải `PASS`, `lark_sync.py gate` phải thoát 0, và
mọi ảnh phải `CLEARED` trong `image-manifest.csv`. **Bấm Publish là việc của người thật** — xin đừng
"tự động hóa nốt bước cuối", đó là ràng buộc nghiệp vụ chứ không phải việc còn sót.

---

## 8. Đặt lịch bằng cron: cái gì được, cái gì không

Đặt lịch được, vì chỉ đọc hoặc chỉ kiểm:

```cron
# Sức khỏe kho tri thức, 6h sáng mỗi ngày
0 6 * * * cd /home/contentseo/apps/content-seo && LANG=C.UTF-8 python3 scripts/wiki_lint.py >> logs/wiki-lint.log 2>&1

# Bản lưu, 1h sáng
0 1 * * * tar -czf /home/contentseo/backup/content-seo-$(date +\%F).tar.gz -C /home/contentseo/apps content-seo
```

**Không đặt lịch được** — nói rõ để không ai mất một tuần thử:

- **Viết bài.** Cần agent AI, không phải script.
- **`lark_watch.py` chạy nền một mình.** Nó chỉ *báo* cổng duyệt đã đổi. Không có phiên Claude Code
  nào mở thì tin báo không ai đọc, và bước sau khi duyệt là viết nội dung.
- **`wp_draft.py` theo lịch.** Nó ghi ra blog thật. Để người thật gọi, sau khi đọc bài.
- **`lark_setup.py --rebuild` theo lịch.** Đây là lệnh sửa cấu trúc Base, không phải lệnh bảo trì.

---

## 9. Sao lưu

Bốn thứ mất là làm lại rất tốn, theo thứ tự quan trọng:

| Đường dẫn | Là gì | Mất thì sao |
|---|---|---|
| `work/` | Gói bàn giao từng bài: brief, outline, bài, ledger, QA | Mất toàn bộ bài đang dở |
| `wiki/` | Kho tri thức: claim đã xác minh kèm nguồn và ngày | Bài sau phải đi tra nguồn lại từ đầu |
| `reference/` | 24 bài thật + 1.217 URL internal link | **Mọi ngưỡng đo lường sinh ra từ đây.** Mất là bộ kiểm giọng văn hết cơ sở |
| `scripts/lark/config.json` | Định danh Base và các bảng | Phải dò lại id, hoặc dựng Base mới |

`tar -czf` cả thư mục dự án là đủ; nó chỉ 2,5 MB cộng phần ảnh. Base trên Lark là dữ liệu của
Larksuite, sao lưu theo cơ chế của họ.

---

## 10. Bốn điều xin đừng làm

Bốn điều này không phải ý kiến kỹ thuật, chúng là ràng buộc nghiệp vụ đã được trả giá bằng bài bị
từ chối ở cổng duyệt:

1. **Đừng tự động hóa bước Publish.** Bản nháp là điểm dừng cuối của máy.
2. **Đừng để script nào ghi "Đồng ý" vào ô Kết quả duyệt.** Chỉ người thật duyệt được; agent chỉ được
   **xóa trắng** cụm duyệt khi nội dung đổi.
3. **Đừng nới ngưỡng trong `scripts/lexicon/` để bài qua cửa.** Các con số ở đó đo từ 24 bài thật.
   Muốn đổi thì thêm bài thật vào `reference/muaban-blog/` rồi chạy lại
   `python3 scripts/house_voice_profile.py`, đừng sửa tay file JSON.
4. **Đừng commit `.env`, `~/.muaban-wp.json` hay `~/.lark-cli/` vào bất kỳ repo nào.**

---

## 11. Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Xử lý |
|---|---|---|
| `UnicodeEncodeError` giữa một lần chạy | Locale không phải UTF-8 | `export LANG=C.UTF-8 PYTHONIOENCODING=utf-8` |
| `Khong tim thay node` | Node không trong `PATH` | `export LARK_NODE=$(which node)` |
| `Khong tim thay @larksuite/cli` | Cài cục bộ thay vì toàn cục | `npm i -g @larksuite/cli`, hoặc đặt `LARK_CLI_ENTRY` |
| Lệnh Lark báo `missing_scope` | App thiếu quyền Base | Cấp scope Bitable cho app rồi đăng nhập lại |
| Lệnh Lark báo `unauthorized` | Hồ sơ hết hiệu lực | `lark auth login` lại theo mục 6 |
| `wp_draft` báo 401 | Sai application password, hoặc đang dùng mật khẩu đăng nhập | Tạo application password mới |
| `wp_draft` dừng và báo bài đã `publish` | Đúng như thiết kế | Người thật sửa trực tiếp bài đang đăng |
| `gate` thoát khác 0 | Người duyệt chưa bấm, hoặc nội dung đã đổi sau khi duyệt | Đọc ô Góp ý trên Base |
| `run_qa` thoát 1 trên bài cũ | Ngưỡng đã đổi sau khi kho bài thật được cập nhật | Đọc `BLOCK` cụ thể, đừng nới ngưỡng |

---

## 12. Bàn giao cần ai cấp gì

Trước khi máy chủ chạy được đủ, bốn thứ sau phải xin từ bốn chỗ khác nhau:

| Cần | Xin ai | Ghi chú |
|---|---|---|
| Quyền vào Lark Base + scope Bitable cho app | Quản trị Larksuite | Thiếu là mọi lệnh Lark báo `missing_scope` |
| Application password WordPress **riêng cho máy chủ** | Quản trị `muaban.net/blog` | Cấp cho một tài khoản có quyền tạo bản nháp |
| Tài khoản Anthropic + cài Claude Code | Người quyết chi phí | **Chỉ cần cho phạm vi B**, xem mục 1 |
| Quyết định dùng chung Base hay dựng Base riêng | Trưởng nhóm nội dung | Xem mục 5 |

---

## 13. Trong gói có gì, và cái gì đã bị cố ý bỏ ra

137 file, 542 KB. Bốn thứ **đã bị loại khỏi gói** vì chúng là trạng thái riêng của máy cũ, không phải
mã nguồn:

| Đã loại | Vì sao | Tự sinh lại thế nào |
|---|---|---|
| `work/*/.lark.json` | Trỏ tới đúng bản ghi trên Base của máy cũ. Giữ lại thì máy chủ có thể ghi đè lên bản ghi người thật đang duyệt | `lark_sync.py intake` tạo mới cho bài mới |
| `work/*/.wp.json` | Id bản nháp WordPress đã tạo từ máy cũ | `wp_draft.py` tạo lại khi cần |
| `work/*/qa-report.json` và `examples/*/qa-report.json` | Kết quả máy kiểm, có nhúng đường dẫn tuyệt đối của máy cũ | `run_qa.py --json` sinh lại |
| `__pycache__/`, `*.pyc` | Bytecode biên dịch cho Python của máy cũ | Python tự sinh |

Hai thư mục trong `work/` **được giữ lại làm mẫu tham chiếu**: một bài bất động sản
(`kinh-nghiem-thue-tro-gan-truong-dai-hoc-kinh-te-tp-hcm`) và một bài điềm báo
(`chuon-chuon-bay-vao-nha`). Mỗi thư mục có bảy file, hữu ích khi cần biết đầu ra đúng trông như thế
nào. **Cả hai đều còn thiếu ảnh**, nên không có `image-manifest.csv` — đó là việc còn dở của đội nội
dung, không phải file bị loại khỏi gói; mẫu manifest nằm ở `templates/image-manifest.csv`. Cả hai bài
cũng đang dở giữa quy trình trên Base cũ, nên **đừng dùng chúng để thử `push`** — hãy `intake` một
từ khóa mới.

Trong gói **không có** mật khẩu, token hay key nào. Đã rà soát tự động: mọi chỗ khớp mẫu
`app_password` / `app_secret` trong gói đều là tên trường hoặc chuỗi ví dụ trong tài liệu.
