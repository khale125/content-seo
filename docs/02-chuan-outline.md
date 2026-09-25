# 02 — Chuẩn outline

Outline là nơi rẻ nhất để sửa sai. Một outline tốt phải nhìn vào là biết bài sẽ trả lời gì,
bằng nguồn nào, và chỗ nào còn thiếu bằng chứng — **trước khi** viết một câu nào.

## Nguyên tắc dựng sườn

### Một mục phải nhận câu hỏi chính

Trước mọi thứ khác: **đúng một mục trong bài phải trả lời thẳng truy vấn chính, và mục đó đứng đầu.**

Nếu truy vấn là *"chuyển đất nông nghiệp lên thổ cư mất bao nhiêu tiền"*, phải có một mục nhận
đúng câu đó. Một sườn bài gồm *"Tiền sử dụng đất được tính thế nào"*, *"Các yếu tố ảnh hưởng"*,
*"Thủ tục gồm những bước nào"* nghe rất hợp lý nhưng **không mục nào trả lời câu người ta gõ vào ô
tìm kiếm**. Bài đó sẽ lan man dù từng mục đều đúng.

Đây là hai lỗi ngược nhau, và né lỗi này quá tay sẽ rơi thẳng vào lỗi kia:

| Lỗi | Biểu hiện | Hậu quả |
|---|---|---|
| Nhồi từ khóa | Nhiều mục cùng chứa truy vấn chính | Spam, Google đọc được, người đọc cũng thấy |
| **Lệch trọng tâm** | **Không mục nào nhận truy vấn chính** | **Bài không trả lời đúng việc, mất thứ hạng lẫn người đọc** |

Quy tắc cân bằng: **đúng một mục nhận, các mục còn lại không lặp lại.**

Mục nhận câu hỏi chính nên viết gần nguyên văn cách người đọc hỏi — kể cả khi trông "giống từ khóa".
Một lần là câu hỏi thật; lặp lại nhiều lần mới là nhồi.

`scripts/outline_check.py` chặn ở mức `BLOCK` khi không mục nào phủ được từ 60% số từ mang nghĩa
của truy vấn chính, và cảnh báo khi mục nhận nó không đứng đầu.

### Bốn quy tắc dựng sườn từ top 5

Outline **phải được tổng hợp từ bài của top 5 đang xếp hạng**, không dựng bằng cảm tính.

**1. Đọc top 5, không đọc qua loa.** Mở thật từng kết quả, chép danh sách heading vào
`competitors.json`. Trang nào chặn truy cập thì ghi vào `not_captured` kèm lý do — đừng bỏ im lặng,
vì nó làm cỡ mẫu nhỏ đi. Kết quả từ vị trí 6 trở xuống **không tính vào mức sàn**: một trang xếp
dưới top 5 không phải bằng chứng về thứ Google đang thưởng.

**2. Đối thủ có thì mình phải có.** Mọi chủ đề xuất hiện trong top 5 đều phải có mục trả lời.
Thiếu là `BLOCK`. Muốn bỏ một chủ đề thì **phải khai báo** vào mục
`## Chủ đề đã cân nhắc và không đưa vào` kèm lý do cụ thể — bỏ im lặng không được chấp nhận, vì
người duyệt cần nhìn thấy quyết định đó.

**3. Phải có điểm khác biệt.** Ít nhất một mục mà không kết quả nào trong top 5 có. Không có thì
`BLOCK`: phủ đủ chủ đề của họ mà không thêm gì thì bài chỉ là bản sao tốt hơn chút ít, không đủ
lý do để Google xếp trên.

**4. Heading viết rõ ý, không trùng câu chữ.** Cùng chủ đề với đối thủ thì được — cùng câu chữ là
đạo văn. Trùng nguyên văn là `BLOCK`; gần trùng là `WARN`. Heading dưới 3 từ mang nghĩa bị cảnh báo
là chưa rõ ý: *"Tiền sử dụng đất"* là cụm danh từ, *"Tiền sử dụng đất tính theo mấy bậc"* mới là
một câu hỏi.

> Bốn quy tắc này kéo nhau: quy tắc 2 đẩy bài rộng ra, quy tắc 4 buộc phải diễn đạt lại, quy tắc 3
> đảm bảo bài không thành bản sao. Nhưng chúng **không** ghi đè quy tắc cắt: mục không có
> `source_ids` và không phải hướng dẫn thao tác vẫn phải cắt. Nếu một chủ đề của top không có bằng
> chứng để viết, hãy khai báo bỏ kèm lý do — đừng viết bừa cho đủ.

```powershell
copy templates\competitors.json work\<slug>\
python scripts/serp_outline.py analyze work/<slug>/competitors.json   # top phục vụ chủ đề nào
python scripts/serp_outline.py check   work/<slug>/outline.md         # đã phủ đủ chưa
```

### Sườn bám câu hỏi, không bám từ khóa

Sai — nhồi từ khóa:
```
H2: Thủ tục sang tên sổ đỏ
H2: Thủ tục sang tên sổ đỏ mới nhất
H2: Hồ sơ thủ tục sang tên sổ đỏ gồm những gì
```
Ba heading này là một heading bị lặp ba lần để nhét từ khóa.

Cũng sai — lệch trọng tâm (truy vấn: *"thủ tục sang tên sổ đỏ"*):
```
H2: Sổ đỏ là gì
H2: Các yếu tố ảnh hưởng tới thời gian xử lý
H2: Những lưu ý khi giao dịch nhà đất
```
Không heading nào nhận câu hỏi. Từng mục đều hợp lý, cộng lại thành bài lan man.

Đúng:
```
H2: Thủ tục sang tên sổ đỏ gồm những bước nào     ← nhận câu hỏi chính, đứng đầu
H2: Cần chuẩn bị giấy tờ gì
H2: Nộp ở đâu và mất bao lâu
H2: Các khoản phải đóng và ai đóng
H2: Ba tình huống dễ bị trả hồ sơ
```
Mục đầu nhận câu hỏi chính; các mục sau là câu hỏi tiếp theo và không lặp lại truy vấn.

### Trả lời trước, giải thích sau

Nguyên tắc này áp dụng ở hai cấp: **sapo** trả lời trước phần thân, và **mục đầu tiên** trả lời
trước các mục sau. Điều kiện, bối cảnh, các yếu tố ảnh hưởng đều là phần giải thích — chúng đi sau.

Đoạn mở phải chứa câu trả lời trực tiếp cho truy vấn chính trong 2–4 câu. Không "dẫn dắt".
Người đọc và các hệ thống trích dẫn (AI Overviews, đoạn trích nổi bật) đều lấy phần này.

Nếu câu trả lời phụ thuộc điều kiện, nói luôn điều kiện: *"Nếu nhà đã có sổ hồng riêng, hồ sơ gồm 5 loại
giấy tờ và mất 10–15 ngày làm việc. Nếu đang thế chấp ngân hàng, phải giải chấp trước và thời gian
dài hơn."*

### Độ dài do nội dung quyết định

Không đặt mục tiêu số chữ trước. Ước lượng độ dài từ số câu hỏi phải trả lời và lượng dữ liệu có thật.
Nếu bằng chứng chỉ đủ cho 900 chữ thì viết 900 chữ. Kéo dài bằng câu chung chung là cách chắc chắn
nhất để bài nghe như máy viết.

### Mỗi H2 phải khai báo bằng chứng

Trong outline, dưới mỗi H2 ghi rõ `claims` và `source_ids` trỏ về `evidence-ledger.csv`.
H2 nào không có `source_ids` và cũng không phải phần tổng hợp/hướng dẫn thao tác → **cắt H2 đó**.
`outline_check.py` chỉ **cảnh báo** (`WARN`) chứ không chặn; quyết định cắt là của bạn.

## Cấu trúc chuẩn theo loại bài

Chọn đúng một mẫu theo intent đã chốt ở bước 01.

### A. Thủ tục / pháp lý (intent: cách làm)

```
Sapo (2-4 câu): trả lời thẳng + phạm vi áp dụng + mốc thời gian hiệu lực
[Hộp tóm tắt]: hồ sơ / nơi nộp / thời gian / chi phí — dạng bảng
H2 Điều kiện áp dụng và trường hợp ngoại lệ
H2 Hồ sơ cần chuẩn bị          → liệt kê có số lượng bản, bản chính/sao
H2 Quy trình từng bước          → đánh số, mỗi bước có nơi thực hiện + thời gian
H2 Chi phí và ai chịu
H2 Những lỗi khiến hồ sơ bị trả lại
H2 Câu hỏi thường gặp           → chỉ câu hỏi thật có người hỏi
[Khối minh bạch]: căn cứ pháp lý + ngày cập nhật + khuyến nghị tham vấn
```

### B. So sánh / quyết định (intent: có nên)

```
Sapo: kết luận ngắn kèm điều kiện ("nên nếu ..., không nên nếu ...")
[Bảng]: tiêu chí × phương án
H2 Các tiêu chí thật sự tạo khác biệt
H2 Phương án A hợp với ai — kèm đánh đổi
H2 Phương án B hợp với ai — kèm đánh đổi
H2 Rủi ro hay bị bỏ qua
H2 Cách tự kiểm tra trước khi quyết
[Khối minh bạch]: giả định, mốc dữ liệu, giới hạn
```

### C. Khu vực / giá / thị trường (intent: tra cứu dữ liệu)

```
Sapo: con số chính + kỳ dữ liệu + nguồn
[Bảng dữ liệu]: có cột "kỳ" và "nguồn" ngay trong bảng
H2 Dữ liệu nói gì               → chỉ mô tả, chưa diễn giải
H2 Vì sao có mức đó              → diễn giải, đánh dấu rõ là nhận định
H2 Ý nghĩa với người mua / người thuê / người bán
H2 Điều cần kiểm chứng thêm trước khi xuống tiền
[Ghi chú phương pháp]: dữ liệu lấy từ đâu, khoảng thời gian, cỡ mẫu, hạn chế
```

> Với dữ liệu tin đăng Muaban.net: đó là **giá chào**, không phải giá giao dịch. Bắt buộc ghi rõ
> điều này, kèm số lượng tin và khoảng thời gian. Không gọi giá chào là "giá thị trường".

### D. Khái niệm (intent: là gì)

```
Sapo: định nghĩa một câu, đúng theo cách dùng phổ thông + cách dùng pháp lý nếu khác nhau
H2 Phân biệt với khái niệm hay bị nhầm   → bảng
H2 Gặp trong tình huống nào
H2 Ảnh hưởng gì tới giao dịch
H2 Câu hỏi thường gặp
```

## Những thứ KHÔNG đưa vào outline

- **FAQ lấp chỗ trống.** Chỉ thêm FAQ khi có câu hỏi thật quan sát được (Mọi người cũng hỏi,
  diễn đàn, câu hỏi khách hàng). Không tự nghĩ ra câu hỏi để có thêm mục.
- **Mục "Kết luận" / "Tổng kết" / "Tóm lại" tóm tắt lại bài.** Người đọc vừa đọc xong, không cần
  đọc lại. Thay bằng **bước tiếp theo cụ thể** hoặc **checklist tự kiểm**.
  Ngoại lệ đã thống nhất: **"Lời kết"** là mục bắt buộc của format hệ Blog Muaban.net — xem mục
  "Format outline của hệ Blog Muaban.net" bên dưới. Nó không phải phần tóm tắt.
- **Mục "Lời mở đầu" / "Tổng quan".** Sapo đã làm việc đó.
- **Heading chỉ để nhét từ khóa.**
- **Số lượng bullet cố định.** Đừng ép mọi mục có đúng 3 gạch đầu dòng — đó là dấu vết máy rõ nhất.

## Format outline của hệ Blog Muaban.net

Nguồn: sheet **"Format Outline hệ Blog"** trên Lark Wiki, dòng *Muaban.net và Vieclam.net*.
Sheet có hai dòng; dòng *Mogi.vn* dùng quy ước khác (sapo không để H2, heading không đánh số) và
**không áp dụng** cho dự án này.

### Bốn thứ bắt buộc

| Thứ | Quy định | Máy kiểm |
|---|---|---|
| `Title:` và `H1:` | Hai dòng mở đầu outline, trước cả dòng liên hệ | `outline_check` → WARN |
| Dòng liên hệ | `Mọi thắc mắc liên hệ người lên outline <tên>` ngay sau H1 | `outline_check` → WARN |
| Sapo | Đặt ở mức **H2**, 3–5 câu, chứa keyword chính, chèn keyword phụ nếu vào tự nhiên | `outline_check` → WARN |
| Đánh số | Mục chính số La Mã (`I.`, `II.`), mục con số Ả Rập (`1.`, `2.`) | `outline_check` → WARN |
| Lời kết | Mục cuối cùng, có kêu gọi hành động | `outline_check` → WARN |

Bốn thứ này ở mức `WARN` chứ không phải `BLOCK`: đây là quy ước trình bày của tòa soạn, không phải
ràng buộc nội dung. Một outline sai format vẫn có thể đúng về chất; ngược lại thì không.

**Bài viết giữ nguyên cấu trúc này, không chỉ outline** (CLAUDE.md quy tắc 14). `onpage_check.py`
kiểm phía bài bằng `check_house_format`: có một H2 đứng trước toàn bộ mục chính, mục chính ở H3 đánh
số La Mã, mục con ở H4 đánh số Ả Rập, và `Lời kết` là mục cuối. Hàm này **không** đòi tiêu đề H2 phải
là chữ "Sapo" — tòa soạn tự đặt tên đọc được cho người đọc.

Hai chỗ bộ kiểm đã nhường format nhà, vì nếu không thì mọi bài đúng chuẩn đều bị cảnh báo oan:

- **Mục lục:** `docs/10` mục A6 khuyến nghị bài trên 1.200 chữ có TOC. Format hệ Blog không có mục
  lục — các mục đánh số La Mã đã làm việc đó. Bài có mục chính đánh số thì `onpage_check` bỏ qua
  cảnh báo TOC.
- **Mục đầu tiên:** kiểm trọng tâm trước đây đo "H2 đầu tiên". Với format này H2 đầu luôn là sapo,
  nên nó đo mục La Mã đầu tiên.

### Ba chỗ đã điều chỉnh so với sheet — và vì sao

**1. "Lời kết" không phải phần tóm tắt.**
Sheet ghi: *"Tóm tắt ngắn gọn bài viết nói về cái gì? Mong muốn của người viết. Call to action"*.
Dự án giữ **vế hai và vế ba**, bỏ vế một. Lý do: mục "Kết luận tóm tắt lại bài" là thứ `docs/02`
cấm từ đầu, và cấm có căn cứ — người đọc vừa đọc xong. Nhưng mong muốn của người viết và CTA thì
không phải tóm tắt, chúng là thứ mới. Giữ tên **"Lời kết"** theo đúng format, đổi ruột.

**2. Tên người lên outline phải là người có thật.**
Sheet để `"Tên người lên outline"`. Agent **không được bịa tên người** (CLAUDE.md quy tắc 1 và 3).
Khi agent dựng outline, ghi định danh thật của nó — ví dụ `content-seo agent` — rồi người duyệt đổi
lại thành tên mình nếu muốn nhận trách nhiệm. Một cái tên bịa làm CTV gửi câu hỏi vào hư không.

**3. CTA chọn một, không gom cả ba.**
Sheet liệt kê *"bình luận, hoặc chia sẻ bài viết, xem thêm tại Muabannet/Vieclamnet"*. Dự án chọn
**đúng một** CTA, khớp với việc người đọc vừa làm xong. Gom cả ba vào cuối bài là mẫu câu kết máy
viết, đúng thứ `human_voice_check.py` tồn tại để bắt. CTA cũng không được hứa hẹn kết quả
(CLAUDE.md quy tắc 4).

### Ánh xạ sang cấu trúc file

Sheet mô tả outline dưới dạng liệt kê `H1:`, `H2:`, `H3: I.`. File `templates/outline.md` của dự án
giữ khung máy đọc được (`## Sườn bài` rồi mỗi mục một `### `), vì ba script phụ thuộc vào nó. Ánh xạ:

| Trong sheet | Trong `outline.md` |
|---|---|
| `Title:` / `H1:` | hai dòng thường ở đầu file |
| `H2: Sapo` | `## Sapo (2–4 câu)` |
| `H3: I.` | `### I. <tiêu đề mục>` |
| `H4: 1.` | `#### 1. <ý triển khai>` |
| `Lời kết` | `### Lời kết` |

Mục con (`H4`) **không cần** `source_ids` riêng — bằng chứng khai ở mục chính chứa nó.

## Kế hoạch liên kết và hình ảnh (nằm trong outline, không để sau)

- **Internal link:** tối thiểu 1 liên kết tới danh mục/tin đăng Muaban.net đúng địa bàn và đúng loại
  hình, đặt ở chỗ người đọc thật sự cần chuyển tiếp. Anchor mô tả nội dung đích, không dùng
  "tại đây", "xem thêm".
- **External link:** tối thiểu 1 nguồn gốc (cổng thông tin chính phủ, văn bản pháp luật, cơ quan
  thống kê, báo cáo có phương pháp) cho bài có dữ liệu. HTTPS, mở tab mới, `rel="noopener"`.
- **Hình:** ghi mục đích từng ảnh. Ảnh minh họa chung chung không giải thích gì thì bỏ.
  Biểu đồ/bảng tự dựng từ dữ liệu có nguồn thì giữ. Mọi ảnh phải có bản quyền rõ ràng —
  không hotlink, không lấy ảnh báo/đối thủ.

## Kiểm outline trước khi đưa lên duyệt

```powershell
python scripts/outline_check.py work/<slug>/outline.md
python scripts/serp_outline.py check work/<slug>/outline.md
```

`outline_check.py` kiểm sáu thứ nhưng chỉ **chặn** hai: không mục nào nhận câu hỏi chính, và truy
vấn bị nhồi vào quá nhiều mục. Bốn thứ còn lại chỉ **cảnh báo** — mục nhận không đứng đầu, câu hỏi
trong brief chưa có mục nhận, mục thiếu `source_ids`, có mục "Kết luận", thiếu ước lượng độ dài.

`serp_outline.py check` **chặn** khi thiếu chủ đề top có mà không khai báo lý do, khi không có mục
nào khác biệt, và khi heading trùng **nguyên văn** heading đối thủ. Heading gần trùng chỉ cảnh báo.

**Lưu ý về cấp heading:** trong `outline.md`, mỗi mục viết bằng `###` nằm dưới `## Sườn bài` — đó là
thứ hai script đọc. Tài liệu này gọi chúng là "H2" theo cấp chúng sẽ có trong **bài đã xuất bản**,
không phải cấp trong file outline. Viết mục bằng `##` sẽ khiến máy không tìm thấy mục nào và báo
`BLOCK`.

Sửa hết `BLOCK` trước khi đẩy lên Lark. Bắt lỗi ở outline tốn một phút; phát hiện cùng lỗi đó
sau khi đã viết 1.500 chữ tốn cả buổi.

## Đầu ra

`work/<slug>/outline.md` theo `templates/outline.md` (đã gồm link map và image plan), kèm
`evidence-ledger.csv` đã điền — kể cả các dòng `GAP`.

Đẩy lên Lark rồi **dừng**:

```powershell
python scripts/lark/lark_sync.py push work/<slug>
```

Chỉ viết bài khi `lark_sync.py gate work/<slug>` trả về exit 0 — nghĩa là trên Lark đã có
`Kết quả duyệt = Đồng ý` kèm tên người duyệt.

- **Không thêm mục lạc đề chỉ để có chỗ đặt liên kết nội bộ.** Người duyệt đã từ chối hai lần vì
  cùng một liên kết tới bài khác: lần đầu nằm trong câu dẫn giữa mục, lần sau được nâng thành hẳn
  một mục con về chủ đề lân cận — *"Tại sao lại có đoạn này trong bài chuồn chuồn"*. Liên kết nội bộ
  phải nằm trong mục vốn đã thuộc về bài, hoặc ở câu kết bài theo khuôn tòa soạn.
- **Mọi mục chính phải mang từ khóa chính hoặc từ khóa phụ.** Tiêu đề phải cho biết mục đó nói về
  cái gì — "Vì sao chúng tìm tới nơi bạn ở" thì cả người đọc lẫn Google đều không biết "chúng" là
  con gì. Quy tắc này và quy tắc "đúng một mục nhận truy vấn chính" **không mâu thuẫn**: một mục
  chứa nguyên văn cụm từ khóa, các mục còn lại dùng từ khóa phụ hoặc một phần của cụm.
  `outline_check.py` cảnh báo mục nào không mang từ khóa nào; từ vựng đối chiếu lấy từ
  `primary_query`, `entities` và `same_page_variants` của brief, nên brief càng đầy thì kiểm càng
  chặt. Quy tắc sinh ra từ một lần bị từ chối thật ở cổng duyệt outline ngày 24/09/2026, khi agent
  cắt hết từ khóa khỏi tiêu đề chỉ để né cổng máy phía trên.
