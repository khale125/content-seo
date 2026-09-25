# 01 — Intent, từ khóa và chọn đề tài

Mục tiêu của bước này: từ một chủ đề rộng, chốt được **một bài** với intent rõ, có khoảng trống thật
trên SERP, và Muaban.net có lý do chính đáng để nói về nó.

## Bước 1 — Xác định intent trước, từ khóa sau

Với mỗi truy vấn hạt giống, phân loại vào **một** nhóm. Nhóm quyết định format bài, không phải ngược lại.

| Intent | Dấu hiệu trong truy vấn | Format Google thường thưởng | Ví dụ BĐS |
|---|---|---|---|
| Informational — khái niệm | "là gì", "nghĩa là", "phân biệt" | Giải thích ngắn + ví dụ + bảng đối chiếu | "sổ hồng và sổ đỏ khác nhau thế nào" |
| Informational — thủ tục | "cách", "thủ tục", "hồ sơ", "bao lâu" | Quy trình đánh số + hồ sơ + chi phí + mốc thời gian | "thủ tục sang tên sổ đỏ" |
| Investigational | "có nên", "so sánh", "review", "kinh nghiệm" | Tiêu chí quyết định + đánh đổi + trường hợp nên/không nên | "có nên mua chung cư chưa có sổ" |
| Transactional / local | "giá", "cho thuê", "quận", "gần" | Trang danh sách, bộ lọc, dữ liệu thời điểm | "thuê phòng trọ quận 7" |
| Navigational | tên riêng, tên dự án | Trang thực thể chính chủ | "Vinhomes Grand Park" |

**Quy tắc chặn:** nếu SERP cho truy vấn chính hầu hết là **trang danh sách tin đăng** hoặc
**trang công cụ**, thì viết một bài blog để chen vào là chọn sai format. Khi đó đề xuất
trang danh mục / landing page và ghi lý do, đừng cố viết bài dài hơn.

## Bước 2 — Đọc SERP để tìm khoảng trống, không để sao chép

Hai việc song song, đừng bỏ việc nào:

1. **Ghi nhận định tính** vào `serp-notes.md` — loại trang, chỗ trả lời, nguồn dùng, chỗ đã cũ.
2. **Chép danh sách heading** của top 5 vào `competitors.json`, rồi chạy
   `python scripts/serp_outline.py analyze work/<slug>/competitors.json` để biết chủ đề nào là
   mức sàn. Chi tiết ở `02-chuan-outline.md`, mục "Đọc sườn bài của top 5".

Với 5–10 kết quả đầu, ghi vào `templates/serp-notes.md`:

- **Loại trang** (blog / danh sách / công cụ / diễn đàn / báo / trang chính phủ).
- **Bài trả lời câu hỏi chính ở đâu** — ngay đầu hay chôn ở giữa?
- **Dữ liệu bài đó dùng** — nguồn nào, cập nhật ngày nào, còn hiệu lực không?
- **Câu hỏi bài đó bỏ sót**, đặc biệt câu hỏi xuất hiện ở "Mọi người cũng hỏi", diễn đàn, phần bình luận.
- **Chỗ bài đó sai hoặc đã cũ** — văn bản pháp lý đã thay thế, số liệu quá hạn, địa giới hành chính đã đổi.

Khoảng trống hợp lệ là một trong các dạng sau:

1. **Lỗi thời** — nguồn của top hiện tại đã bị thay thế bởi văn bản/số liệu mới hơn.
2. **Thiếu cụ thể** — top nói nguyên tắc chung, không nói con số, mốc, hồ sơ, chi phí thật.
3. **Sai format** — người tìm cần quy trình, top đưa bài luận.
4. **Thiếu nhóm người đọc** — top viết cho người mua, người tìm là người bán / người thuê / môi giới.
5. **Thiếu dữ liệu địa phương** — top nói cả nước, truy vấn hỏi một quận/tỉnh.

Nếu không tìm được khoảng trống nào trong năm dạng trên: **không viết bài đó**. Ghi
`decision = SKIP` kèm lý do. Viết thêm một bài nữa nói y hệt top hiện tại chính là định nghĩa của
nội dung dư thừa.

## Bước 3 — Cụm từ khóa, không phải danh sách từ khóa

Gom về **một truy vấn chính** + biến thể cùng intent. Kiểm tra bằng cách so SERP: nếu hai truy vấn
có phần lớn kết quả trùng nhau, chúng thuộc cùng một bài. Nếu SERP khác hẳn, đó là hai bài.

Ghi lại:

```yaml
primary_query: "thủ tục sang tên sổ đỏ 2026"
same_page_variants:        # cùng SERP → cùng bài
  - "hồ sơ sang tên sổ đỏ"
  - "sang tên sổ đỏ cần giấy tờ gì"
separate_pages:            # SERP khác → bài khác, ghi để lên lịch sau
  - "phí sang tên sổ đỏ"   # SERP thiên về bảng phí
entities:                  # thực thể phải xuất hiện tự nhiên trong bài
  - "Văn phòng đăng ký đất đai"
  - "thuế thu nhập cá nhân 2%"
  - "lệ phí trước bạ 0,5%"
questions_to_answer:
  - "Nộp hồ sơ ở đâu?"
  - "Mất bao lâu?"
  - "Ai chịu thuế, bên mua hay bên bán?"
```

**Không** đặt mục tiêu mật độ từ khóa. Thực thể và câu hỏi quan trọng hơn lặp từ.

## Bước 4 — Chống ăn thịt lẫn nhau (cannibalization)

Trước khi chốt, tra `site:muaban.net/blog <truy vấn chính>`. Nếu đã có URL phục vụ cùng intent:

- Nội dung cũ còn dùng được → **cập nhật URL cũ**, không tạo URL mới.
- Có 2+ URL cũ chia nhau cùng intent → **gộp**, chọn một URL giữ lại, phần còn lại đề xuất 301.
- Chỉ trùng một phần → thu hẹp bài mới và đặt internal link hai chiều.

Quyết định phải nằm trong `brief.yaml` ở trường `url_decision: CREATE | UPDATE | MERGE | SKIP`.

## Bước 5 — Kiểm tra "vì sao là bây giờ" và "vì sao là Muaban.net"

Đề tài chỉ được duyệt khi trả lời được cả hai:

- **Vì sao bây giờ** — có văn bản mới, số liệu mới, mùa vụ, hay câu hỏi đang tăng? (Nếu là chủ đề
  thường trực thì ghi `evergreen` và nêu lý do cập nhật.)
- **Vì sao Muaban.net** — trang có dữ liệu tin đăng, có danh mục tương ứng, hay có đường dẫn hợp lý
  cho người đọc sau khi đọc xong? Nếu CTA duy nhất nghĩ ra được là "hãy truy cập Muaban.net", thì
  liên kết giữa bài và sản phẩm chưa đủ chặt.

## Đầu ra của giai đoạn này

`work/<slug>/brief.yaml` theo `templates/brief.yaml`, gồm: intent, truy vấn chính, biến thể, thực thể,
câu hỏi, khoảng trống, url_decision, người đọc mục tiêu, việc người đọc hoàn thành sau bài, CTA,
mốc dữ liệu, và các rủi ro YMYL đã thấy trước.
