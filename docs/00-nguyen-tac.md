# 00 — Nguyên tắc nền

## Bài toán thật sự là gì

Ba yêu cầu của project nghe như ba yêu cầu riêng, thực chất là một:

- *"Ontop Google"* — Google xếp hạng trang **giải quyết xong việc của người tìm kiếm**, không phải
  trang chứa nhiều từ khóa nhất.
- *"Không bịa đặt"* — bịa đặt là cách nhanh nhất để mất độ tin cậy với cả người đọc lẫn hệ thống
  đánh giá chất lượng.
- *"Giọng người thật"* — văn AI nghe giả không phải vì cấu trúc câu, mà vì **nó không biết gì cụ thể**.
  Văn chung chung sinh ra sáo ngữ; sáo ngữ là triệu chứng, thiếu thông tin mới là bệnh.

Nên thứ tự đúng là: **có thông tin cụ thể trước, viết sau**. Mọi kỹ thuật "nhân hóa" áp lên một bài
rỗng chỉ tạo ra văn rỗng nghe tự nhiên hơn.

## Năm nguyên tắc

### 1. Một bài = một việc người đọc cần làm xong

Trước khi viết, phải trả lời được: *Người đọc mở bài này ra, xong bài họ quyết định được điều gì?*
Nếu câu trả lời là "hiểu thêm về thị trường", đề tài chưa đủ hẹp. Nếu là "biết mình có đủ điều kiện
vay 70% giá trị căn hộ tại TP.HCM hay không", đề tài đã đủ hẹp để viết.

### 2. Chỉ viết được những gì đã tra ra

Mỗi con số, mốc thời gian, tên văn bản, tên dự án trong bài phải truy ngược được về một nguồn cụ thể
kèm ngày truy xuất. Không có nguồn thì có ba lựa chọn hợp lệ: bỏ claim, thu hẹp claim tới mức nguồn
chịu được, hoặc ghi rõ đây là nhận định chứ không phải dữ kiện. Lựa chọn thứ tư — đoán một con số
nghe hợp lý — không tồn tại.

### 3. Giá trị đến từ tổng hợp, không đến từ độ dài

Việc AI làm tốt và hợp pháp: đối chiếu nhiều nguồn, dựng bảng so sánh, rút ra hệ quả cho từng nhóm
người đọc, chỉ ra điều kiện áp dụng và ngoại lệ, dựng checklist thao tác. Việc AI không được làm:
tự tạo dữ kiện mới để bài dày hơn.

### 4. Viết cho một người cụ thể

"Người mua nhà" quá rộng. "Người đang có 900 triệu tiền mặt, muốn mua căn hộ 2 phòng ngủ ở Bình Tân,
chưa từng vay ngân hàng" là một người có thể viết cho. Giọng văn tự nhiên là hệ quả của việc biết
mình đang nói với ai.

### 5. Nói rõ chỗ mình không chắc

Bất động sản là lĩnh vực YMYL — thông tin sai có thể khiến người đọc mất tiền. Ghi rõ phạm vi áp dụng,
mốc dữ liệu, giả định, và chỗ cần hỏi chuyên môn. Một bài dám nói "phần này tùy từng chi nhánh ngân
hàng, bạn cần hỏi trực tiếp" đáng tin hơn một bài trả lời chắc nịch mọi thứ.

## Cái gì KHÔNG nằm trong phạm vi project này

- Không publish, không gọi WordPress/CMS.
- Không hứa thứ hạng. Không có công cụ nào bảo đảm được vị trí trên Google.
- Không "qua mặt" bộ dò AI. Mục tiêu là bài thật sự có giá trị, không phải bài né được detector.
  Các bộ dò AI hiện có độ chính xác không ổn định và **không phải** tiêu chí xếp hạng của Google;
  đừng lấy điểm detector làm mục tiêu.

## Rủi ro thật cần tránh

Google không phạt vì nội dung "được tạo bằng AI". Thứ bị nhắm tới trong chính sách spam là
**scaled content abuse** — sản xuất nhiều trang với mục đích chính là thao túng thứ hạng thay vì
giúp người đọc, bất kể do người hay máy tạo ra. Chi tiết và cách tự kiểm ở
[`06-chinh-sach-google.md`](06-chinh-sach-google.md).
