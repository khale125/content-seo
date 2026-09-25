# 09 — Phát hiện chủ đề tự động

Radar trả lời câu hỏi *"tuần này viết gì"* bằng cách quét nguồn chính thống, thay vì chờ người
nghĩ ra đề tài.

## Nguyên tắc: tin tức là tín hiệu, không phải lệnh viết bài

Một văn bản mới ban hành **không** tự động thành một bài. Nó chỉ thành bài khi trả lời được:
ai đọc, họ quyết định được gì sau bài, và Muaban.net có gì để nói mà nơi khác không có.

Radar được thiết kế để **dễ nói không**. Không có ứng viên nào đạt thì báo cáo là không có.
Đề xuất một chủ đề yếu để lấp chỗ trống chính là con đường dẫn tới scaled content abuse
(xem `06-chinh-sach-google.md`).

## Thứ tự quét bám thứ tự ưu tiên nguồn

| Ưu tiên | Nguồn | Quét gì |
|---|---|---|
| 1 | `vanban.chinhphu.vn` | Nghị định, thông tư về đất đai, nhà ở, kinh doanh bất động sản |
| 2 | `moc.gov.vn` — Bộ Xây dựng | Công bố quý về nhà ở và thị trường, chỉ đạo về nhà ở xã hội |
| 3 | `sbv.gov.vn` — Ngân hàng Nhà nước | Lãi suất điều hành, tín dụng bất động sản |
| 4 | `nso.gov.vn` — Cục Thống kê | CPI nhóm nhà ở và vật liệu xây dựng |
| 5 | Sở Xây dựng / cổng tỉnh thành | Bảng giá đất, quy hoạch, thủ tục địa phương |
| 6 | Báo chí | **Chỉ để phát hiện sự kiện**, phải truy ngược về văn bản gốc |

Danh mục đầy đủ ở `scripts/radar/sources.json`. Trong đó **chỉ có URL đã mở được thật**, kèm
ngày xác minh. Nguồn địa phương cố tình **không** ghi sẵn URL — mỗi tỉnh một cổng khác nhau, ghi
sẵn mà chưa mở là đúng cái việc dự án này cấm. Thay vào đó có phương pháp tìm.

## Loại sự kiện đáng thành bài

**Văn bản pháp luật mới hoặc sửa đổi** — mạnh nhất. Có ngày, có số hiệu, có điều khoản trích được,
và làm mọi hướng dẫn cũ trở nên sai.

**Số liệu mới có phương pháp** — công bố quý của Bộ Xây dựng, CPI. Cho phép viết bài có con số
thay vì tính từ.

**Thay đổi chi phí vốn** — lãi suất điều hành, quy định cho vay. Đổi trực tiếp bài toán của
người mua.

**Hai chiều ngược nhau cùng lúc** — ví dụ giá giảm nhẹ trong khi lãi vay cao. Đây là loại đề tài
tốt nhất, vì nó tạo ra một câu hỏi thật mà người đọc không tự trả lời được.

Loại bỏ: dự thảo, đề xuất, phát biểu chưa thành văn bản; tin không đổi hành vi người đọc;
sự kiện đã có bài cùng intent mà không có gì mới để bổ sung.

## Giá trị lớn nhất của radar: tìm bài cũ đã lỗi thời

Với mỗi văn bản mới, câu hỏi quan trọng nhất không phải *"viết bài mới nào"* mà
***"bài nào trên blog đang dẫn quy định cũ"***.

```
site:muaban.net/blog <truy vấn liên quan>
```

Một bài đang xếp hạng tốt nhưng dẫn căn cứ đã hết hiệu lực vừa là **rủi ro** (thông tin sai trong
lĩnh vực YMYL) vừa là **cơ hội** (`UPDATE` giữ được thứ hạng, rẻ hơn và an toàn hơn `CREATE`).

Mặc định nghiêng về `UPDATE`. Chỉ `CREATE` khi thật sự chưa có URL nào phục vụ intent đó.

## Chống đề xuất trùng

Radar giữ `scripts/radar/seen.json`: vân tay mỗi sự kiện đã đề xuất, kèm kết cục.

```powershell
python scripts/radar/radar.py check --url "<url>" --event "<mô tả>"
python scripts/radar/radar.py list
python scripts/radar/radar.py close <slug> VIET|BO_QUA|GOP --note "..."
```

Vân tay là `URL nguồn + nội dung sự kiện`. Cùng một sự kiện được nhiều báo đưa sẽ tạo vân tay khác
nhau, nên `check` còn cảnh báo khi **gần trùng** (từ 55% từ khóa chung trở lên) với đề xuất cũ.

## Chốt chặn chống bịa đặt

`radar.py add` **từ chối** ứng viên khi:

- Thiếu `source_url`, hoặc URL không phải HTTPS.
- Thiếu `published_date`, sai định dạng, hoặc ở tương lai.
- Nguồn cũ hơn 400 ngày mà không nói rõ đã kiểm tra còn hiệu lực.
- `source_tier = SIGNAL` (báo chí) mà chưa ghi `primary_source_todo` — tức văn bản gốc phải truy
  ngược trước khi viết.

Đây là chốt đặt trong **script**, không phải trong hướng dẫn. Hướng dẫn thì agent có thể quên hoặc
tự thuyết phục mình bỏ qua; script thì không.

## Đầu ra

`radar.py add` dựng cho mỗi ứng viên:

```
work/<slug>/
├── brief.yaml          # đã điền sẵn phần radar biết; phần còn lại để trống
├── serp-notes.md       # mẫu, chờ bước outline
└── evidence-ledger.csv # chỉ có header
```

Radar **không** tạo `outline.md`. Một file mẫu chưa điền vẫn là file có nội dung, và sẽ bị tính
nhầm là "outline đã viết xong", khiến bản ghi nhảy qua cổng duyệt chủ đề.

> **Tài liệu này mô tả một bước tùy chọn, không còn nằm trong quy trình chính.** Quy trình hiện tại
> bắt đầu bằng việc bạn đưa **từ khóa chính kèm volume search**, nên trạng thái `Chờ duyệt chủ đề`
> đã bị bỏ. Radar giờ chỉ trình **danh sách gợi ý để bạn chọn từ khóa**, không đẩy lên Lark và không
> tạo bản ghi chờ duyệt. Chọn được từ khóa rồi thì chạy `seo-outline-bds` như bình thường.

## Nhịp chạy

| Việc | Nhịp |
|---|---|
| Văn bản pháp luật, Bộ Xây dựng, Ngân hàng Nhà nước | hằng tuần |
| CPI Cục Thống kê | hằng tháng, khoảng ngày 6 |
| Công bố quý Bộ Xây dựng | 3–4 tuần sau khi kết thúc quý |
| Rà bài cũ bị văn bản mới làm lỗi thời | hằng tháng |

Đừng chạy radar dày hơn năng lực viết. Hàng đợi ứng viên dài mà không ai viết chỉ tạo cảm giác
bận rộn, và cám dỗ viết ẩu để giải phóng hàng đợi.

## Giới hạn

- Radar **không tự đọc web bằng script**. Việc đọc và đánh giá nguồn là phán đoán, không phải
  parse HTML — nên agent làm, script chỉ lo trạng thái, chống trùng và chốt chặn.
- Radar **không chọn thay bạn**. Nó đề xuất; bạn duyệt chủ đề trên Lark.
- Radar không truy cập được dữ liệu tin đăng nội bộ của Muaban.net. Đề tài cần số liệu đó sẽ được
  ghi rõ là cần cung cấp thêm.
