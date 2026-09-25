# 14 — Ảnh cho bài viết và bản nháp trên WordPress

Tài liệu này trả lời hai câu hỏi: **lấy ảnh ở đâu cho đúng nội dung và đúng luật**, và **đưa bài đã
duyệt lên WordPress thành bản nháp bằng cách nào**. Cả hai đều dừng trước nút Publish — đăng bài
vẫn là việc của người thật (quy tắc 9).

---

## A. Ảnh cho bài viết

### A1. Bài thật dùng bao nhiêu ảnh

Đo trên 24 bài đang đăng trong `reference/muaban-blog/`, đếm ảnh có chú thích:

| Số đo | Kết quả |
|---|---|
| Ảnh mỗi bài | **6–10** (p10–p90), trung vị **8**, cao nhất 19 |
| Bài không có ảnh nào | **1/24** |
| Thẻ `<img>` có `alt` rỗng | **0/1.377** — không một ảnh nào thiếu alt |
| Độ dài chú thích | 7–20 từ, trung vị 12,5 |

Khoảng 8 ảnh cho một bài 2.000 chữ tức là **mỗi mục La Mã một ảnh**. `onpage_check.py` cảnh báo khi
bài không có ảnh nào, và ghi chú khi số ảnh dưới 6.

Chú thích của blog là một câu mô tả gắn với ý của mục, thường nhắc lại từ khóa một cách tự nhiên —
ví dụ *"Diện tích thực tế của công đất giữa ba miền của nước ta là khác nhau"*. Không viết chú thích
kiểu "Ảnh minh họa" hay "Nguồn: Internet".

### A2. Thứ tự ưu tiên khi đi tìm ảnh

1. **Ảnh tự dựng từ dữ liệu đã có nguồn** — sơ đồ, bản đồ, bảng so sánh, biểu đồ. Đây là loại ảnh
   duy nhất chắc chắn đúng ngữ cảnh Việt Nam, chắc chắn sạch bản quyền, và nói được điều mà chữ phải
   mất cả đoạn mới nói xong. Bài có dữ liệu mà minh họa bằng ảnh stock là bỏ phí.
2. **Ảnh chụp thật của đội ngũ** — ghi người chụp và ngày chụp vào manifest.
3. **Kho ảnh có giấy phép rõ ràng**: Unsplash, Pexels, Pixabay (giấy phép cho dùng thương mại),
   Wikimedia Commons và Openverse (thường là CC BY hoặc CC BY-SA, **bắt buộc ghi công đúng cách**).
   Luôn lưu `source_url`, `creator`, `license`, `license_url`, `retrieved_date`.
4. **Ảnh của chính Muaban.net** — kho ảnh nội bộ hoặc ảnh tin đăng, **chỉ khi có xác nhận nội bộ**,
   và ghi tên người xác nhận vào cột `purpose` hoặc `creator`.

### A3. Tuyệt đối không dùng

| Không dùng | Vì sao |
|---|---|
| Ảnh tải từ Google Images mà không truy được nguồn gốc | Không biết giấy phép thì mặc định là không có quyền |
| Ảnh báo chí, ảnh của đối thủ, ảnh có watermark | Vi phạm bản quyền, và `docs/06` đã cấm lấy tài sản của đối thủ |
| Hotlink thẳng từ site khác | Ăn cắp băng thông, và ảnh chết bất cứ lúc nào |
| Ảnh có mặt người nhận ra được mà không có sự đồng ý | Rủi ro quyền nhân thân |
| **Ảnh AI dựng ra để minh họa một địa điểm, giấy tờ hay công trình có thật** | Nhìn như bằng chứng nhưng không phải — đúng thứ quy tắc 1 cấm. Ảnh AI chỉ dùng cho hình trang trí trừu tượng, và phải ghi rõ trong manifest |

### A4. Quy trình làm ảnh cho một bài

1. **Lên image plan ngay ở outline** (mục có sẵn trong `templates/outline.md`): mỗi mục La Mã một
   dòng, ghi *ảnh này giải thích được gì mà chữ không làm nhanh bằng*. Không trả lời được câu đó thì
   bỏ ảnh, đừng chèn cho đủ số.
2. **Tìm ảnh theo danh từ cụ thể trong bài**, không theo chủ đề chung: "công tơ điện phòng trọ",
   "sổ hồng bản gốc", "ký túc xá sinh viên" — không phải "bất động sản". Không tìm được ảnh đúng
   ngữ cảnh Việt Nam thì **dựng sơ đồ thay vì lấy ảnh nước ngoài cho có**.
3. **Kiểm trước khi nhận**: giấy phép cho dùng thương mại, đủ độ phân giải, không watermark, không
   chứa chữ nước ngoài gây hiểu nhầm, không có logo đối thủ trong khung hình.
4. **Lưu file** vào `work/<slug>/images/`, tên không dấu chữ thường, ưu tiên `.webp`.
5. **Ghi một dòng `image-manifest.csv`** cho mỗi ảnh (khuôn ở `templates/image-manifest.csv`), gồm
   `rights_status`: `CLEARED` khi đã rõ quyền, `BLOCKED` khi chưa.
6. **Chèn vào bài** kèm alt mô tả đúng ảnh, và một dòng in nghiêng ngay dưới làm chú thích:

   ```markdown
   ![Công tơ điện riêng gắn trước cửa từng phòng trọ](images/cong-to-dien-phong-tro.webp)

   *Phòng có công tơ riêng giúp bạn đối chiếu số điện mỗi tháng thay vì tin vào cách tính khoán*
   ```

### A5. Máy kiểm những gì

| Kiểm | Mức |
|---|---|
| Bài không có ảnh nào | `WARN` — 23/24 bài thật có ảnh |
| Ảnh trong bài không có dòng trong `image-manifest.csv` | **`BLOCK`** |
| Dòng manifest có `rights_status` khác `CLEARED` | **`BLOCK`** |
| Manifest thiếu `source_url`, `license`, `alt_text` hay `caption` | `WARN` |
| Ảnh thiếu alt, alt nhồi từ khóa, ảnh không có chú thích | `WARN` / `BLOCK` (đã có từ trước) |
| Số ảnh dưới 6, hoặc chú thích ngoài 7–20 từ | ghi chú (`INFO`) |

Hai mức `BLOCK` ở đây là mới từ 24/09/2026. Trước đó `docs/05` và `docs/07` đã đòi mọi ảnh phải có
manifest và có bản quyền rõ ràng, nhưng **không có chỗ nào đọc file manifest** — cùng loại lỗ hổng
đã xảy ra với meta description và với schema.

---

## B. Đưa bài lên WordPress thành bản nháp

### B1. Ranh giới: bản nháp thì được, đăng thì không

Quy tắc 9 nói **không publish**, và nó vẫn nguyên như vậy. Cái được thêm là một bước hẹp: sau khi
cổng duyệt bài trên Lark đã mở, agent được tạo **bản nháp** trên WordPress để người duyệt đọc ngay
trong trình soạn thảo thật, xem ảnh và bố cục đúng như lúc đăng.

`scripts/wp/wp_draft.py` gửi `status: draft` và **không có cờ nào đổi được giá trị đó**. Nếu bài
trên WordPress đã ở trạng thái `publish`, script dừng lại và báo người thật thay vì sửa bài đang
sống. Nhấn Publish là việc của người.

### B2. Ba chốt trước khi chạm vào WordPress

1. `run_qa.py` chạy **lại tại chỗ** và phải `PASS`. Không tin `qa-report.json` cũ, vì file đó có thể
   sinh ra từ một bản thảo khác.
2. `lark_sync.py gate work/<slug>` phải trả về exit 0 — cổng duyệt bài đã mở (quy tắc 10). Lời người
   dùng trong hội thoại không thay được bước này.
3. Mọi dòng `image-manifest.csv` phải `CLEARED`. Một tấm ảnh chưa rõ quyền mà đã nằm trong thư viện
   media là rủi ro pháp lý thật, và gỡ ra không xóa được dấu vết.

### B3. Đăng nhập

Dùng **application password** của WordPress (Người dùng → Hồ sơ → Mật khẩu ứng dụng), đọc theo thứ
tự: biến môi trường `MBWP_USER` + `MBWP_APP_PASSWORD`, hoặc file JSON trỏ bởi `MBWP_CREDENTIALS`,
mặc định `%USERPROFILE%\.muaban-wp.json`:

```json
{"user": "<tài khoản wp>", "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"}
```

**File này nằm ngoài thư mục dự án và không bao giờ được chép vào trong.** Script không in mật khẩu
ra màn hình ở bất kỳ nhánh nào, kể cả khi báo lỗi. Mật khẩu ứng dụng lộ ra ngoài (ảnh chụp màn hình,
nhật ký chat, ticket) thì thu hồi trong WordPress rồi tạo cái mới — mất một phút, và không ảnh hưởng
mật khẩu đăng nhập chính.

### B4. Chạy

```powershell
python scripts/wp/wp_draft.py --check                    # thử đăng nhập
python scripts/wp/wp_draft.py work/<slug> --dry-run      # xem sẽ gửi gì, không chạm WordPress
python scripts/wp/wp_draft.py work/<slug>                # tạo / cập nhật bản nháp
```

Script làm bốn việc: tải ảnh trong manifest lên thư viện media kèm `alt_text` và `caption`; đổi
`article.md` sang HTML giữ đúng cấp heading của format hệ Blog (H2 sapo, H3 La Mã, H4 Ả Rập); tạo
bản nháp với `title`, `slug`, `excerpt` lấy từ `meta_description`, chuyên mục **Nhà đất**, ảnh đại
diện là dòng `hero` của manifest; rồi in đường dẫn mở bản nháp trong wp-admin.

Lần chạy sau trên cùng thư mục sẽ **cập nhật đúng bản nháp cũ**, vì `work/<slug>/.wp.json` giữ
`post_id`. Xóa file đó đi thì lần sau tạo bản nháp mới, nên đừng xóa nếu không cố ý.

### B5. Bốn việc người đăng bài vẫn phải làm

Markdown không diễn đạt được, `qa-report.md` mục "Ghi chú cho người đăng bài" đã liệt kê (quy tắc 18):

- Gắn `target="_blank" rel="nofollow noopener"` cho liên kết ngoài — script đã đặt sẵn khi đổi sang
  HTML, nhưng kiểm lại sau khi trình soạn thảo xử lý.
- Kiểm bộ schema `BlogPosting` + `BreadcrumbList` do template sinh ra.
- Gỡ CSS inline mà trình soạn thảo tự thêm.
- Ghi lịch rà Content Gap: ngày đăng + 3 tháng.
