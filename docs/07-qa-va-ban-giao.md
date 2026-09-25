# 07 — QA và gói bàn giao

## Ba lớp kiểm tra

| Lớp | Công cụ | Chặn ở đâu |
|---|---|---|
| Máy kiểm | `python scripts/run_qa.py` | Mọi `BLOCK` phải hết |
| Agent tự kiểm | Checklist bên dưới | Ghi kết quả vào `qa-report.md` |
| Người duyệt | Gói bàn giao | Quyết định cuối |

Máy kiểm bắt được lỗi cơ học. Nó **không** kiểm được bài có đúng không, có hữu ích không, có bịa
không — ba thứ đó chỉ agent và người duyệt kiểm được. Đừng coi `PASS` là xong.

## Chạy máy kiểm

```powershell
python scripts/run_qa.py work/<slug>/article.md --ledger work/<slug>/evidence-ledger.csv --brief work/<slug>/brief.yaml
```

Thêm `--json work/<slug>/qa-report.json` để lưu kết quả máy đọc được.
Chạy riêng từng phần khi cần: `human_voice_check.py`, `onpage_check.py`, `evidence_check.py`.

Mã thoát: `0` = PASS (không có BLOCK), `1` = có BLOCK, `2` = lỗi chạy.

## Checklist agent tự kiểm

### Độ chính xác

- [ ] Mọi số, tỷ lệ, ngày, số hiệu văn bản trong bài đối chiếu được với `supporting_quote` trong ledger.
- [ ] Mọi `source_url` đã mở lại và còn sống tại ngày bàn giao.
- [ ] Văn bản pháp luật được dẫn chưa bị sửa đổi/thay thế.
- [ ] Tên cơ quan, địa danh, loại giấy tờ viết đúng.
- [ ] Đơn vị đúng (m² chứ không phải m, triệu/m² chứ không phải triệu).
- [ ] Không còn dòng `GAP` nào biến thành câu khẳng định trong bài.

### Intent và cấu trúc

- [ ] Sapo trả lời thẳng truy vấn chính trong 2–4 câu.
- [ ] Mọi câu hỏi liệt kê trong `brief.yaml` đều được trả lời.
- [ ] Một H1; heading không nhảy cấp; heading là câu hỏi/mệnh đề, không phải cụm từ khóa.
- [ ] Không có mục nào tồn tại chỉ để dài hơn.
- [ ] FAQ (nếu có) là câu hỏi thật, không tự nghĩ.

### Giọng văn

- [ ] `human_voice_check.py` không còn `BLOCK`; các `WARN` đã được xử lý hoặc giải trình.
- [ ] Độ dài câu và đoạn có biến thiên.
- [ ] Không còn sáo ngữ mở bài, nối câu công nghiệp, kết bài đóng hộp.
- [ ] Mỗi mục lớn có ít nhất một câu có lập trường (nên/không nên/cẩn thận chỗ này).
- [ ] Phân biệt rõ dữ kiện, diễn giải, dự báo.

### SEO

- [ ] Title nhắm 50–60 ký tự, máy cảnh báo ngoài 40–65 (trong front matter của `article.md`), chứa truy vấn chính một lần, không hứa hẹn.
- [ ] Meta description nhắm 140–160 ký tự, máy cảnh báo ngoài 120–165, nói kết quả người đọc nhận được.
- [ ] Slug ngắn, không dấu, không trùng bài cũ.
- [ ] Có tối thiểu 1 internal link Muaban.net đúng địa bàn/loại hình, anchor mô tả (đối chiếu link map trong `outline.md`).
- [ ] Có tối thiểu 1 external link tới nguồn gốc (bài có dữ liệu).
- [ ] Mọi liên kết HTTPS, còn sống; external có `rel="noopener"`.
- [ ] Có **link out định nghĩa trong thân bài**, không dồn hết liên kết ngoài xuống khối "Căn cứ".
- [ ] Miền của mọi liên kết ngoài đều có trong `evidence-ledger.csv`; không có Wikipedia trong cột
      `source_url`.
- [ ] Alt text mô tả ảnh, không nhồi từ khóa.
- [ ] Schema khai đúng `BlogPosting` + `BreadcrumbList` (+ `ImageObject` khi có ảnh, `FAQPage` khi
      có mục hỏi đáp), và **không khai thứ bài không có**.
- [ ] Bản thảo là Markdown thuần, không còn `<span>`/`style="..."`.

### Tuân thủ

- [ ] Không câu nào bảo đảm giá, lợi nhuận, thanh khoản, duyệt vay, kết quả pháp lý.
- [ ] Bài YMYL có phạm vi, mốc dữ liệu, căn cứ, giới hạn, khuyến nghị tham vấn.
- [ ] Dữ liệu tin đăng Muaban.net ghi rõ là giá chào, kèm cỡ mẫu, kỳ, phạm vi.
- [ ] Không sao chép câu chữ, outline, dữ liệu độc quyền hay ảnh của đối thủ.
- [ ] Mọi ảnh có bản quyền rõ ràng, có manifest.
- [ ] Đã trả lời hết checklist trong `06-chinh-sach-google.md`.

## Gói bàn giao

Thư mục `work/<slug>/` phải có đủ:

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

SEO fields sống trong front matter của `article.md`; link map và image plan sống trong `outline.md`;
câu hỏi mở sống trong `qa-report.md`. Mỗi thông tin một chỗ duy nhất.

Phần **câu hỏi mở** trong `qa-report.md` là phần quan trọng nhất với người duyệt. Ghi rõ:

- Claim nào phải bỏ vì không tra được nguồn.
- Chỗ nào cần chuyên gia xác nhận trước khi đăng.

### Ghi chú cho người đăng bài — bắt buộc trong `qa-report.md`

Bốn việc dưới đây là **kỹ thuật SEO của khâu CMS**, Markdown không diễn đạt được, nên nếu không ghi
ra thì chúng biến mất khỏi quy trình. Nguồn: tab *Kĩ thuật SEO* của file quy chuẩn, đối chiếu ở
`docs/10` mục E.

| Việc | Ghi cụ thể gì |
|---|---|
| Thuộc tính liên kết ngoài | Liệt kê từng URL ngoài trong bài, kèm `target="_blank" rel="nofollow noopener"`. Liên kết tài trợ thì `rel="sponsored nofollow noopener"`. Bài thật làm vậy với **toàn bộ** liên kết ngoài |
| Bộ schema | Đúng bộ đã khai trong front matter, và nhắc chèn ở `<head>` |
| Làm sạch code | Nhắc gỡ CSS inline mà trình soạn thảo sinh ra, giữ nội dung trong `<p>` |
| Mốc rà Content Gap | **Ngày đăng + 3 tháng**. Không biết ngày đăng thì ghi đúng cụm đó, đừng đoán một ngày |

## Đẩy lên Lark

```powershell
python scripts/lark/lark_sync.py push work/<slug>
```

Chỉ đưa bài lên cổng duyệt khi `qa_status = PASS`. Còn `BLOCK` thì sửa trước — đẩy một bài còn
`BLOCK` lên cổng duyệt là đẩy việc của mình sang người khác.

## Sau khi cổng duyệt bài mở: bản nháp trên WordPress

```powershell
python scripts/wp/wp_draft.py work/<slug> --dry-run
python scripts/wp/wp_draft.py work/<slug>
```

Script tạo **bản nháp** (không bao giờ publish) trên `muaban.net/blog`: tải ảnh trong manifest lên
thư viện media kèm alt và caption, đổi bài sang HTML giữ đúng cấp heading, đặt chuyên mục Nhà đất và
ảnh đại diện, rồi in đường dẫn mở trong wp-admin. Ba chốt phải qua trước: QA `PASS` chạy lại tại chỗ,
`lark_sync.py gate` exit 0, và mọi ảnh `CLEARED`. Chi tiết ở `docs/14-anh-va-ban-nhap-wordpress.md`.

## Sau khi bàn giao

Project này dừng ở gói bàn giao. Việc đăng bài, gắn tác giả, tạo bản nháp CMS thuộc quy trình của
`D:\Codex\workspaces\Create content blog`.

Đặt lịch rà soát theo `review_after` trong `brief.yaml`, và rà lại ngay khi:
văn bản pháp luật liên quan thay đổi, số liệu hết kỳ, nguồn chết, hoặc SERP đổi format.
