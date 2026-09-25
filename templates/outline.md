# Outline — <tiêu đề làm việc>

> Duyệt trên Lark, không duyệt trong file này: chọn `Kết quả duyệt = Đồng ý` và điền `Người duyệt`
> ở bảng Điều phối. Kiểm tra cổng bằng `python scripts/lark/lark_sync.py gate work/<slug>`.

Title: <tiêu đề sẽ lên Google, 50–60 ký tự>
H1: <tiêu đề hiển thị đầu bài — không trùng Title, không trùng URL>

Mọi thắc mắc liên hệ người lên outline <tên người lên outline>

## Thông tin gốc

| Trường | Giá trị |
|---|---|
| content_id | |
| Truy vấn chính | |
| Volume search | *người dùng cung cấp — không tự điền* |
| Intent | |
| Người đọc | |
| Việc người đọc làm xong sau bài | |
| Khoảng trống khai thác | |
| url_decision | |
| Mốc dữ liệu | |
| Ước lượng độ dài | ____ chữ — *suy ra từ số câu hỏi và lượng dữ liệu có thật, không đặt trước* |

## Sapo (2–4 câu)

Ghi ý chính sẽ viết, không viết sẵn văn:

- Câu trả lời trực tiếp cho truy vấn chính:
- Phạm vi / điều kiện áp dụng:
- Mốc thời gian:

## Hộp tóm tắt đầu bài (nếu phù hợp)

| | |
|---|---|
| | |

## Sườn bài

> Mỗi mục dự kiến của bài viết một dòng `### <tiêu đề mục>`. `outline_check.py` đọc đúng chỗ này.
>
> **Mục 1 phải nhận câu hỏi chính** — viết gần nguyên văn cách người đọc hỏi, và đứng đầu.
> Các mục sau phục vụ câu hỏi tiếp theo và **không lặp lại** truy vấn chính.
>
> **Đánh số theo format hệ Blog Muaban.net:** mục chính là số La Mã (`### I.`, `### II.`),
> mục con là số Ả Rập (`#### 1.`, `#### 2.`). Mục con không cần `source_ids` riêng.

### I. <viết lại truy vấn chính thành câu hỏi của người đọc>

- **Mục đích:** trả lời thẳng truy vấn chính, ngay mục đầu tiên
- **Trả lời trong 3 câu đầu:** <câu trả lời cô đọng, có điều kiện nếu cần>
- **Key claims:** ...
- **source_ids:** `C01`, `C03`
- **Định dạng:** câu trả lời thẳng + bảng / danh sách nếu giúp so sánh

### II. <câu hỏi tiếp theo của người đọc>

- **Mục đích:**
- **Key claims:**
- **source_ids:**
- **Định dạng:**

#### 1. <ý triển khai thứ nhất>

#### 2. <ý triển khai thứ hai>

### III. <câu hỏi tiếp theo>

### Lời kết

- **Mong muốn của người viết:** <người đọc làm được gì sau bài này>
- **Kêu gọi hành động:** bình luận, chia sẻ, hoặc xem thêm tại Muaban.net — chọn **một**, đúng với
  việc người đọc vừa làm xong
- **Không được:** tóm tắt lại toàn bài, hứa hẹn kết quả tài chính hay pháp lý

> **Hai quy tắc cắt:**
> - Mục nào không có `source_ids` và cũng không phải hướng dẫn thao tác → **cắt bỏ**.
> - Mục nào không trả lời câu hỏi nào trong brief → **cắt bỏ**. Không thêm mục để bài dài hơn.

## Phần tác động / checklist

Việc cụ thể người đọc làm được ngay sau khi đọc:

1.
2.

## FAQ

Chỉ điền nếu có câu hỏi **thật** quan sát được. Ghi nguồn câu hỏi.

| Câu hỏi | Quan sát ở đâu | Trả lời dựa trên |
|---|---|---|
| | | |

## Khối minh bạch (bắt buộc với bài YMYL)

- Phạm vi áp dụng:
- Dữ liệu cập nhật tới:
- Căn cứ (liệt kê nguồn có liên kết):
- Giới hạn / chỗ tùy từng trường hợp:
- Khuyến nghị tham vấn:

## SEO fields dự kiến

| Trường | Dự kiến | Độ dài |
|---|---|---|
| title | | |
| meta description | | |
| slug | | |
| schema đề xuất | | |

Khi viết, các trường này đi thẳng vào front matter của `article.md`.

## Link map

| Loại | Anchor (mô tả đích đến) | URL đích | Đặt ở mục nào và vì sao |
|---|---|---|---|
| internal | | | |
| external | | | |

Tối thiểu: 1 liên kết nội bộ Muaban.net đúng địa bàn/loại hình, và 1 nguồn gốc bên ngoài cho
bài có dữ liệu. Không dùng anchor "tại đây" / "xem thêm".

## Image plan

| Vị trí | Giải thích được gì cho người đọc | Nguồn dự kiến | Bản quyền |
|---|---|---|---|
| hero | | | CLEARED / BLOCKED |

Bỏ trống nếu bài không cần ảnh. Ảnh minh họa chung chung không giải thích gì thì đừng thêm.

## Rủi ro và điểm còn trống

- Claim nào đang là `GAP`:
- Chỗ nào cần chuyên gia xác nhận:
- Dữ liệu nội bộ nào cần xin:
