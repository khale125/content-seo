# QA và câu hỏi mở — <slug>

Ngày chạy: ____________   Phiên bản: ____________

Đây là tài liệu người duyệt đọc kèm bài. Nó trả lời hai câu: **máy kiểm nói gì**, và
**bài này còn thiếu gì mà chỉ người mới xử lý được**.

## 1. Kết quả máy kiểm

```
python scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json
```

| | Số lượng |
|---|---|
| BLOCK | |
| WARN | |
| Trạng thái | PASS / FAIL |

Mọi `BLOCK` phải hết trước khi đưa bài lên cổng duyệt.

### Giải trình từng WARN còn lại

| Check | Dòng | Cảnh báo | Xử lý | Lý do giữ nguyên |
|---|---|---|---|---|
| | | | sửa / giữ | |

## 2. Câu hỏi mở — phần quan trọng nhất với người duyệt

**Không giấu khoảng trống bằng câu mơ hồ.** Một bài trung thực về giới hạn của nó đáng tin hơn
một bài trông hoàn hảo.

### Claim đã bỏ vì không tra được nguồn

| claim_id | Claim định viết | Đã tìm ở đâu | Xử lý trong bài |
|---|---|---|---|
| | | | bỏ / thu hẹp thành "..." / chuyển thành hướng dẫn tự tra |

### Cần chuyên gia xác nhận trước khi đăng

| Nội dung | Vì sao cần | Loại chuyên môn | Mức chặn |
|---|---|---|---|
| | | công chứng viên / luật sư / chuyên viên tín dụng | chặn đăng / nên có |

### Dữ liệu nội bộ cần xin

| Dữ liệu | Dùng ở mục nào | Ai giữ | Không có thì bài xử lý thế nào |
|---|---|---|---|
| | | | |

### Trải nghiệm thực tế còn thiếu

Truy vấn này có thể được phục vụ tốt nhất bởi người đã thật sự làm việc đó. Bài hiện thay bằng:

- [ ] Tổng hợp dữ liệu tin đăng
- [ ] Đối chiếu nhiều quy định
- [ ] Checklist dựng từ quy trình chính thức
- [ ] Gom câu hỏi thật từ người dùng

Nếu không đủ, đề xuất: ____________ (lấy trải nghiệm thật / đổi đề tài)

## 3. Checklist tự kiểm

Nguồn đầy đủ: `docs/07-qa-va-ban-giao.md`. Đánh dấu thật, không đánh dấu cho đủ.

**Độ chính xác**
- [ ] Mọi số, ngày, số hiệu văn bản đối chiếu được với `supporting_quote` trong ledger
- [ ] Mọi `source_url` đã mở lại và còn sống
- [ ] Văn bản pháp luật được dẫn chưa bị sửa đổi/thay thế
- [ ] Đơn vị và địa danh viết đúng
- [ ] Không còn `GAP` nào thành câu khẳng định

**Intent và giọng văn**
- [ ] Sapo trả lời thẳng truy vấn chính trong 2–4 câu
- [ ] Mọi câu hỏi trong brief đều được trả lời
- [ ] Heading là câu hỏi thật, không phải cụm từ khóa
- [ ] Độ dài câu và đoạn có biến thiên; không còn sáo ngữ mở/kết bài
- [ ] Mỗi mục lớn có ít nhất một câu có lập trường

**SEO và tuân thủ**
- [ ] Title, meta, slug đạt chuẩn; ≥1 internal link đúng địa bàn, ≥1 nguồn gốc bên ngoài
- [ ] Mọi liên kết HTTPS, còn sống, anchor mô tả đích đến
- [ ] Không câu nào bảo đảm kết quả tài chính hoặc pháp lý
- [ ] Bài YMYL có phạm vi, mốc dữ liệu, căn cứ, giới hạn, khuyến nghị tham vấn
- [ ] Dữ liệu tin đăng ghi rõ là giá chào, kèm cỡ mẫu, kỳ, phạm vi
- [ ] Mọi ảnh có bản quyền rõ ràng (`image-manifest.csv`)

**Rủi ro chính sách Google** — trả lời có/không, không trả lời "gần như"

| Câu hỏi | Trả lời |
|---|---|
| Bài có ít nhất một thứ không tìm được ở 5 kết quả đầu hiện tại? | |
| Không có bài nào khác trên blog phục vụ cùng intent? | |
| Nếu bỏ hết từ khóa đi, bài vẫn còn lý do tồn tại? | |
| Đọc xong người ta làm được việc, không phải đi tìm tiếp? | |

## 4. Rủi ro còn lại

| Rủi ro | Mức | Khuyến nghị cho người duyệt |
|---|---|---|
| | thấp / vừa / cao | |
