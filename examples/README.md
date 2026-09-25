# Ví dụ

Thư mục này chứa **fixture để kiểm thử script**, không phải nội dung để đăng.

| Thư mục | Mục đích | Kết quả mong đợi |
|---|---|---|
| `fixture-van-may/` | Bản nháp cố tình viết theo giọng máy: sáo ngữ, hứa hẹn, viện dẫn mơ hồ, số liệu không có nguồn, nhồi từ khóa vào heading. | `FAIL`, khoảng 8 `BLOCK` |
| `fixture-dat-chuan/` | Bản nháp viết đúng chuẩn: **mọi câu khuyên lấy "bạn" làm chủ ngữ** (quy tắc 17), có lập trường, có phạm vi và giới hạn, mọi con số truy được về ledger. | `PASS`, `0 BLOCK`, khoảng 6 `WARN` |
| `fixture-outline-lech/` | Outline lệch trọng tâm: không mục nào nhận câu hỏi chính, có mục "Kết luận". Chạy bằng `outline_check.py`. | `BLOCK` ở check `focus` |
| `fixture-humanizer/` | Bản nháp cài sẵn sáu nhóm pattern thích ứng từ Humanizer và bốn kiểm cấu trúc mới. Chạy bằng `human_voice_check.py`. | `0 BLOCK`, `15 WARN` |
| `fixture-wiki-dat/` | Wiki đạt chuẩn: front matter đủ, claim có nguồn và trích dẫn nguyên văn, liên kết chéo hai chiều. Chạy bằng `wiki_lint.py`. | `0 BLOCK`, `0 WARN` |
| `fixture-wiki-hong/` | Wiki cố tình hỏng: id không khớp tên file, thiếu trường `status`, liên kết trỏ vào hư vô, claim `VERIFIED` thiếu trích dẫn, và **văn bản hết hiệu lực mà vẫn còn bài đang dùng**. | `6 BLOCK` |

> **Nguồn trong ledger của cả hai fixture là `example.com` giả lập, không phải nguồn thật.**
> Đây là lựa chọn có chủ ý: dự án cấm tạo ra văn bản pháp luật hoặc số liệu nghe như thật, kể cả
> trong dữ liệu thử. Đừng dùng nội dung trong hai fixture làm nguồn tham khảo về bất động sản.

> **Mẫu giọng văn gốc nay là `reference/muaban-blog/`, không phải fixture.** Kho đó chứa **24 bài**
> thật đang đăng trên blog, kèm số đo ở `docs/12-giong-nha-muaban.md`. Fixture dưới đây từng được
> chỉ định làm mẫu giọng, nhưng đo ra thì nó lệch giọng thật còn nhiều hơn cả một bài đang bị chê
> cứng: 31% câu ngắn so với 2,8% của bài thật. Fixture đã được viết lại theo giọng nhà, và **lần
> thứ hai** theo quy tắc 17 — trước đó chỉ 25% câu khuyên của nó gọi người đọc, tức chính fixture
> làm mẫu lại đang dạy sai. Nó phải giữ trạng thái `0 BLOCK` và số chỉ số lệch trong mốc mà
> `house_voice_check.py` in ra.

`fixture-dat-chuan/article.md` dùng được làm **mẫu về giọng văn và cấu trúc** — cách mở bài,
cách đặt heading thành câu hỏi, cách nêu giới hạn, cách kết bài. Đừng chép nội dung của nó.

## Chạy thử

```powershell
python scripts/run_qa.py examples/fixture-van-may/article.md
python scripts/run_qa.py examples/fixture-dat-chuan/article.md
python scripts/outline_check.py examples/fixture-outline-lech/outline.md
python scripts/human_voice_check.py examples/fixture-humanizer/article.md
python scripts/wiki_lint.py --wiki examples/fixture-wiki-dat  --work work
python scripts/wiki_lint.py --wiki examples/fixture-wiki-hong --work work
```

Hai fixture này là bài kiểm tra ngược của bộ kiểm:

- Nếu `fixture-van-may` trả về `PASS` → bộ kiểm quá lỏng, xem lại `scripts/lexicon/ai_phrases.json`.
- Nếu `fixture-dat-chuan` trả về `FAIL` → bộ kiểm quá chặt, xem lại ngưỡng trong
  `scripts/human_voice_check.py` và `scripts/onpage_check.py`.

Thêm bài vào `reference/muaban-blog/` rồi chạy lại `house_voice_profile.py` thì **mọi dải đều
đổi**, nên phải chạy lại cả hai fixture ngay sau đó. Ngưỡng của `house_voice_check.py` không nằm
trong code mà sinh ra từ kho bài.

Chạy cả hai sau mỗi lần sửa lexicon hoặc ngưỡng.
