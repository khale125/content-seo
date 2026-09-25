---
name: seo-outline-bds
description: "Nghiên cứu intent và lên outline chuẩn SEO cho bài bất động sản Việt Nam (blog Muaban.net). Phân loại intent, đọc SERP tìm khoảng trống thật, gom cụm từ khóa theo SERP overlap, kiểm tra trùng nội dung, dựng evidence ledger trước khi viết, đẩy lên Lark Base rồi dừng lại chờ duyệt. Dùng khi người dùng nói: lên outline, sườn bài, nghiên cứu từ khóa, chọn đề tài, content brief, SERP gap, hoặc đưa một chủ đề bất động sản cần viết."
---

# Outline bất động sản chuẩn SEO

Skill này là **bước đầu tiên** của quy trình: từ **từ khóa chính + volume do người dùng đưa** →
brief → outline đã có bằng chứng. **Dừng lại sau outline.** Không viết bài trong cùng lượt chạy.

## Đầu vào

Người dùng gõ **từ khóa chính** và **volume search** vào bảng Điều phối trên Base, rồi tích ô
**`Duyệt từ khoá`**. Đó là toàn bộ điều kiện vào — không còn cổng duyệt chủ đề, vì việc chọn đề tài
đã do họ quyết bằng chính từ khóa đó.

**Thư mục làm việc do `lark_sync.py intake` tạo, không copy `templates/` bằng tay nữa:**

```powershell
python scripts/lark/lark_sync.py intake
```

Lệnh này sinh slug, tạo `work/<slug>/` với `brief.yaml` đã điền mã bài + truy vấn + volume,
`evidence-ledger.csv` rỗng, `serp-notes.md`, `competitors.json`, và ghi `.lark.json` để push sau này
bám đúng bản ghi. Nó **không** tạo `outline.md` — bạn tạo file đó ở Bước 6 từ `templates/outline.md`.

Thiếu volume thì hỏi một câu rồi làm tiếp; **không bao giờ tự ước lượng con số** (quy tắc 1). Để
trống `search_volume` còn hơn điền số đoán.

Ghi cả hai vào `brief.yaml`: `primary_query` và `search_volume`. Cột **Volume** trên bảng Điều phối
lấy thẳng từ đó, để bạn sắp xếp và ưu tiên bài ngay trên Base.

## Đọc trước

1. `CLAUDE.md` (hard rules)
2. `docs/00-nguyen-tac.md`
3. `docs/01-intent-va-keyword.md`
4. `docs/02-chuan-outline.md`
5. `docs/04-chinh-sach-nguon.md` (phần thứ tự ưu tiên nguồn + evidence ledger)
6. `docs/11-wiki-tri-thuc.md` + `wiki/schema.md` (tra trước khi nghiên cứu, ghi lại sau khi xác minh)

## Chuẩn bị thư mục

`intake` đã tạo sẵn bốn file trong `work/<slug>/`: `brief.yaml`, `serp-notes.md`,
`competitors.json`, `evidence-ledger.csv`. Việc còn lại của bạn là tạo `outline.md` từ
`templates/outline.md` ở Bước 6. Năm file đó là toàn bộ đầu ra của giai đoạn outline, không phải gói
bàn giao — gói đầy đủ ở `docs/07-qa-va-ban-giao.md`.

Thư mục chưa tồn tại thì đừng tạo tay: chạy `intake` trước, vì chỉ lệnh đó mới ghi được `.lark.json`
để bản ghi trên Base bám đúng thư mục.

## Bước 1 — Intent

Phân loại truy vấn hạt giống vào **một** nhóm: informational-khái-niệm, informational-thủ-tục,
investigational, transactional-local, navigational. Intent quyết định format, không phải ngược lại.

**Chặn sớm:** nếu SERP cho truy vấn chính chủ yếu là trang danh sách tin đăng hoặc trang công cụ,
ghi `url_decision: SKIP` và đề xuất loại trang đúng. Đừng cố viết blog dài hơn để chen vào.

## Bước 2 — Đọc SERP

Điền `serp-notes.md` cho 5–10 kết quả đầu: loại trang, chỗ trả lời câu hỏi chính, nguồn dữ liệu và
ngày cập nhật, câu hỏi bị bỏ sót, chỗ đã cũ hoặc sai.

Khoảng trống chỉ hợp lệ khi thuộc một trong năm dạng: **lỗi thời**, **thiếu cụ thể**, **sai format**,
**thiếu nhóm người đọc**, **thiếu dữ liệu địa phương**. Không tìm được dạng nào → `SKIP`, ghi lý do.

Chỉ đọc để hiểu intent và tìm gap. **Không mượn câu chữ, không clone outline, không lấy dữ liệu
độc quyền hay ảnh.**

### Bắt buộc: tổng hợp sườn từ top 5

Mở thật từng kết quả **trong top 5**, chép danh sách heading vào `competitors.json`
(mẫu ở `templates/competitors.json`). Ghi đúng thứ hạng thật trên SERP — kết quả từ vị trí 6 trở
xuống không tính vào mức sàn. Trang nào chặn truy cập thì ghi vào `not_captured` kèm lý do.

```powershell
python scripts/serp_outline.py analyze work/<slug>/competitors.json
```

Bốn quy tắc (chi tiết ở `docs/02-chuan-outline.md`):

1. Outline **tổng hợp từ top 5**, không dựng bằng cảm tính.
2. **Chủ đề đối thủ có thì mình phải có.** Thiếu là `BLOCK`. Muốn bỏ thì khai báo vào mục
   `## Chủ đề đã cân nhắc và không đưa vào` kèm lý do — bỏ im lặng không được chấp nhận.
3. **Phải có điểm khác biệt** — ít nhất một mục không kết quả nào trong top 5 có.
4. **Heading viết rõ ý, không trùng câu chữ của họ.** Cùng chủ đề thì được; cùng câu chữ là đạo văn.

`competitors.json` là danh sách câu hỏi phải trả lời, không phải sườn để copy.

## Bước 3 — Cụm từ khóa

Gom biến thế cùng SERP về một bài (`same_page_variants`); SERP khác hẳn thì tách ra bài khác
(`separate_pages`). Liệt kê `entities` và `questions_to_answer` — thực thể và câu hỏi quan trọng hơn
mật độ từ khóa. **Không đặt mục tiêu keyword density.**

## Bước 4 — Chống trùng

Tra `site:muaban.net/blog <truy vấn chính>`. Chốt `url_decision`: `CREATE` / `UPDATE` / `MERGE` / `SKIP`
kèm lý do. Đã có URL phục vụ cùng intent thì mặc định là `UPDATE`, không phải `CREATE`.

## Bước 5 — Evidence ledger TRƯỚC outline

### 5a. Tra wiki trước khi đi tìm nguồn

Đừng bắt đầu bằng công cụ tìm kiếm. Mở `wiki/index.md` trước.

Claim nào đã có trang wiki với `status: VERIFIED` thì chép thẳng vào `evidence-ledger.csv` —
tên trường trên wiki trùng khớp tên cột của ledger, không phải dịch — rồi điền cột **`wiki_ref`**
bằng `id` của trang.

Vẫn phải **mở lại `source_url`** nếu trang wiki đã cũ hơn ngưỡng trong `wiki/schema.md`
(số liệu 180 ngày, địa bàn 270 ngày, còn lại 400 ngày). Wiki nói nguồn **từng** đúng, không nói
nguồn **hiện còn** đúng. Mở lại xong thì cập nhật `retrieved_date` và `updated` của trang wiki.

Trang có `status: het-hieu-luc` thì **không được dùng**. `wiki_lint.py` chặn ở mức `BLOCK`, và đó
là tín hiệu bài này nên đổi căn cứ sang văn bản thay thế.

### 5b. Nghiên cứu phần còn thiếu

Điền `evidence-ledger.csv`: một dòng mỗi claim vật chất, có `supporting_quote` **nguyên văn** từ nguồn,
`source_url` HTTPS đã thật sự mở được, `published_date`, `retrieved_date`.

- Không tra được → `status: GAP`. Không bịa, không đoán URL.
- `FACT` + `risk: HIGH` (pháp lý, thuế, tín dụng, an toàn, giá) bắt buộc nguồn `LAW`/`GOV`/`STATS`.
- Báo chí là **tín hiệu dẫn đường**; quay về văn bản gốc mà bài báo nhắc tới.

### 5c. Ghi ngược vào wiki

Mọi claim vừa xác minh được mà **dùng lại được cho bài khác** — văn bản pháp luật, khái niệm,
hạn mức địa phương, chuỗi số liệu — phải được ghi vào wiki, nếu không bài sau lại đi tra từ đầu.

1. **Sửa trang đã có trước khi tạo trang mới.** Trùng lặp trong wiki sinh ra hai phiên bản sự thật.
2. Trang mới dùng khung `templates/wiki-page.md`, đặt đúng thư mục theo `type`.
3. Thêm `<slug>` của bài vào `used_in` — đây là chỉ mục ngược để radar biết bài nào cần `UPDATE`
   khi văn bản hết hiệu lực.
4. Điền `wiki_ref` ở dòng ledger tương ứng.

```powershell
python scripts/wiki_index.py build
python scripts/wiki_lint.py
```

Ghi một dòng vào `wiki/log.md`:

```
- 2026-09-16 · INGEST · nghi-dinh-50-2026 · 3 claim từ toàn văn Điều 6, dùng cho <slug>
```

Claim **chỉ đúng với riêng bài này** (ví dụ đặc điểm một dự án cụ thể) thì để nguyên trong ledger,
đừng đẩy lên wiki. Wiki là tri thức dùng lại được, không phải bản sao của ledger.

Ledger xong mới dựng sườn. Làm ngược lại sẽ sinh ra outline mà bằng chứng không đỡ nổi.

## Bước 6 — Outline

Dùng `templates/outline.md`. Chọn đúng một mẫu cấu trúc theo intent (mục "Cấu trúc chuẩn theo loại bài"
trong `docs/02-chuan-outline.md`).

**Format hệ Blog Muaban.net** (chi tiết ở `docs/02` mục "Format outline của hệ Blog Muaban.net"):
dòng `Mọi thắc mắc liên hệ người lên outline <tên>` ở đầu; sapo đặt ở **H2**; mục chính đánh số
La Mã (`### I.`), mục con số Ả Rập (`#### 1.`); mục cuối là **`### Lời kết`** có kêu gọi hành động.
Ghi định danh thật của agent vào dòng liên hệ — **không bịa tên người**.

Quy tắc bắt buộc:

- **Đúng một mục nhận câu hỏi chính, và mục đó đứng đầu.** Viết gần nguyên văn cách người đọc hỏi.
  Né nhồi từ khóa quá tay sẽ rơi vào lỗi ngược lại: bài không trả lời đúng câu người ta gõ vào.
- Các mục còn lại là **câu hỏi thật tiếp theo**, không lặp lại truy vấn chính.
- Mỗi H2 khai báo `source_ids`. H2 không có `source_ids` và cũng không phải phần tổng hợp/hướng dẫn
  thao tác → **cắt**.
- Ước lượng độ dài **suy ra từ** số câu hỏi và lượng dữ liệu có thật, không đặt trước.
- Không có mục "Kết luận" / "Tổng kết" tóm tắt lại bài. Mục **"Lời kết"** của format hệ Blog thì
  bắt buộc phải có, nhưng ruột là mong muốn người viết + **một** CTA, không phải tóm tắt.
- FAQ chỉ khi có câu hỏi thật quan sát được, ghi nguồn câu hỏi.
- Link map và image plan là hai mục trong chính `outline.md`, không tách file riêng.
- **Image plan liệt kê 6–10 ảnh**, khoảng một ảnh cho mỗi mục La Mã (đo 24 bài thật: trung vị 8).
  Mỗi dòng ghi *ảnh này giải thích được gì mà chữ không làm nhanh bằng*; không trả lời được thì bỏ
  ảnh đó, đừng chèn cho đủ số. Thứ tự ưu tiên nguồn ảnh ở `docs/14-anh-va-ban-nhap-wordpress.md`.
- URL đích cho link map lấy từ kho: `python scripts/internal_links.py find --brief work/<slug>/brief.yaml`.

## Bước 7 — Kiểm outline

```powershell
python scripts/outline_check.py work/<slug>/outline.md
python scripts/serp_outline.py check work/<slug>/outline.md
```

Phải hết `BLOCK` ở cả hai trước khi đẩy lên. Bốn lỗi hay gặp nhất:

- **Không mục nào nhận câu hỏi chính** — sườn nghe hợp lý nhưng không trả lời đúng truy vấn.
- **Thiếu chủ đề top có** — và cũng không khai báo lý do bỏ.
- **Không có điểm khác biệt** — phủ đủ nhưng không thêm gì, chưa đủ lý do để xếp trên họ.
- **Heading trùng câu chữ đối thủ** — cùng chủ đề thì được, cùng câu chữ là đạo văn.

Sửa ở đây tốn một phút.

## Bước 8 — Đẩy lên Lark và dừng

Bản ghi mới đi thẳng vào trạng thái **Chờ duyệt outline**, không qua cổng chủ đề.

```powershell
python scripts/lark/lark_sync.py push work/<slug>
```

Lệnh này cập nhật bản ghi trong bảng **Điều phối**, đổ evidence ledger vào bảng **Bằng chứng**, và tải
brief + outline lên Drive dưới dạng Markdown. Trạng thái chuyển thành "Chờ duyệt outline".

Push **không bao giờ** ghi "Đồng ý". Nếu outline đã sửa, push tự nhận ra nội dung đổi, tăng số Bản
và xóa trắng cụm duyệt — không cần `--bump` thủ công.

Sau đó báo cáo:

- Đề tài đã chọn và vì sao (why now + why Muaban.net).
- Khoảng trống khai thác kèm bằng chứng.
- `url_decision` và lý do.
- Số claim `VERIFIED` / `PARTIAL` / `GAP`, và các `GAP` ảnh hưởng tới mục nào.
- Rủi ro YMYL đã thấy trước và chỗ cần chuyên gia.
- Đường dẫn Base và `content_id` của bản ghi.

**Không viết bài.** Việc duyệt diễn ra trên Lark, không diễn ra trong hội thoại: kể cả khi người dùng
nói "duyệt rồi, viết đi", điều kiện vào skill `seo-writer-bds` vẫn là

```powershell
python scripts/lark/lark_sync.py gate work/<slug>    # exit 0 = đã duyệt
```

Nếu cổng chưa mở, nói rõ còn thiếu trường nào trên Lark và dừng.
