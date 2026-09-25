---
# SEO fields sống ngay đây, không tách file riêng.
title: ""                       # 50-60 ký tự, truy vấn chính 1 lần ở nửa đầu, không hứa hẹn
meta_description: ""            # 140-160 ký tự, nói kết quả người đọc nhận được
slug: ""                        # chữ thường không dấu, 5-13 từ (đo từ 24 bài thật), không gắn năm nếu cập nhật hằng năm
primary_query: ""
data_as_of: ""                  # YYYY-MM-DD
review_after: ""                # YYYY-MM-DD
schema: "BlogPosting"           # 24/24 bài thật dùng BlogPosting, không dùng Article
schema_extra: "BreadcrumbList"  # thêm ImageObject khi có ảnh, FAQPage khi có mục hỏi đáp — docs/10 E3
toc: false                      # bắt buộc true khi bài > 1.200 chữ
author: ""                      # để trống nếu chưa có tác giả đã xác minh — KHÔNG bịa
status: "DRAFT"
---

# <Tiêu đề bài — H1 duy nhất>

<!--
Sapo: 2-4 câu. Trả lời THẲNG truy vấn chính. Nêu phạm vi và mốc thời gian nếu
nội dung phụ thuộc thời điểm. Không dẫn dắt, không lặp lại tiêu đề.
KHONG chen ky hieu [C01] vao than bai (quy tac 16b). Dan nguon bang cach neu ten van ban
ngay trong cau, vi du "Theo diem c khoan 2 Dieu 10 Nghi quyet 254/2025/QH15, ...".
claim_id chi ton tai trong evidence-ledger.csv va trong khoi "Can cu" cuoi bai.

Theo quy chuẩn on-page (docs/10): từ khóa chính phải xuất hiện trong 100 CHỮ ĐẦU
và được **in đậm** một lần. Chèn tự nhiên, không làm mất mạch lạc của đoạn.
H1 ở trên không được trùng nguyên văn Title và không trùng URL.
-->

## <Câu dẫn đầu tiên — đây là SAPO, đặt ở H2>

<!--
Sapo nằm trong chính thẻ H2 này, đúng như bài thật làm (quy tắc 14). Viết một câu dẫn đọc
được, KHÔNG để nguyên chữ "Sapo" hay "Mở bài" làm tiêu đề — house_voice_check.py cảnh báo.
-->

### I. <Câu hỏi thật thứ nhất — mục này nhận truy vấn chính>

<!--
Mỗi mục trả lời xong một câu hỏi và đứng độc lập được.
Phân biệt rõ: dữ kiện (khẳng định + nguồn) / diễn giải ("có thể lý giải", "cách hiểu là") /
dự báo ("nếu ... thì").

DANH XUNG NGUOI DOC (quy tac 17): moi muc chinh phai co it nhat mot cau khuyen lay "ban" lam
CHU NGU. Khuon: trang ngu -> "ban" -> dong tu khuyen -> viec cu the.
  Dung: "Truoc khi dat coc, ban can hoi ro gia dien, nuoc, phi gui xe."
  Sai:  "Truoc khi dat coc, can hoi ro gia dien, nuoc, phi gui xe."
Cau tra loi trong muc hoi dap cung phai goi "ban". Khong dung "minh" de chi nguoi doc.

Cau dau cua muc thi dat chu the len truoc (<chu the> + la/co + ...); tu cau thu hai moi goi
nguoi doc. Khong don menh de phu dai len truoc nong cot cau — xem docs/13.

Liên kết đặt ngay tại chỗ người đọc cần chuyển tiếp, anchor mô tả đích đến.
Tối thiểu 1 liên kết nội bộ Muaban.net đúng địa bàn/loại hình và 1 nguồn gốc bên ngoài.
onpage_check.py đọc liên kết trực tiếp từ bài — không cần link map riêng.
-->

#### 1. <Mục con, đánh số Ả Rập>

#### 2. <Mục con>

### II. <Câu hỏi thật thứ hai>

### III. <Câu hỏi thật thứ ba>

### <Tìm/Mua [loại hình] [địa bàn] trên Muaban.net>

<!--
BAT BUOC va dat AP CHOT, ngay truoc "Loi ket" (quy tac 15). house_voice_check.py CHAN bai
thieu muc nay. Day la muc noi dung that: cach loc tin, cac khu vuc lan can, khoang gia.
Khong phai mot dong quang cao.
-->

### Lời kết

<!--
Mục cuối, thay cho phần "Kết luận". Ba nhịp theo khuôn tòa soạn: chốt lại việc người đọc làm
được ngay → "Hy vọng..." → lời mời về Muaban.net. Phải gọi "bạn" (quy tắc 15 và 17).
Không "chúc bạn thành công".

Theo quy chuẩn on-page: đoạn kết thân bài nên nhắc lại từ khóa chính một cách
tự nhiên. Mỗi mục tối đa 230 chữ — dài hơn thì tách heading con.
-->

---

## Nguồn và phạm vi

- **Dữ liệu cập nhật tới:** <YYYY-MM-DD>
- **Phạm vi áp dụng:** <loại hình, địa bàn, thời điểm>
- **Giới hạn:** <chỗ nào tùy địa phương / ngân hàng / trường hợp>
- **Khuyến nghị:** <khi nào cần hỏi công chứng viên, luật sư, chuyên viên tín dụng>

**Căn cứ:**

1. [Tên văn bản / báo cáo đầy đủ](https://...) — công bố <ngày>, truy xuất <ngày>.
2. ...

<!--
Trước khi bàn giao:
  python scripts/run_qa.py <file này> --json qa-report.json
  python scripts/lark/lark_sync.py push <thư mục này>
-->
