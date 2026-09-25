# Content SEO — Bất động sản

> **Repo nội bộ Muaban.net — để ở chế độ Private.** Trong repo có `app_token` của Lark Base, kho
> 2.137 URL internal link lấy từ sheet nội bộ, và 24 bài nguyên văn của blog. Muốn mở công khai thì
> phải tách ba thứ đó ra **trước**, vì một lần công khai là không rút lại được. Chi tiết và cách cài
> trên máy mới: [`docs/16-dua-len-github.md`](docs/16-dua-len-github.md).

Công cụ AI để nghiên cứu intent, lên outline và viết bài chuẩn SEO cho chủ đề bất động sản Việt Nam
(blog Muaban.net), với ba ràng buộc cứng:

1. **Không bịa đặt** — mọi con số, ngày, tên văn bản trong bài phải truy được về một nguồn thật.
2. **Giọng văn người thật** — không sáo ngữ, không nhịp đều tăm tắp, có lập trường và có giới hạn.
3. **Không rơi vào nhóm nội dung Google coi là spam quy mô lớn** — mỗi URL phải có lý do tồn tại
   riêng, không phải biến thể từ khóa của bài khác.

Ba ràng buộc này thực chất là một: nội dung cụ thể, có nguồn, giải quyết xong việc của người đọc
thì vừa đọc tự nhiên, vừa không nằm trong diện bị chính sách spam nhắm tới.

## Cấu trúc

```
content-seo/
├── CLAUDE.md               Hard rules — đọc đầu tiên
├── docs/                   Tiêu chuẩn biên tập (00 → 14) + triển khai máy chủ (15)
├── .claude/skills/         5 skill cho Claude Code
├── scripts/                Bộ kiểm tự động (Python 3.10+, không cần cài gói ngoài)
│   ├── preflight.py        Kiểm máy trước khi chạy — chạy đầu tiên trên máy mới
│   ├── wp/                 Tạo bản nháp trên WordPress (không bao giờ publish)
│   ├── lark/               Đồng bộ hai chiều với Lark Base
│   └── radar/              Phát hiện chủ đề từ nguồn chính thống
├── templates/              Mẫu brief, outline, ledger, bài, QA, bàn giao, trang wiki
├── examples/               Fixture kiểm thử bộ kiểm
├── wiki/                   Kho tri thức dùng lại giữa các bài (không có cổng duyệt)
└── work/<slug>/            Nơi làm việc cho từng bài
```

## Quy trình

```
bạn đưa từ khóa + volume → intent + SERP gap → evidence ledger → outline
       → [cổng outline] → draft → QA → [cổng bài] → bàn giao
```

Hai cổng duyệt nằm trên **Lark Base**. Agent đẩy artifact lên, bạn duyệt trên đó, agent đọc ngược
trạng thái để biết được phép đi tiếp hay chưa.

Bốn skill tương ứng bốn giai đoạn:

| Skill | Làm gì | Dừng ở đâu |
|---|---|---|
| `seo-radar-bds` *(tùy chọn, ngoài quy trình chính)* | Quét văn bản pháp luật, Bộ Xây dựng, Ngân hàng Nhà nước, Cục Thống kê; tìm bài cũ đã lỗi thời; trình gợi ý kèm nguồn đã xác minh | — không đẩy lên Lark |
| `seo-outline-bds` | Phân loại intent, đọc SERP tìm khoảng trống, gom cụm từ khóa, chống trùng nội dung, dựng evidence ledger, viết outline, đẩy lên Lark | `OUTLINE_PENDING` — chờ duyệt trên Lark |
| `seo-writer-bds` | Viết bài sau khi cổng outline mở, sáu lượt tự sửa, điền SEO fields và link map | `ARTICLE_PENDING` — chờ duyệt trên Lark |
| `seo-qa-bds` | Chạy máy kiểm, đối chiếu bằng chứng thủ công, kiểm rủi ro chính sách, đóng gói bàn giao | `DONE` — đã duyệt, chờ bàn giao |

Outline phải có người thật duyệt trước khi viết. Sửa outline rẻ hơn sửa bài.

Ngoài bốn skill của quy trình còn có `humanizer-bds`: **viết lại** đoạn nghe như máy. `human_voice_check.py` chỉ báo lỗi, skill này mới là phương pháp sửa. Thích ứng từ [blader/humanizer](https://github.com/blader/humanizer) (MIT), đã khoá lại hai pattern đánh nhau với yêu cầu YMYL — mọi câu nêu phạm vi, mốc dữ liệu, giới hạn và khuyến nghị tham vấn đều giữ nguyên.

## Cài đặt

Ba bước trên một máy mới. **Không cần `pip install` gì cả** — bộ kiểm chỉ dùng thư viện chuẩn Python.

```bash
git clone https://github.com/<tên-của-bạn>/content-seo.git
cd content-seo

bash install.sh                                        # Linux / macOS
powershell -ExecutionPolicy Bypass -File install.ps1   # Windows
```

`install.sh` kiểm máy, tạo `.env` từ bản mẫu, rồi chạy `scripts/preflight.py` — 19 mục kiểm cộng bốn
fixture hồi quy. Phải in `Du dieu kien chay.` và thoát mã 0.

Còn hai thông tin đăng nhập phải tự điền: `MBWP_USER` + `MBWP_APP_PASSWORD` vào `.env`, và
`npm i -g @larksuite/cli` rồi `lark auth login`. Kiểm lại bằng
`python scripts/preflight.py --all` (phải 23/23). Yêu cầu máy, phân quyền và cách làm việc chung trên
một Base: [`docs/16-dua-len-github.md`](docs/16-dua-len-github.md). Dựng trên VPS Linux không màn
hình: [`docs/15-trien-khai-vps.md`](docs/15-trien-khai-vps.md).

Xong thì mở **Claude Code** ngay trong thư mục này.

## Bắt đầu

Cách 1 — để radar tự tìm chủ đề:

```
/seo-radar-bds
```

Radar quét nguồn chính thống, đối chiếu với nội dung đã có trên blog, rồi đẩy các ứng viên lên Lark
dưới dạng danh sách gợi ý. Bạn chọn từ khóa nào thì đưa kèm volume để viết cái đó.

Cách 2 — bạn tự đưa chủ đề:

```
/seo-outline-bds thủ tục sang tên sổ đỏ
```

Skill đẩy brief, evidence ledger và outline lên Lark rồi dừng. Bạn duyệt trên Lark bằng cách điền
**hai ô**: `Kết quả duyệt = Đồng ý` và `Người duyệt = tên bạn`.

Sau đó:

```
/seo-writer-bds work/thu-tuc-sang-ten-so-do
/seo-qa-bds     work/thu-tuc-sang-ten-so-do
```

## Radar phát hiện chủ đề

```powershell
python scripts/radar/radar.py sources                              # danh mục nguồn đã xác minh
python scripts/radar/radar.py check --url "<url>" --event "<mô tả>"  # đã đề xuất chưa
python scripts/radar/radar.py add <file.json>                      # ghi nhận + dựng work/<slug>/
python scripts/radar/radar.py list                                 # lịch sử đề xuất
python scripts/radar/radar.py close <slug> VIET|BO_QUA|GOP         # ghi kết cục
```

Nguồn đã xác minh: `vanban.chinhphu.vn` (văn bản pháp luật), `moc.gov.vn` (Bộ Xây dựng, công bố quý
về nhà ở và thị trường), `sbv.gov.vn` (lãi suất, tín dụng), `nso.gov.vn` (CPI). Báo chí chỉ là tín
hiệu, bắt buộc truy ngược về văn bản gốc.

`add` **từ chối** ứng viên thiếu nguồn HTTPS, thiếu ngày công bố, ngày ở tương lai, hoặc nguồn báo
chí chưa ghi văn bản gốc cần truy. Chốt chặn nằm trong script, không nằm trong hướng dẫn.

Giá trị lớn nhất của radar không phải tìm bài mới, mà là tìm **bài cũ đang dẫn quy định đã hết hiệu
lực** — vừa là rủi ro YMYL vừa là cơ hội `UPDATE` rẻ hơn `CREATE`. Chi tiết: `docs/09-phat-hien-chu-de.md`.

## Đồng bộ Lark

Base: xem `base_url` trong `scripts/lark/config.json`.

```powershell
python scripts/lark/lark_sync.py push   work/<slug>     # đẩy artifact lên
python scripts/lark/lark_sync.py gate   work/<slug>     # cổng hiện tại mở chưa (exit 0 = mở)
python scripts/lark/lark_sync.py pull   work/<slug>     # đọc trạng thái duyệt về
python scripts/lark/lark_sync.py status                 # xem toàn bộ pipeline
python scripts/lark/lark_sync.py remove work/<slug>     # gỡ một bản ghi
```

Toàn bộ Base bằng tiếng Việt. Bốn bảng: **Điều phối** (17 trường, một bản ghi mỗi bài),
**Bằng chứng** (một bản ghi mỗi claim), **Nhật ký**, **Hướng dẫn**. Điều phối và Bằng chứng
nối nhau bằng trường liên kết hai chiều, và có sẵn view **Đang chờ tôi duyệt** đã lọc trước.

Bạn chỉ nhìn cột **Trạng thái** + **Việc kế tiếp**, và điền **hai ô**: `Kết quả duyệt = Đồng ý`
và `Người duyệt`. Từ chối thì thêm `Góp ý`. Ba ô đó tô vàng; phần còn lại do agent quản lý.

Cả hai cổng (outline / bài) dùng chung một cụm duyệt, vì một bản ghi tại một thời điểm
chỉ đứng ở đúng một cổng — cột Trạng thái cho biết bạn đang duyệt cái gì.

**Phê duyệt cũ không bao giờ được tái sử dụng:** agent xóa trắng cụm duyệt khi nội dung đổi
(checksum outline + bài + ledger) hoặc khi phê duyệt vừa được dùng để qua một cổng.
Agent chỉ được *xóa trắng*, không bao giờ được ghi "Đồng ý". Chi tiết: `docs/08-dong-bo-lark.md`.

Nhãn hiển thị nằm trọn trong `scripts/lark/schema.py`; code làm việc bằng khóa ASCII nội bộ nên
đổi cách gọi cột không đụng tới logic.

Không có secret nào nằm trong project; `@larksuite/cli` tự giữ phiên đăng nhập.

## Wiki tri thức

`evidence-ledger.csv` sống và chết trong một thư mục `work/<slug>/`: bài sau không thừa hưởng được
gì từ bài trước. `wiki/` sửa chỗ đó — một kho markdown mà agent dựng và bảo trì, nằm giữa nguồn gốc
và bài viết, giàu lên sau mỗi bài.

```powershell
python scripts/wiki_lint.py                 # rà soát sức khỏe kho tri thức
python scripts/wiki_index.py build          # dựng lại wiki/index.md
python scripts/wiki_index.py check          # mục lục còn khớp không
```

**Luật số 1: wiki không phải nguồn.** Bài viết luôn trích dẫn `source_url` gốc, không bao giờ trích
dẫn trang wiki. Mỗi claim trên wiki bắt buộc mang theo `source_url` HTTPS, trích dẫn nguyên văn và
`retrieved_date`. Để agent trích dẫn wiki là biến zero-fabrication thành fabrication có vẻ ngoài
đáng tin — tệ hơn hẳn việc không có wiki.

Giá trị lớn nhất không phải tốc độ, mà là trường `used_in`: nó trả lời thẳng câu hỏi *"văn bản này
vừa hết hiệu lực, những bài nào đang dẫn nó?"* Trước đây phải rà bằng mắt; giờ `wiki_lint.py` chặn
ở mức `BLOCK`, kể cả khi `wiki_ref` nằm trong ledger của một bài khác.

Dự án **không lưu bản chụp nguồn** — chỉ URL, trích dẫn nguyên văn và ngày lấy về. Wiki **không**
đi qua Lark và **không** thay thế `evidence-ledger.csv`; nó chỉ làm việc điền ledger nhanh hơn và
nhất quán hơn. Quy ước đầy đủ: `docs/11-wiki-tri-thuc.md` và `wiki/schema.md`.
Ý tưởng gốc: [LLM Wiki của Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Bộ kiểm tự động

```powershell
python scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json
```

Script tự tìm `evidence-ledger.csv` và `brief.yaml` cùng thư mục; SEO fields đọc từ front matter
của `article.md`. Mã thoát: `0` = PASS, `1` = còn BLOCK, `2` = lỗi chạy.

| Script | Kiểm gì |
|---|---|
| `serp_outline.py` | **Tổng hợp từ top 5**: gom heading của top 5 thành chủ đề; chặn khi outline thiếu chủ đề họ có mà không khai báo lý do; chặn khi không có điểm khác biệt; chặn khi heading trùng câu chữ của họ |
| `outline_check.py` | **Trọng tâm outline**: một mục nhận câu hỏi chính và đứng đầu, không nhồi truy vấn vào nhiều mục, mọi câu hỏi trong brief có mục nhận, mỗi mục khai báo `source_ids`, không có mục "Kết luận" |
| `human_voice_check.py` | Sáo ngữ, câu hứa hẹn, viện dẫn mơ hồ, dấu vết sinh tự động; burstiness độ dài câu và đoạn; độ đều của danh sách; mật độ số liệu; mức độ có lập trường; định dạng. Từ bản thích ứng Humanizer: tương phản rỗng, câu nghe sâu sắc, cãi với người không có mặt, né động từ "là", rào trước rồi đoán, liên hệ mơ hồ, câu chốt lặp, danh sách nhãn in đậm |
| `onpage_check.py` | Title, meta, slug, cấu trúc heading, **trọng tâm** (heading nhận truy vấn chính, câu hỏi brief được trả lời), sapo, mật độ truy vấn, độ phủ thực thể, liên kết, ảnh và alt |
| `evidence_check.py` | Tính hợp lệ của ledger, trích dẫn nguyên văn, nguồn gốc cho claim rủi ro cao, `GAP` lọt vào bài, **mọi con số trong bài có chỗ dựa trong ledger**, tín hiệu YMYL |
| `wiki_lint.py` | Sức khỏe kho tri thức: front matter, claim có nguồn và trích dẫn nguyên văn, liên kết chéo, trang mồ côi, trang quá cũ, và **bài đang dẫn văn bản đã hết hiệu lực** |
| `wiki_index.py` | Dựng lại `wiki/index.md` từ front matter (`build`), hoặc báo khi mục lục đã lệch (`check`) |

Không cần cài gói ngoài. Bộ từ điển nhận diện nằm ở `scripts/lexicon/ai_phrases.json`, sửa được tự do.

**Đừng nới ngưỡng để bài qua cửa.** Sau mỗi lần sửa lexicon hoặc ngưỡng, chạy lại hai fixture trong
`examples/` để kiểm tra bộ kiểm còn phân biệt được bài dở với bài tốt.

## Gói bàn giao

```
work/<slug>/
├── brief.yaml              # intent, truy vấn, thực thể, câu hỏi, url_decision, người đọc, CTA
├── serp-notes.md           # ghi chép SERP và khoảng trống đã tìm được
├── competitors.json        # heading của top 5 — thiếu file này thì serp_outline.py exit 2
├── evidence-ledger.csv     # một dòng mỗi claim, có supporting_quote; wiki_ref nếu lấy lại từ wiki
├── outline.md              # sườn + link map + image plan
├── article.md              # bài hoàn chỉnh; SEO fields nằm trong front matter
├── qa-report.md            # kết quả máy kiểm + giải trình WARN + câu hỏi mở + checklist
├── qa-report.json          # kết quả máy đọc được
└── image-manifest.csv      # chỉ khi bài có ảnh
```

**Tám file, cộng `image-manifest.csv` khi bài có ảnh.** `.lark.json` là trạng thái đồng bộ do
`lark_sync.py` quản lý — không sửa tay, không thuộc gói bàn giao.

Mỗi thông tin một chỗ duy nhất: SEO fields không tách file riêng, link map ở trong outline,
câu hỏi mở ở trong qa-report.

## Giới hạn của công cụ

- **Máy chỉ bắt được lỗi cơ học.** Bài có đúng không, có hữu ích không, có bịa không — ba thứ đó chỉ
  agent và người duyệt kiểm được. `PASS` không có nghĩa là xong.
- **Không có công cụ nào bảo đảm thứ hạng Google.** Project này làm cho bài xứng đáng được xếp hạng,
  không hứa xếp hạng.
- **Không nhắm tới việc qua mặt bộ dò AI.** Các bộ dò hiện có độ chính xác không ổn định và không phải
  tín hiệu xếp hạng của Google. Lấy điểm detector làm mục tiêu sẽ khiến bài méo mó mà không tốt lên.
- **Không publish.** Đầu ra là gói bàn giao cho người thật duyệt. Việc đăng bài, gắn tác giả và tạo
  bản nháp CMS thuộc quy trình của `D:\Codex\workspaces\Create content blog`.
- **Cổng duyệt là quy ước làm việc, không phải cơ chế bảo mật.** Không có gì ngăn người dùng tự điền
  cả bốn trường duyệt mà không đọc bài. Nó ngăn agent tự cho phép mình, không ngăn được người.

## Quan hệ với project cũ

| | `Create content blog` | `content-seo` (project này) |
|---|---|---|
| Trọng tâm | Vận hành: chatbot duyệt, WordPress draft, idempotency, audit | Chất lượng nội dung: intent, bằng chứng, giọng văn, on-page |
| Đầu ra | Bản nháp WordPress sau hai cổng duyệt | Gói bàn giao Markdown + QA report |
| Nơi duyệt trên Lark | Sheet `FaRxs3Fa...` (Content Pipeline, 53 cột) | Base riêng, 4 bảng tiếng Việt |
| Quyền | Được tạo WordPress `status=draft` sau approval | Không gọi CMS |

Hai project dùng chung nguyên tắc zero-fabrication và cùng dừng trước khi publish. Dùng project này
để làm ra bài, dùng project kia để đưa bài qua quy trình duyệt và lên CMS.
