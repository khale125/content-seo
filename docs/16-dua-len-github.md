# Đưa dự án lên GitHub và cài trên máy khác

Tài liệu này viết cho **người quản trị repo** và cho **thành viên mới của team** cài dự án về máy.
Phần triển khai máy chủ nằm ở `docs/15-trien-khai-vps.md`; hai tài liệu không trùng nhau.

---

## 1. Repo này phải là **private**

Không phải để giữ bí mật code — code không có gì bí mật. Ba thứ dữ liệu bên trong mới là lý do:

| Trong repo | Là gì | Công khai thì sao |
|---|---|---|
| `scripts/lark/config.json` | Tên miền Larksuite của công ty, `app_token` của Base, id bốn bảng, token thư mục Drive, id nhóm chat duyệt | Người ngoài biết đường vào hạ tầng nội bộ và cấu trúc vận hành của team |
| `reference/internal-links-mbn.csv` | 2.137 dòng bản đồ từ khoá → URL, lấy từ sheet nội bộ | Đối thủ đọc được toàn bộ chiến lược internal link |
| `reference/muaban-blog/` | 24 bài nguyên văn của blog công ty | Phát hành lại nội dung có bản quyền của công ty |

Vì vậy khi tạo repo, chọn **Private**. Nếu về sau có ai muốn mở công khai, phải tách ba thứ trên ra
trước — đừng đổi visibility rồi mới xử lý, vì GitHub có fork, có cache và có bản lưu của bên thứ ba,
và một lần công khai là không rút lại được.

`.gitignore` đã chặn sẵn `.env`, `.muaban-wp.json`, `*.pem`, `*.key`. **Mật khẩu và token không bao
giờ được commit**, kể cả trong repo private: repo private vẫn bị sao chép khi ai đó clone, vẫn nằm
trong bản lưu, và quyền truy cập repo sẽ thay đổi theo thời gian.

---

## 2. Đưa lên GitHub

Thư mục đã là một git repo và đã có commit đầu tiên. Việc còn lại là tạo repo trên GitHub rồi đẩy lên.

**Cách A — dùng `gh` CLI (gọn nhất).** Nếu chưa có: `winget install GitHub.cli` trên Windows, hoặc
`sudo apt install gh` trên Ubuntu.

```bash
gh auth login
cd "D:/Claude code/SEO/content-seo"
gh repo create content-seo --private --source=. --remote=origin --push
```

**Cách B — tạo trên web rồi nối remote.** Vào <https://github.com/new>, đặt tên `content-seo`, chọn
**Private**, **không** tích "Add a README" hay "Add .gitignore" (repo đã có sẵn cả hai, tích vào sẽ
sinh xung đột), rồi:

```bash
cd "D:/Claude code/SEO/content-seo"
git remote add origin https://github.com/<tên-của-bạn>/content-seo.git
git branch -M main
git push -u origin main
```

Đẩy lên xong, kiểm hai điều ngay trên GitHub: repo hiện nhãn **Private**, và mở
`Settings → Collaborators` để thêm đúng người cần.

---

## 3. Cài trên một máy mới

Thành viên team làm ba bước. Không có `pip install` nào — bộ kiểm chỉ dùng thư viện chuẩn Python.

```bash
# 1. Lay ma nguon
git clone https://github.com/<tên-của-bạn>/content-seo.git
cd content-seo

# 2. Cai dat (kiem may + dung .env + chay hoi quy)
bash install.sh                                           # Linux / macOS
powershell -ExecutionPolicy Bypass -File install.ps1      # Windows
```

`install.sh` phải in **`Du dieu kien chay.`** và thoát mã 0. Nó chạy `scripts/preflight.py`: 19 mục
kiểm cộng bốn fixture hồi quy. Mã thoát 1 kèm danh sách mục phải sửa.

```bash
# 3. Hai thong tin dang nhap
#    a) WordPress — dien vao .env vua duoc tao
#       MBWP_USER, MBWP_APP_PASSWORD  (WP Admin -> Users -> Profile -> Application Passwords)
#    b) Lark
npm install -g @larksuite/cli
lark auth login

python3 scripts/preflight.py --all      # phai 23/23
```

`wp_draft.py` đọc `.env` ở gốc dự án, nên điền vào đó là đủ — không cần `export` gì thêm. Thứ tự ưu
tiên là biến môi trường, rồi `.env`, rồi `~/.muaban-wp.json`; nguồn nào có trước thì thắng.

Rồi mở **Claude Code** ngay trong thư mục đó. Agent đọc `CLAUDE.md` và các skill trong
`.claude/skills/` là bắt đầu làm việc được.

### Yêu cầu máy

| Cần | Mức | Ghi chú |
|---|---|---|
| Python | **3.10+** | Không cần cài gói ngoài |
| Node.js | 18+ | Chỉ để chạy `@larksuite/cli` |
| Claude Code | Bản hiện tại | Phần viết bài do agent làm, không phải script |
| Locale | UTF-8 | Trên Linux: `export LANG=C.UTF-8 PYTHONIOENCODING=utf-8` |

### Ba thứ phải xin trước khi chạy được đủ

| Cần | Xin ai |
|---|---|
| Quyền vào repo GitHub | Người quản trị repo |
| Quyền vào Lark Base + scope Bitable | Quản trị Larksuite |
| Application password WordPress **riêng cho từng người** | Quản trị `muaban.net/blog` |

Cấp application password **riêng cho mỗi người**, đừng dùng chung một cái: khi cần chặn một máy thì
thu hồi đúng một dòng, và Nhật ký trên WordPress mới truy được ai tạo bản nháp nào.

---

## 4. Làm việc chung trên một Base

Cả team dùng **một** Lark Base, nên hai file trạng thái dưới `work/<slug>/` **được commit có chủ ý**,
khác với thói quen thường thấy là bỏ hết file trạng thái ra ngoài:

| File | Vì sao phải commit |
|---|---|
| `.lark.json` | Buộc thư mục với đúng bản ghi trên Base. Thiếu nó, đồng nghiệp clone repo về **không** `push`, `pull` hay `gate` được bài đã có — các lệnh đó đòi file này tồn tại |
| `.wp.json` | Buộc bài với đúng bản nháp trên WordPress. Thiếu nó, lần chạy sau tạo một bản nháp **trùng** thay vì cập nhật bản nháp cũ |

Cái giá phải trả: hai người cùng sửa một bài sẽ chạm nhau ở `content_version` và `content_hash`. Khi
git báo conflict ở `.lark.json`, **lấy bản có `content_version` cao hơn** rồi chạy lại
`python3 scripts/lark/lark_sync.py push work/<slug>`. Cách tránh: một bài do một người giữ tới khi
qua cổng duyệt.

Ngược lại, bốn thứ này **không** commit vì là trạng thái riêng của từng máy hoặc do máy tự sinh:
`work/.lark-watch.json` (mốc của kênh theo dõi), `work/*/qa-report.json` và `wiki/lint-report.json`
(chạy lại là có), `.env` (bí mật).

`.gitattributes` đặt `eol=lf` cho toàn repo và `crlf` cho `*.ps1`. Đừng bỏ file đó đi: team chạy cả
Windows lẫn Linux, và không có nó thì mỗi lần checkout chéo hệ điều hành cả repo hiện ra như đã sửa
hết, diff thành vô dụng.

---

## 5. Bốn quy tắc không đổi khi lên GitHub

Chúng là ràng buộc nghiệp vụ, không phải lựa chọn kỹ thuật, và đều đã được trả giá bằng bài bị từ
chối ở cổng duyệt:

1. **Không CI/CD nào được publish bài.** `wp_draft.py` gửi `status: draft` cố định. Đừng viết
   GitHub Action gọi nó — nó ghi ra blog thật, và bấm Publish là việc của người thật.
2. **Không script nào ghi "Đồng ý" vào ô Kết quả duyệt.** Chỉ người thật duyệt được.
3. **Không nới ngưỡng trong `scripts/lexicon/` để bài qua cửa.** Muốn đổi thì thêm bài thật vào
   `reference/muaban-blog/` rồi chạy lại `python3 scripts/house_voice_profile.py`.
4. **Không commit `.env`, `~/.muaban-wp.json` hay `~/.lark-cli/`.** Thư mục `~/.lark-cli/` chứa
   `appSecret` và token người dùng; nó nằm ngoài repo và phải ở ngoài.

---

## 6. Vì sao đây không phải một Claude Code plugin

Câu hỏi hợp lý, vì các bộ skill SEO phổ biến (ví dụ `claude-seo`) cài bằng
`/plugin marketplace add <owner>/<repo>` và không cần clone gì.

Khác nhau ở chỗ **dữ liệu sống ở đâu**. Một plugin chỉ mang skill: nó chạy trên website bên ngoài và
không lưu gì lại. Dự án này thì ngược lại — nó **là nơi làm việc**, và bốn thứ phải nằm trong thư mục
dự án mới hoạt động:

- `work/<slug>/` — gói bàn giao từng bài, nơi mọi lệnh đọc và ghi
- `wiki/` — kho tri thức dùng lại giữa các bài
- `reference/` — 24 bài thật cùng kho URL, **mọi ngưỡng đo lường sinh ra từ đây**
- `scripts/lark/config.json` — Base nào, bảng nào

Cài dạng plugin thì skill nằm ở `~/.claude/plugins/` còn bốn thứ trên không có chỗ nào để sống, và
`lark_sync.py` sẽ không biết ghi `work/` vào đâu. Vì vậy cách cài đúng là **clone repo rồi mở Claude
Code trong chính thư mục đó** — đúng ba bước ở mục 3.

Nếu về sau muốn dạng plugin thật, việc phải làm là tách đôi: skill và bộ kiểm thành plugin, còn
`work/`, `wiki/`, `reference/` và `config.json` thành một "thư mục dữ liệu" trỏ tới bằng biến môi
trường. Đó là một lần refactor thật sự, không phải thêm một file manifest.
