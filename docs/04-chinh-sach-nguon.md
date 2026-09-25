# 04 — Chính sách nguồn và chống bịa đặt

## Nguyên tắc một câu

**Cái gì không tra được thì không viết.** Không có ngoại lệ "chắc là", "thường thì", "khoảng chừng".

## Thứ tự ưu tiên nguồn

Với bất động sản Việt Nam, xếp từ mạnh xuống yếu:

1. **Văn bản pháp luật và cổng thông tin chính thức.** Luật, nghị định, thông tư, quyết định của
   UBND tỉnh/thành, công báo, cổng dịch vụ công. Luôn ghi **số hiệu văn bản, ngày ban hành,
   ngày hiệu lực** và kiểm tra văn bản đã bị thay thế hay chưa.
2. **Cơ quan thống kê và ngân hàng nhà nước.** Số liệu kinh tế vĩ mô, lãi suất điều hành, CPI.
3. **Báo cáo có công bố phương pháp.** Báo cáo thị trường của tổ chức nghiên cứu, nếu **có nêu
   cỡ mẫu, phạm vi, cách thu thập**. Báo cáo không nói phương pháp thì chỉ được dùng như ý kiến,
   phải dẫn nguồn kèm tên tổ chức.
4. **Báo chí chính thống.** Dùng như **tín hiệu dẫn đường**, không dùng làm nguồn cuối. Đọc bài báo
   để biết có sự kiện, rồi tìm về văn bản gốc mà bài báo nhắc tới. Nếu không tìm được văn bản gốc,
   ghi rõ "theo báo X ngày Y" và hạ mức chắc chắn của câu.
5. **Dữ liệu tin đăng Muaban.net.** Xem mục riêng bên dưới.
6. **Diễn đàn, nhóm, bình luận.** Chỉ dùng để phát hiện câu hỏi người dùng đang hỏi.
   **Không bao giờ** dùng làm nguồn cho dữ kiện.

**Không được dùng làm nguồn:** nội dung của đối thủ, trang tổng hợp không nêu nguồn gốc, nội dung
do AI khác sinh ra, quảng cáo của chủ đầu tư, tin rao vặt đơn lẻ.

## Evidence ledger — bắt buộc

Mỗi claim vật chất một dòng trong `work/<slug>/evidence-ledger.csv`:

| Cột | Ý nghĩa |
|---|---|
| `claim_id` | `C01`, `C02`... dùng để trỏ từ outline. **Không chèn vào thân bài** — xem CLAUDE.md quy tắc 16b |
| `claim` | Câu sẽ viết trong bài, viết đúng như sẽ xuất hiện |
| `claim_type` | `FACT` / `INTERPRETATION` / `FORECAST` / `EXPERIENCE` |
| `risk` | `LOW` / `MED` / `HIGH` — HIGH cho pháp lý, thuế, tín dụng, an toàn, giá |
| `source_type` | `LAW` / `GOV` / `STATS` / `REPORT` / `NEWS` / `MARKETPLACE` / `NONE` |
| `source_url` | URL đầy đủ, HTTPS |
| `source_title` | Tên văn bản hoặc bài |
| `published_date` | Ngày ban hành hoặc đăng |
| `effective_date` | Ngày hiệu lực (với văn bản pháp luật) |
| `retrieved_date` | Ngày mình truy xuất |
| `supporting_quote` | **Đoạn nguyên văn** trong nguồn chứng minh claim |
| `status` | `VERIFIED` / `PARTIAL` / `GAP` |

Quy tắc:

- `supporting_quote` trống thì `status` không được là `VERIFIED`. Không tóm tắt thay cho trích dẫn;
  phải dán đúng câu chữ trong nguồn.
- Nguồn không chứa claim thì không phải nguồn của claim đó, dù cùng chủ đề.
- `claim_type = FACT` và `risk = HIGH` bắt buộc `source_type` thuộc `LAW`, `GOV` hoặc `STATS`.
- Mọi dòng `GAP` phải được xử lý trước khi bài qua QA: **bỏ claim**, **thu hẹp claim**, hoặc
  **chuyển thành câu hỏi mở cho người đọc tự kiểm tra**. Không được để `GAP` lọt vào bài dưới dạng
  câu khẳng định.

`scripts/evidence_check.py` đối chiếu các số, ngày, tỷ lệ phần trăm và đơn vị tiền xuất hiện trong bài
với ledger, và báo lỗi những giá trị không có dòng nào đỡ.

## Quy tắc riêng cho dữ liệu tin đăng Muaban.net

Đây là nơi dễ nói sai nhất.

- Giá trên tin đăng là **giá chào bán/chào thuê**, không phải **giá giao dịch**. Luôn viết rõ.
- Bắt buộc kèm: **số lượng tin** trong mẫu, **khoảng thời gian**, **phạm vi địa lý**, **loại hình**.
- Nếu mẫu dưới ngưỡng tối thiểu (mặc định 30 tin cho một quận/loại hình), **không đưa ra mức trung
  bình**. Mô tả định tính hoặc gộp phạm vi rộng hơn.
- Dùng **trung vị**, không dùng trung bình, vì tin đăng có đuôi giá rất lệch. Nếu đưa khoảng, dùng
  phân vị 25–75.
- Loại bỏ tin trùng, tin thiếu diện tích, tin giá bất thường trước khi tính, và ghi rõ đã loại.
- Không so sánh hai kỳ nếu cách thu thập giữa hai kỳ khác nhau.

Mẫu câu đúng:

> Trong 412 tin đăng bán căn hộ tại quận Bình Tân trên Muaban.net từ 01/04 đến 30/06/2026, giá chào
> trung vị là 41 triệu đồng/m² (khoảng phân vị 25–75: 36–47 triệu). Đây là giá người bán đưa ra,
> chưa phải giá chốt giao dịch.

## Chống bịa đặt — danh sách cấm

Tuyệt đối không sinh ra nếu không có nguồn:

- Con số bất kỳ: giá, diện tích, lãi suất, thuế, phí, tỷ lệ, thời gian xử lý, số lượng.
- Tên và số hiệu văn bản pháp luật, ngày ban hành, ngày hiệu lực.
- Tên dự án, chủ đầu tư, tiến độ, quy mô, thời điểm bàn giao.
- Thông tin quy hoạch, lộ trình hạ tầng, ngày khởi công/thông xe.
- Tên chuyên gia, chức danh, đơn vị, phát ngôn.
- Khảo sát, kết quả nghiên cứu, "theo thống kê".
- URL nguồn. **Không bao giờ dựng URL từ suy đoán** — chỉ dán URL đã thật sự mở được.
- Trải nghiệm cá nhân, ca khách hàng, ảnh chụp thực địa.
- Tác giả, bằng cấp, chứng chỉ hành nghề.

Khi thiếu, dùng đúng một trong ba cách:

1. **Bỏ.** Câu đó không cần thiết thì cắt.
2. **Thu hẹp.** Từ "phí công chứng khoảng 0,1% giá trị hợp đồng" (không tra được) về
   "phí công chứng tính theo bậc giá trị hợp đồng; bạn tra biểu phí tại phòng công chứng nơi làm thủ tục".
3. **Mở thành việc người đọc tự kiểm.** Biến chỗ trống thành hướng dẫn tra cứu cụ thể: tra ở đâu,
   hỏi ai, cần mang gì.

## YMYL — bất động sản luôn là YMYL

Bài chạm tới pháp lý, thuế, vay vốn, an toàn công trình hoặc quyết định tài chính lớn phải có:

- **Phạm vi áp dụng:** loại hình nào, địa bàn nào, thời điểm nào.
- **Mốc dữ liệu:** "Thông tin cập nhật tới ngày ...".
- **Căn cứ:** liệt kê văn bản/nguồn ở cuối bài, có liên kết.
- **Giới hạn:** nói rõ chỗ nào tùy địa phương, tùy ngân hàng, tùy trường hợp.
- **Khuyến nghị tham vấn:** với thuế, tranh chấp, hợp đồng, hồ sơ vay.
- **Đường sửa lỗi:** cách người đọc báo thông tin sai.

**Cấm tuyệt đối:** bảo đảm được vay, bảo đảm hồ sơ được duyệt, bảo đảm giá tăng, bảo đảm sinh lời,
bảo đảm thắng kiện, bảo đảm dự án đúng tiến độ. `scripts/human_voice_check.py` quét các mẫu câu này
và chặn ở mức `BLOCK`.

## Kiểm tra lại nguồn trước khi bàn giao

- Mở lại từng `source_url`; URL chết thì tìm bản thay thế hoặc hạ claim.
- Với văn bản pháp luật, kiểm tra **đã bị sửa đổi/thay thế chưa** tại thời điểm bàn giao.
- Ghi `retrieved_date` đúng ngày kiểm tra cuối.
- Đặt `review_after` cho bài: mặc định 6 tháng, 3 tháng với bài có số liệu thị trường,
  và ngay lập tức khi văn bản pháp luật liên quan thay đổi.
