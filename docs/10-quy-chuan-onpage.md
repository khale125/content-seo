# 10 — Quy chuẩn on-page (theo file quy chuẩn của dự án)

Nguồn: [Google Sheet quy chuẩn SEO on-page](https://docs.google.com/spreadsheets/d/1FQrXp0rpis4Gh5jGyig4ri4-cg8qOruNyJ_axRYxlQY/edit)
— 6 sheet: *Basic onpage*, *Advanced onpage*, *draf1*, *1. Onpage*, *2. Onpage (2)*,
*Note onpage nâng cao*. Đọc ngày 2026-09-15.

Bổ sung ngày 2026-09-23: tab **Kĩ thuật SEO**
([gid=1714737326](https://docs.google.com/spreadsheets/d/1FQrXp0rpis4Gh5jGyig4ri4-cg8qOruNyJ_axRYxlQY/edit?gid=1714737326))
— năm công đoạn của người làm kĩ thuật SEO: external link, làm sạch HTML code, schema,
Content Gap, và on-page nâng cao. Đối chiếu từng mục ở **phần E**.

Tài liệu này ghi lại phần **đã đưa vào dự án**, phần **đã điều chỉnh**, và phần **không áp dụng**
kèm lý do. Mỗi mục có nói rõ máy kiểm được hay phải người kiểm.

---

## A. Đã đưa vào và máy kiểm tự động

### A1. Title

| Quy chuẩn | Ngưỡng | Kiểm |
|---|---|---|
| Độ dài 50–60 ký tự | 50–60 là mục tiêu; máy cảnh báo ngoài 40–65 | `onpage_check` |
| Từ khóa càng gần bên trái càng tốt | trong 50% đầu | `onpage_check` → WARN |
| Toàn bộ title phải có dấu | có dấu tiếng Việt | `onpage_check` → WARN |
| Không ký tự đặc biệt `[ ] ! # @ $` | — | `onpage_check` → WARN |
| Title không trùng 100% với URL | so sánh sau khi bỏ dấu | `onpage_check` → WARN |
| Tham khảo điểm chung của top 5 | — | người kiểm, ghi vào `competitors.json` |
| Tính từ mạnh, con số, năm | tùy trường hợp | người kiểm |
| Tên thương hiệu trong title | **không dùng** | đo trên 24 bài thật: **0/24** title có "Muaban.net". File gốc ghi "nếu có thể", và blog chọn không |

**Độ dài đo từ 24 bài thật:** 49–70 ký tự, trung vị **59**, p10–p90 là 55–63. Ngưỡng máy
(40–65) rộng hơn dải đó, nên máy im không có nghĩa là đã đạt. **58% title thật có chữ số**
("12+ cách…", "Top 3 khu vực…", "6 ưu điểm…"); con số là cách blog tạo CTR, không phải tính từ.

### A2. H1 và sub-heading

| Quy chuẩn | Kiểm |
|---|---|
| Chỉ một H1, đứng đầu, không có heading nào phía trên | `onpage_check` → BLOCK |
| **H1 không trùng Title và không trùng URL** | `onpage_check` → WARN |
| H1 bao hàm toàn bộ ý bài, ngắn gọn, không ký tự đặc biệt | `onpage_check` → WARN |
| **Mỗi sub-heading tối đa 230 chữ** | `onpage_check` → WARN |
| Không nhảy cấp (H3 trong H2, H4 trong H3) | `onpage_check` → WARN |
| **Số lượng heading ngang ngửa hoặc hơn top 3** | `serp_outline check` → WARN |
| Phần Q&A: mỗi câu hỏi là một H3 hoặc H4 | người kiểm |

### A2a. Title, meta và H1 cùng bám một search intent

| Quy chuẩn | Kiểm |
|---|---|
| Title chứa truy vấn chính ở nửa đầu | `onpage_check` → WARN |
| Meta chứa ≥80% từ của truy vấn chính, trong 60 ký tự đầu | `onpage_check` → WARN |
| **H1 phủ ≥60% từ của truy vấn chính** | `onpage_check` → WARN |
| Câu mời đọc tiếp ở sapo nhắc truy vấn chính | `onpage_check` → WARN |

Người duyệt từ chối một bài với lý do *"Title và meta description, h1 cũng phải bám sát theo search
intent của từ khoá chính"*. Bài đó có Title và meta đều mở bằng *"… là điềm gì?"* trong khi H1 lại
là *"… dân gian nói gì và vì sao chúng bay vào"* — cùng chủ đề nhưng không phải câu người đọc gõ.
H1 vẫn phải **khác Title**, nhưng khác ở cách diễn đạt chứ không khác ở ý người đọc đi tìm.

### A2b. Từ khóa trong tiêu đề mục

| Quy chuẩn | Kiểm |
|---|---|
| **Mọi mục chính mang từ khóa chính hoặc từ khóa phụ** | `outline_check` → WARN |
| Đúng **một** mục chứa nguyên văn cụm từ khóa chính | `outline_check` → BLOCK khi nhiều mục cùng nhận |

Hai dòng trên đi cùng nhau. Người duyệt đã từ chối một outline vì các tiêu đề *không có từ khóa nào*
— hệ quả của việc agent né dòng thứ hai bằng cách cắt sạch từ khóa khỏi tiêu đề. Cách đúng là dùng
từ khóa phụ hoặc một phần cụm chính cho các mục sau, không phải bỏ trống.

### A3. Từ khóa ở vị trí quan trọng

| Quy chuẩn | Kiểm |
|---|---|
| **Từ khóa chính trong 100 chữ đầu** | `onpage_check` → WARN |
| **Từ khóa đó được in đậm** | `onpage_check` → WARN |
| **Đoạn kết bài chứa từ khóa chính** | `onpage_check` → WARN |
| In đậm dùng `<strong>`, không dùng `<b>`/`<bold>` | `onpage_check` → WARN |
| Chèn không được làm mất mạch lạc của đoạn văn | người kiểm |

### A4. Meta description

| Quy chuẩn | Ngưỡng | Kiểm |
|---|---|---|
| Độ dài | 120–165; bài thật 116–164, trung vị **147** | `onpage_check` → WARN |
| **Chứa truy vấn chính** (so sau khi bỏ dấu, ≥80% từ) | — | `onpage_check` → WARN |
| **Truy vấn chính nằm trong 60 ký tự đầu** | — | `onpage_check` → WARN |
| **Có khả năng kêu gọi hành động** | — | `onpage_check` → WARN |
| Không chép lại title quá 45 ký tự đầu | — | `onpage_check` → WARN |
| Chứa tính từ mạnh | — | người kiểm |

#### Khuôn meta của blog, đo từ 24 bài thật

> **`<động từ dẫn>` + `<cụm truy vấn chính>` + `:` hoặc `với` + `<3–5 thứ bài trả lời>` +
> `<lợi ích người đọc nhận được>`**

Ba ví dụ nguyên văn:

> *"Kinh nghiệm thuê phòng trọ Bình Chánh: cách chọn vị trí, giá thuê, kiểm tra phòng và lưu ý
> hợp đồng để tránh rủi ro."*
> *"Tìm hiểu kinh nghiệm thuê phòng trọ Quận 1 an toàn, tiết kiệm chi phí với những lưu ý quan
> trọng về giá thuê, hợp đồng, vị trí và cách tránh rủi ro khi thuê phòng."*
> *"Tổng hợp kinh nghiệm thuê phòng trọ Quận 12 từ A-Z: cách chọn khu vực, tham khảo giá thuê,
> lưu ý khi đặt cọc và bí quyết tìm phòng phù hợp, an toàn."*

Số đo đỡ cho khuôn này:

| | Bài thật |
|---|---|
| Meta chứa ≥80% từ đặc trưng của title | **21/24 (88%)** |
| Trong số đó, đặt từ khóa trong 60 ký tự đầu | **21/21**, vị trí trung vị là ký tự thứ 9 |
| Có động từ dẫn / cụm kêu gọi | 17/24 (71%) |
| Có tên thương hiệu | 7/24 (29%) — **không bắt buộc** |
| Là câu hỏi | 3/24 (12%) — không phải khuôn chính |
| Có chữ số | 12/24 (50%) |

**Vì sao phải ghi lại bằng số.** Bài 001 từng bị người duyệt từ chối với nhận xét *"mô tả meta
đang đọc không hiểu gì, không thu hút, không có đối thủ nào viết như vậy cả"*. Meta lúc đó là
*"UEH có tới 10 cơ sở nằm rải khắp TPHCM nên hai chữ gần trường mỗi người một nghĩa..."* — đủ
160 ký tự, có cụm kêu gọi, nên **máy kiểm cho qua sạch**. Nhưng nó không chứa cụm "thuê trọ",
không nói bài trả lời những gì, và vế đầu mất nghĩa vì cụm *"gần trường"* bị bỏ dấu ngoặc kép.
Hai chốt đầu bảng trên sinh ra từ đúng lần đó.

### A4b. URL / slug

| Quy chuẩn | Ngưỡng | Kiểm |
|---|---|---|
| Chỉ chữ thường không dấu, số, gạch nối | — | `onpage_check` → BLOCK |
| Chứa từ khóa trọng điểm | — | `onpage_check` → WARN qua độ phủ |
| Ngắn nhất có thể **nhưng vẫn bao hàm toàn ý** | 5–13 từ | `onpage_check` → WARN |
| Không gắn năm nếu bài cập nhật hằng năm | — | `onpage_check` → WARN |
| Đổi URL thì phải 301 redirect URL cũ | — | người kiểm / CMS |

**Ngưỡng cũ là "3–6 từ", và nó bắt oan 23/24 bài thật.** Đo slug của 24 bài đang đăng: 5–13 từ,
trung vị **7**. Bài dài nhất là `kinh-nghiem-thue-tro-gan-truong-dai-hoc-su-pham-ky-thuat-tphcm`
(13 từ) — chính bài cùng cụm với bài 001. File gốc đã nói trước điều này: *"Đôi khi URL quá ngắn
chỉ chứa Keyword chính cũng là con dao 2 lưỡi, bạn cần cân nhắc xem thị trường/đối thủ của mình
đặt URL như thế nào."* Ngưỡng nay lấy từ chính dải của blog.

### A5. Hình ảnh

| Quy chuẩn | Kiểm |
|---|---|
| Ảnh đầu tiên: alt chứa từ khóa chính đại diện topic | `onpage_check` → WARN |
| Ảnh kế tiếp: từ khóa phụ / semantic / mô tả ảnh | người kiểm |
| **Mỗi ảnh phải có caption** | `onpage_check` → WARN |
| Alt vẫn phải mô tả đúng ảnh cho người không nhìn thấy | `onpage_check` → BLOCK nếu nhồi |

### A6. Mục lục (TOC)

| Quy chuẩn | Kiểm |
|---|---|
| **Bài dài phải có TOC**, click nhảy đúng heading | `onpage_check` → WARN khi bài > 1.200 chữ mà không có. **Trừ bài theo format hệ Blog Muaban.net** — format đó không có mục lục, các mục đánh số La Mã thay thế. Xem CLAUDE.md quy tắc 14 |
| TOC đặt ở nơi dễ click, đầu bài | người kiểm |

### A7. Liên kết ngoài

| Quy chuẩn | Kiểm |
|---|---|
| Mở tab mới, không chuyển thẳng trên cùng tab | người đăng bài — ghi trong gói bàn giao (E1) |
| **Không trỏ tới trang affiliate, trang bán hàng, dịch vụ** | `onpage_check` → WARN, danh sách ở `lexicon/ai_phrases.json` khóa `commercial_url_hints` |
| Không trỏ tới trang đối thủ | `onpage_check` → WARN, khóa `competitor_hosts` |
| Trang trust thấp thì `nofollow` | người đăng bài. Dự án **không đo được DR** nên thay bằng điều kiện đo được: miền phải có trong ledger (E1) |
| Anchor là từ khóa semantic hoặc liên quan mật thiết | `onpage_check` → WARN nếu anchor chung chung |
| **Hai loại link out**: định nghĩa trong thân bài + tham khảo cuối bài | `onpage_check` → WARN khi mọi link ngoài dồn hết xuống khối cuối |

### A8. Schema cho bài blog

Theo sheet *Advanced onpage* và tab *Kĩ thuật SEO*, dạng Blogpost cần:

1. `BlogPosting` → `mainEntityOfPage`
2. `BreadcrumbList`
3. `ImageObject` cho featured image
4. `VideoObject` (nếu có video phù hợp)
5. Schema TOC
6. `FAQPage` (nếu có FAQ **hiển thị trên trang**)

Quy tắc chung của file, trùng với quy tắc sẵn có của dự án: **khai báo gì trong schema thì bài
phải thật sự có thứ đó**.

Từ 2026-09-23 mục này **có máy kiểm**: `onpage_check.check_schema` đọc hai trường `schema` và
`schema_extra` của front matter. Trước đó A8 chỉ là tài liệu — không một dòng code nào đọc trường
`schema`, và bài 001 khai `Article` vẫn qua sạch. Đó đúng là loại lỗ hổng đã xảy ra với meta
description, nên cách sửa cũng như lần đó: đo bài thật rồi đặt ngưỡng. Số đo và mức chặn ở **E3**.

### A9. Content gap sau khi bài đã chạy

Chỉ áp dụng khi bài **trên 3 tháng** và đã vào top 10–20. Lấy truy vấn thật từ Search Console
(Hiệu suất → Trang → URL chứa) kết hợp Ahrefs Content Gap, rồi bổ sung nội dung cho những truy vấn
người dùng thật sự dùng để tìm tới trang.

Đây là bước **làm mới**, thuộc `docs/07`, không phải bước viết mới. Việc của người viết chỉ là
để lại mốc: `review_after` trong front matter, và một dòng trong gói bàn giao ghi ngày sớm nhất
được rà Content Gap (ngày đăng + 3 tháng). Chi tiết ở **E4**.

---

## B. Đã điều chỉnh so với file gốc — và vì sao

### B1. Mật độ từ khóa: đo và đối chiếu, không đặt làm mục tiêu

**File gốc** (sheet *Note onpage nâng cao*) yêu cầu: *"Mật độ keywords nên cao hơn tối đa thị trường
0,3%"* và *"keywords density của từ khóa SEO chính phải đứng đầu bảng"*.

**Dự án điều chỉnh thành:** đo mật độ, đối chiếu với khoảng của top, và **cảnh báo cả hai phía** —
thấp quá thì có thể lệch chủ đề, cao quá thì là dấu hiệu viết gượng.

Lý do: đặt mật độ làm mục tiêu số là cách nhanh nhất tạo ra văn gượng, và văn gượng chính là thứ
`human_voice_check.py` tồn tại để chặn. Chính file gốc cũng lặp lại năm lần *"khi chèn không được
mất đi sự mạch lạc của đoạn văn"* — nên tinh thần là **điều chỉnh về gần chuẩn thị trường mà vẫn
đọc trôi**, không phải đẩy số lên cho vượt.

Ngưỡng `BLOCK` khi mật độ > 2,5% giữ nguyên.

### B2. Blockquote: giữ phần trích dẫn, bỏ phần gom referring domain

**File gốc** yêu cầu blockquote dạng
`<blockquote class="tu-khoa-seo" cite="https://ow.ly/abc#semantic-keyword">`, và giải thích ở mục TOC:
*"càng nhiều link rút gọn thì càng đa dạng được reffering domains => tăng trust"*.

**Dự án áp dụng:** dùng `<blockquote>` cho **trích dẫn thật** từ nguồn uy tín, `cite` trỏ tới
**URL nguồn gốc thật** đã mở được.

**Dự án không áp dụng:** nhét từ khóa vào thuộc tính `class`, và dùng link rút gọn để tạo đa dạng
referring domain.

Lý do: phần sau là hành vi tạo liên kết nhân tạo, thuộc nhóm bị chính sách link spam của Google
nhắm tới. Với nội dung YMYL bất động sản, rủi ro đó không đáng đánh đổi. Phần trích dẫn thật thì
vừa hợp chuẩn vừa trùng với quy tắc dẫn nguồn sẵn có của dự án.

### B3. Từ khóa chính trong sub-heading

**File gốc** mâu thuẫn nội bộ: sheet *Basic onpage* nói *"bắt buộc có một từ khóa trong heading 2"*,
sheet *1. Onpage* nói *"không được dùng từ khóa chính chèn trong các thẻ heading này"*.

**Dự án chốt:** **đúng một** mục nhận câu hỏi chính (quy tắc đã có ở `docs/02`), và nhận bằng
**cách diễn đạt tự nhiên của câu hỏi**, không cần lặp nguyên văn cụm từ khóa. Các heading còn lại
dùng từ khóa phụ và semantic. Nếu cụm từ khóa chính xuất hiện nguyên văn ở **từ hai sub-heading trở
lên** → `WARN` quá tối ưu.

Cách này thỏa cả hai vế của file gốc và không phá quy tắc trọng tâm đã có.

### B4. Alt ảnh đầu tiên

**File gốc:** *"Chèn từ khóa chính xác muốn SEO vào ảnh đầu tiên"*.

**Dự án áp dụng** nhưng giữ nguyên ràng buộc cũ: alt **vẫn phải mô tả đúng nội dung ảnh**. Một alt
chứa từ khóa nhưng không mô tả ảnh là hỏng cả khả năng tiếp cận lẫn mục đích của thuộc tính alt.
Nhồi từ khóa vào alt vẫn `BLOCK`.

---

## C. Không áp dụng

| Mục trong file | Vì sao không áp dụng |
|---|---|
| Fake IP bằng Zenmate để xem SERP US | Không cần thiết cho nội dung tiếng Việt phục vụ người đọc Việt Nam. Mục đích thật của bước này là tìm nguồn tiếng Anh uy tín; với bất động sản Việt Nam thì nguồn mạnh nhất là văn bản pháp luật và cổng thông tin trong nước (`docs/04`) |
| `#keywords` nhồi tối đa 3 từ khóa vào anchor của TOC | Giữ TOC với anchor mô tả đúng heading. Nhồi từ khóa vào fragment là tối ưu cho máy, không cho người |
| Chuẩn Title/Meta của sheet *draf1* (`[Mã] \| [Key] \| [Brand]`, mô tả ≤140 ký tự, bảng thông số, bảng báo giá) | Đó là chuẩn cho **trang sản phẩm nội thất**, không phải bài blog bất động sản. Ghi lại để dùng nếu sau này làm trang sản phẩm |
| Surfer SEO (`words in body`, `exact keywords in h2 to h6`...) | Dự án không có license Surfer. Phần đo được thì đã thay bằng đối chiếu trực tiếp với top 5 trong `serp_outline.py`. Nếu sau này có Surfer, các chỉ số này bổ sung vào `competitors.json` |
| Làm sạch code HTML, gỡ CSS inline, `<p>` bao nội dung | Thuộc khâu đưa lên CMS, nằm ngoài phạm vi dự án này (dự án dừng ở Markdown), và **chính blog cũng chưa đạt** — trung vị 67 thuộc tính `style=` và 101 thẻ `<span>` mỗi bài. Đã ghi vào gói bàn giao. Phần thuộc dự án thì nay có máy kiểm: xem E2 |
| AMP, page speed, TTFB, UX/UI | Kỹ thuật website, không phải on-page của một bài viết |

---

## D. Chạy kiểm

```powershell
python scripts/onpage_check.py work/<slug>/article.md --brief work/<slug>/brief.yaml
# tu tim evidence-ledger.csv cung thu muc de doi chieu mien link ngoai; --ledger de chi duong khac
python scripts/serp_outline.py check work/<slug>/outline.md      # số heading so với top 3
python scripts/run_qa.py work/<slug>/article.md                  # chạy tất cả
```

Các ngưỡng nằm ở đầu `scripts/onpage_check.py`, sửa được. Sửa xong nhớ chạy lại hai fixture trong
`examples/` để chắc bộ kiểm còn phân biệt được bài dở với bài tốt.

---

## E. Tab "Kĩ thuật SEO" — năm công đoạn, đối chiếu từng mục

Tab này mô tả việc của **người làm kĩ thuật SEO**, không phải việc của người viết, nên phần lớn nói
về Ahrefs, Search Console và thao tác trong CMS. Vì vậy mỗi mục dưới đây được xếp vào đúng một
trong ba chỗ: **máy dự án kiểm được**, **ghi vào gói bàn giao cho người đăng bài**, hoặc **không
áp dụng** kèm lý do.

Ba nhóm số đo dưới đây lấy từ **HTML thô của 24 bài thật** (tải ngày 2026-09-23), không lấy từ bản
markdown trong `reference/muaban-blog/` — bản đó đã lọc bỏ thẻ và liên kết, nên không đo được
schema hay outlink. Đây cũng là bài học đã ghi ở cuối tài liệu này: muốn biết blog làm gì thì phải
đếm trên HTML.

### E1. Công đoạn 11 — Triển khai external link

**Đo được gì trên bài thật:** 8/24 bài có liên kết ra ngoài miền, tổng 20 liên kết.

| Số đo | Kết quả |
|---|---|
| Mở tab mới | **20/20** liên kết có `target="_blank"` |
| `nofollow` | **20/20** — 16 `rel="nofollow noopener"`, 4 `rel="sponsored nofollow noopener"` |
| Miền được trỏ tới | unica.vn 8, vi.wikipedia.org 5, thuvienphapluat.vn 3, docs.google.com 1, vanban.chinhphu.vn 1, facebook.com 1, google.com 1 |
| Vị trí trong thân bài | 0,06–0,94 chiều dài thân bài, trung vị 0,45 |

Bốn điều chốt từ đó:

1. **Hai loại link out, không phải một.** Sheet đòi "link out định nghĩa" đặt ngay trong câu đang
   nói về khái niệm đó (anchor là từ khóa semantic) **và** "link out tham khảo" ở cuối bài. Số đo
   đỡ đúng điều này: bài thật rải liên kết khắp thân bài, không dồn hết xuống đáy. Dự án đã có khối
   "Căn cứ" cuối bài từ đầu, nên phần còn thiếu là link trong thân bài — `onpage_check` nay `WARN`
   khi mọi liên kết ngoài đều nằm trong khối cuối. Cách làm khớp sẵn với quy tắc 16b: bài nêu tên
   văn bản ngay trong câu, thì gắn liên kết vào chính tên đó.
2. **"DR ≥ 20" đổi thành một điều kiện đo được.** Dự án không có Ahrefs, và **bịa một con số DR là
   vi phạm quy tắc 1**. Thay bằng: miền của liên kết ngoài phải có mặt trong `evidence-ledger.csv`,
   tức đã đi qua thứ tự ưu tiên nguồn ở `docs/04`. Không có trong ledger thì `WARN` — thêm dòng
   ledger cho nguồn đó, hoặc bỏ liên kết.
3. **`target="_blank"` và `nofollow` là việc của người đăng bài.** Markdown không mang được hai
   thuộc tính này, nên chúng nằm trong gói bàn giao (`docs/07`), không phải trong `article.md`.
   Bài thật `nofollow` **toàn bộ** liên kết ngoài, không chỉ trang trust thấp — nên hướng dẫn bàn
   giao ghi đúng như vậy, và liên kết tài trợ thì `rel="sponsored nofollow noopener"`.
4. **Wikipedia: được làm link out định nghĩa, không được làm nguồn cho claim.** Sheet khuyên dùng
   `keyword + wiki` để lấy liên kết định nghĩa, và 5 bài thật làm đúng thế. Nhưng `docs/04` không
   nhận trang tổng hợp làm nguồn, nên một `source_url` trỏ tới Wikipedia trong ledger là `WARN`:
   claim phải quay về văn bản gốc. Hai việc này khác nhau và đừng lẫn — và cũng đừng lẫn với quy
   tắc 12, vốn nói về thư mục `wiki/` nội bộ của dự án.

**Một chỗ cố ý không chỉnh theo bài thật:** 16/24 bài thật **không có liên kết ngoài nào**, nên
theo cơ chế phân xử của quy tắc 16 thì ngưỡng "phải có ít nhất một liên kết nguồn" đang bắt oan
hai phần ba kho bài. Ngưỡng này **vẫn giữ**, vì nó tồn tại để đỡ quy tắc 1 và quy tắc 2 — mọi claim
vật chất phải có nguồn — chứ không phải là một quy tắc văn phong thừa hưởng từ tài liệu tiếng Anh.
Quy tắc 16 đã nói rõ cơ chế đó không áp cho nhóm này.

### E2. Công đoạn 12 — Tối ưu HTML code (làm sạch code)

Sheet đòi content sạch CSS inline, chỉ dùng HTML5, và nội dung nằm trong thẻ `<p>`.

**Đo trên bài thật: chính blog chưa đạt.** Trung vị **67** thuộc tính `style=` và **101** thẻ
`<span>` trong mỗi thân bài, do trình soạn thảo WordPress sinh ra. Đây là lý do công đoạn này tồn
tại, và cũng là lý do nó là **việc của khâu CMS** chứ không phải của người viết.

Phần thuộc phạm vi dự án thì nay có máy kiểm: `article.md` phải là **Markdown thuần**. Thẻ trang
trí (`<span>`, `<font>`, `<center>`, `<b>`, `<i>`, `<small>`) và thuộc tính `style=` đều `WARN`.
Giữ bản thảo sạch từ đầu thì khi dán lên CMS content mới nằm gọn trong `<p>`. Ngoại lệ đã có từ
trước: `<blockquote cite="...">` cho trích dẫn thật (mục B2).

### E3. Công đoạn 13 — Triển khai tối ưu schema

**Đo JSON-LD trên 24 bài thật:**

| Loại schema | Số bài có |
|---|---|
| `BlogPosting`, `BreadcrumbList`, `ImageObject`, `WebPage`, `WebSite`, `Person`, `ListItem` | **24/24** |
| `FAQPage` + `Question` + `Answer` | 9/24 — đúng những bài có mục hỏi đáp thật |
| `VideoObject` | 0/24 |
| Schema cho mục lục | 0/24 |

Từ đó `onpage_check.check_schema` chốt như sau:

| Tình huống | Mức | Vì sao |
|---|---|---|
| Front matter không khai schema nào | `WARN` | 24/24 bài thật có khai |
| Khai `Article` thay vì `BlogPosting` | `WARN` | 24/24 bài dùng `BlogPosting` làm `mainEntityOfPage` |
| Thiếu `BreadcrumbList` | `WARN` | 24/24 bài có |
| Bài có ảnh mà không khai `ImageObject` | `WARN` | 24/24 bài khai cho ảnh đại diện |
| Bài có mục hỏi đáp mà không khai `FAQPage` | `WARN` | 9/9 bài có hỏi đáp đều khai |
| **Khai `FAQPage` mà bài không có mục hỏi đáp** | `BLOCK` | luật trung tâm của sheet |
| **Khai `ImageObject` mà bài không có ảnh** | `BLOCK` | như trên |
| **Khai `VideoObject` mà bài không nhúng video** | `BLOCK` | như trên |

Vế "khai báo gì thì bài phải có thứ đó" nghiêm hơn vế còn lại vì nó **cùng hướng với quy tắc 1**:
khai một thứ bài không có là nói sai về chính bài viết, và Google xử lý phần này bằng án thủ công
chứ không phải hạ thứ hạng nhẹ.

**Ba mục của sheet không áp dụng, kèm lý do:**

- **Schema TOC** — 0/24 bài thật có, và format hệ Blog Muaban.net đã bỏ mục lục (quy tắc 14). Không
  có mục lục thì không có gì để khai.
- **`sameAs`, `additionalType`, `isSimilarTo`, `isRelatedTo`** — sheet gọi đây là phần khó nhất.
  Chúng là khai báo **cấp website và cấp trang sản phẩm**, không phải cấp một bài blog: `sameAs`
  cần các profile chính thức của thương hiệu, `isSimilarTo` cần danh mục sản phẩm. Người làm kĩ
  thuật SEO của Muaban.net giữ phần này; agent không tự khai vì khai sai một URL profile là bịa đặt.
- **Ba dạng `Product category`, `Product`, `Service`** — dự án chỉ viết bài blog. Ghi lại để dùng
  nếu sau này làm trang sản phẩm hoặc trang dịch vụ.

### E4. Công đoạn 1 — Triển khai Content Gap

Cần Ahrefs hoặc Search Console, và **chỉ áp dụng khi bài đã trên 3 tháng và đã vào top 10–20**.
Dự án không có license Ahrefs, còn Search Console thì thuộc người quản trị site. Vì vậy đây là
**bước làm mới sau khi bài đã chạy**, không phải bước viết.

Việc bắt buộc của người viết chỉ có hai dòng, và cả hai đều nằm trong gói bàn giao:

- `review_after` trong front matter — `evidence_check` đã kiểm ngày này.
- Ngày sớm nhất được rà Content Gap = **ngày đăng + 3 tháng**, ghi trong `qa-report.md`. Không có
  ngày đăng lúc bàn giao thì ghi "ngày đăng + 3 tháng" đúng như vậy, đừng đoán một ngày cụ thể.

Khi rà, bổ sung theo truy vấn thật người dùng đã dùng để tới trang, và nếu phải thêm nội dung thì
quay lại quy trình bình thường: sửa outline, lên cổng duyệt, viết. Không chèn từ khóa rời vào bài
cũ — đó là cách nhanh nhất phá `human_voice_check`.

### E5. Công đoạn 2 — On-page nâng cao cho URL quan trọng

Sheet nói thẳng: *"thông thường bạn nên hỏi Manager vì nó sẽ đi theo chiến lược tổng"*. Dự án giữ
đúng tinh thần đó — sáu mục dưới đây không mục nào là việc agent tự quyết:

| Mục | Xếp ở đâu |
|---|---|
| `Schema potentialAction`, schema webpage stacking thành entity tổng | Chiến lược cấp website, người quản trị site quyết. Agent không khai (E3) |
| AMP, page speed, TTFB | Kỹ thuật website, không phải on-page của một bài |
| Tối ưu UX/UI | Như trên |
| **Featured Snippet** | Thuộc nội dung, và dự án đã có: đúng một mục nhận câu hỏi chính và mục đó đứng đầu (quy tắc 7), sapo trả lời thẳng. Số đo đoạn trả lời đầu tiên sau mục I trên 24 bài thật: **22–92 từ, p10 31, trung vị 68,5, p90 91**. Tài liệu SEO phổ thông khuyên 40–60 từ cho snippet dạng đoạn; dải của blog rộng hơn, nên đây là **mốc biên tập**, không phải cổng chặn |
| **Mật độ từ khóa cụ thể** | Đã xử lý ở mục B1: đo và đối chiếu với top, không đặt làm mục tiêu số |
