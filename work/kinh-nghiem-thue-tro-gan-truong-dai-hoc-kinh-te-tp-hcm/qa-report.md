# Báo cáo QA — 001 · kinh-nghiem-thue-tro-gan-truong-dai-hoc-kinh-te-tp-hcm

Bản 0.1.10 · lập ngày 18/09/2026, sửa ngày 23/09/2026 theo quy tắc 17 và 18, và theo hai lượt góp ý từ chối

## 1. Máy kiểm

```
python scripts/run_qa.py work/<slug>/article.md
→ PASS · BLOCK=0 · WARN=10 · 1.923 chữ thân bài (9 cảnh báo ledger cùng một lỗi, xem mục 2; cảnh báo thứ 10 là bài chưa có ảnh, xem mục 6)
python scripts/house_voice_check.py work/<slug>/article.md
→ 0 chỉ số lệch trên 18 (kho 24 bài thật: lệch trung vị 4, nhiều nhất 9)
python scripts/outline_check.py / serp_outline.py check
→ 0 BLOCK, 1 WARN (ít mục hơn top 3 — hệ quả trực tiếp của việc gộp mục, xem mục 2)
```

Bằng chứng: **9 VERIFIED · 0 PARTIAL · 4 GAP**. 0 số liệu không có chỗ dựa. Đủ 4/4 tín hiệu YMYL.

## 1b. Đã sửa gì theo góp ý từ chối (bản 0.1.3 → 0.1.4)

Người duyệt **Khá** từ chối bản 0.1.3 với hai góp ý. Cả hai đã xử lý:

**(1) "Sửa lại title và metades cho thu hút hơn (tham khảo đối thủ)"**

| | Bản 0.1.3 | Bản 0.1.4 |
|---|---|---|
| Title | "Kinh nghiệm thuê trọ gần Đại học Kinh tế TPHCM theo cơ sở" (57 ký tự) | "Kinh nghiệm thuê trọ gần Đại học Kinh tế TPHCM cho tân sinh viên" (64 ký tự) |
| Meta | 158 ký tự, mở bằng dữ kiện | 160 ký tự, mở bằng con số 10 cơ sở, đóng bằng lời kêu gọi |

Đã đọc title của top 5: họ dùng **nhóm người đọc** ("cho tân sinh viên" — kết quả #3 và #4) và **tên viết tắt trường** ("(UEH)", "(IUH)", "(HCMUE)"). Bài lấy cụm "cho tân sinh viên" vì đó đúng là người đọc của bài. Không lấy "(UEH)" vì title sẽ thành 69 ký tự, vượt dải 40–65 của máy kiểm.

**Một thứ cố ý không lấy:** khuôn title của blog nhà là *"...giá tốt"*, *"...giá rẻ, hạn chế rủi ro"* — xem `kinh-nghiem-thue-tro-gan-truong-dai-hoc-su-pham-ky-thuat-tphcm`. Bài này **không có một con số giá nào** (`C10` là `GAP`), nên hứa "giá tốt" ngay ở title là title không mô tả đúng nội dung, vi phạm quy tắc 4. Nếu chấp nhận đếm tin đăng thật để có khoảng giá (câu hỏi mở số 2) thì title dùng được khuôn đó.

**(2) "Gom nội dung phần II và III để tránh bị nói dài dòng lan man"**

Đúng là trùng: mục II (cơ sở nào, ở đâu) và mục III (khoanh vùng trọ) **chia theo cùng bốn nhóm cơ sở**, nên người đọc phải đi qua cùng một cách phân nhóm hai lần — 294 chữ rồi lại 335 chữ. Đã gộp thành một mục **II. Mười cơ sở của UEH nằm ở đâu và nên khoanh vùng trọ ở đâu**, bốn mục con, mỗi mục con nêu địa chỉ rồi nói luôn vùng nên tìm.

- **Không mất dữ kiện nào:** đủ 10 địa chỉ cơ sở và đủ bốn vùng gợi ý. Ledger không đổi.
- Các mục sau dồn số La Mã lên một bậc (IV→III, …, VIII→VII), và ba chỗ tham chiếu trong bài đã sửa theo.
- **`outline.md` đã sửa theo**, kèm dòng ghi chú lý do ngay trong mục — đổi cấu trúc so với outline đã duyệt thì phải nêu lý do.
- Thân bài giảm 110 chữ. Đây là lý do duy nhất của cảnh báo `serp` "outline có 8 mục, ít hơn top 3 (nhiều nhất 12)": gộp mục thì số mục giảm. Không thêm mục rỗng để bù cho đủ số.
- Một chủ đề của đối thủ mất chỗ khớp khi đổi tên heading ("Đại học Mở TPHCM cơ sở Nhà Bè") nên đã **khai báo lý do bỏ** vào mục "Chủ đề đã cân nhắc và không đưa vào": đó là bài cho sinh viên trường khác, UEH không có cơ sở nào ở Nhà Bè.

## 1c. Đã sửa gì theo góp ý từ chối lần hai (0.1.4 → 0.1.5)

Người duyệt từ chối bản 0.1.4: *"mô tả meta đang đọc không hiểu gì, không thu hút, không có đối thủ nào viết như vậy cả. Rule viết meta đang có vấn đề sao?"*

**Nhận xét đúng, và rule đúng là có vấn đề.** Meta cũ — *"UEH có tới 10 cơ sở nằm rải khắp TPHCM nên hai chữ gần trường mỗi người một nghĩa. Xem cách khoanh vùng trọ theo đúng cơ sở bạn học và tránh bẫy tên phường mới."* — đủ 160 ký tự và có cụm kêu gọi, nên **máy kiểm cho qua sạch**. Ba lỗi nó không nhìn thấy:

1. **Không chứa cụm "thuê trọ"** hay bất kỳ phần nào của truy vấn chính ở dạng người đọc sẽ gõ.
2. **Không nói bài trả lời những gì** — khuôn của blog luôn liệt kê 3–5 mục.
3. **Vế đầu mất nghĩa**, vì tôi bỏ dấu ngoặc kép quanh *"gần trường"* để tránh lỗi cú pháp YAML. Cách đúng là bọc cả chuỗi bằng ngoặc đơn.

Đã đo title và meta thật của 24 bài đang đăng để có khuôn:

| | Bản 0.1.4 | Bản 0.1.5 | Bài thật |
|---|---|---|---|
| Title | "…cho tân sinh viên" (64 ký tự, không số) | "…theo 10 cơ sở" (60 ký tự, có số) | 49–70, trung vị 59; 58% có chữ số |
| Meta | 160 ký tự, **6/11 từ khóa** | 149 ký tự, **11/11 từ khóa** | 116–164, trung vị 147 |
| Từ khóa trong 60 ký tự đầu | không có | có, từ ký tự đầu | 21/21 bài có từ khóa đều đặt sớm, trung vị ký tự thứ 9 |

Meta mới theo đúng khuôn `<động từ dẫn> + <truy vấn chính> + ":" + <3–5 thứ bài trả lời>`:

> *"Tổng hợp kinh nghiệm thuê trọ gần trường Đại học Kinh tế TPHCM: cách xác định đúng cơ sở mình học, khoanh vùng từng khu và lưu ý khi đọc tin đăng cũ."*

Hai chốt mới trong `onpage_check.py` sinh ra từ lần này: meta phải chứa ≥80% từ của truy vấn chính, và phải đặt nó trong 60 ký tự đầu. Cả hai đều lấy ngưỡng từ số đo, không phải nghĩ ra.

## 1d. Đã sửa gì theo quy tắc 18 (0.1.5 → 0.1.6)

Quy tắc 18 sinh ra từ tab *Kĩ thuật SEO* của file quy chuẩn. Hai chỗ của bài này không đạt, và cả
hai đều là **lỗi máy không bắt được trước đây** vì chưa có kiểm:

| Chỗ sai | Sửa thành | Vì sao |
|---|---|---|
| `schema: "Article"` | `schema: "BlogPosting"` | Đo JSON-LD của 24 bài thật: **24/24** dùng `BlogPosting` làm `mainEntityOfPage`, không bài nào dùng `Article`. `docs/10` mục A8 đã ghi đúng từ 15/09, nhưng không dòng code nào đọc trường `schema` nên bài vẫn qua sạch |
| Liên kết ngoài duy nhất nằm trong khối "Căn cứ" | Thêm link out định nghĩa vào câu mở mục II, gắn vào chính cụm "thông báo địa chỉ các cơ sở" | File quy chuẩn đòi **hai** loại link out. Bài thật rải liên kết khắp thân bài (vị trí 0,06–0,94, trung vị 0,45), không dồn hết xuống đáy |

Một chi tiết đáng ghi để lần sau khỏi mất công: lần đầu tôi đặt liên kết đó vào **sapo**, ở cụm
"Theo thông báo của UEH". Anchor dài hơn làm mệnh đề trước dấu phẩy tăng từ 5 lên 8 từ, vượt ngưỡng
đếm của `front_clause_ratio`, và bài lập tức lệch một chỉ số giọng nhà (0,500 so với trần 0,496).
Chuyển liên kết sang câu mở mục II — nơi mệnh đề đầu câu vốn đã dài — thì hết. **Chèn liên kết vào
nửa đầu một câu ngắn có thể đẩy chỉ số cú pháp qua ngưỡng**, nên chọn chỗ đặt theo câu, đừng chọn
theo thứ tự xuất hiện.

Bài không có ảnh nên **không khai `ImageObject`**, và không có mục hỏi đáp nên không khai `FAQPage` —
khai một loại mà bài không có thứ tương ứng là `BLOCK`. Khi bản đồ 10 cơ sở được dựng (câu hỏi mở
số 3) thì thêm `ImageObject` vào `schema_extra`.

## 1e. Đã sửa gì theo quy tắc heading mang từ khoá (0.1.6 → 0.1.7)

Người duyệt từ chối outline của bài 002 vì *"các heading không có từ khoá chính, từ khoá phụ"*. Góp ý
đó thành một kiểm mới trong `outline_check.py`, và kiểm đó soi ra **bài này cũng dính hai chỗ**:

| Mục | Trước | Sau |
|---|---|---|
| III | Tên phường đã đổi từ 01/7/2025 và cái bẫy khi đọc tin đăng cũ | … khi đọc tin đăng **trọ** cũ |
| V | Kiểm chất lượng và mức độ an toàn của phòng khi đi xem | … an toàn của phòng **trọ** khi đi xem |

Sửa ở cả `article.md` và `outline.md`. Thêm đúng một từ mỗi tiêu đề, không đổi nghĩa, và vẫn giữ
nguyên nguyên tắc chỉ **một** mục chứa nguyên văn cụm truy vấn chính.

## 1f. Đã sửa gì theo quy tắc sapo (0.1.7 → 0.1.8)

Người duyệt từ chối bài 002 vì sapo mang ngày cập nhật và thiếu lời mời đọc tiếp. Đo trên 24 bài
thật: **0/24 sapo có ngày**, và **13/24 kết bằng lời mời đọc tiếp**. Bài này mắc đúng lỗi đó nên
sửa luôn, không chờ bị từ chối lần nữa.

- Trước: *"Bài viết của Muaban.net giúp khoanh vùng tìm trọ theo đúng cơ sở đó, cập nhật tới
  18/09/2026."*
- Sau: *"Mời bạn cùng theo dõi bài viết dưới đây của Muaban.net để khoanh vùng tìm trọ theo đúng cơ
  sở đang học."*

Mốc dữ liệu 18/09/2026 vẫn nằm ở khối minh bạch cuối bài. Sau khi sửa, mật độ xưng hô "bạn" vọt lên
10,22 và vượt trần 10,10 của bài thật, nên tôi bỏ một chữ "bạn" ở câu không phải câu khuyên
("nhanh hơn bạn nghĩ" thành "nhanh hơn tưởng tượng") để về lại trong dải.

## 1g. CTA của sapo phải bám truy vấn chính (0.1.8 → 0.1.9)

Người duyệt từ chối bài 002 vì CTA mời đọc một ý phụ thay vì chính truy vấn. Kiểm mới soi ra bài này
cũng vậy: CTA cũ mời "để khoanh vùng tìm trọ theo đúng cơ sở đang học", không nhắc truy vấn chính.

- Sau: *"Mời bạn cùng theo dõi bài viết dưới đây của Muaban.net để biết kinh nghiệm thuê trọ gần
  trường Đại học Kinh tế nên bắt đầu từ đâu."*

Lần sửa đầu tôi viết đủ cả cụm "Đại học Kinh tế TP.HCM" và mật độ truy vấn chính vọt lên 2,5% —
đúng ngưỡng chặn — cộng sapo dài 92 chữ. Đã rút gọn sapo và bỏ phần đuôi địa danh trong CTA, mật độ
về lại mức an toàn.

## 1h. Liên kết bài liên quan chuyển sang khuôn "Xem thêm" (0.1.9 → 0.1.10)

Chủ dự án chốt khuôn dẫn liên kết tới bài khác trên blog: một dòng riêng giữa hai mục, `**Xem
thêm:** [<tiêu đề bài đích>](<url>)`. Kiểm mới trong `onpage_check.py` bắt bài này đang dẫn sai —
liên kết tới bài *thuê trọ gần Đại học Sư phạm Kỹ thuật TPHCM* nằm lẫn trong câu văn ở mục VI.

Đã chuyển thành dòng "Xem thêm" đặt ngay trước `Lời kết`, anchor lấy đúng tiêu đề đang đăng của bài
đích. Câu văn cũ bỏ mệnh đề dẫn link, giữ nguyên ý còn lại.

## 2. Giải trình cảnh báo

| Cảnh báo | Số lần | Giải trình |
|---|---|---|
| `ledger` thiếu `published_date` | 9 | Thông báo địa chỉ cơ sở trên trang hỗ trợ của UEH **không hiển thị ngày đăng**. Để trống là đúng; điền một ngày phỏng đoán mới là vi phạm quy tắc 1. Đổi lại, `effective_date` đã ghi 01/7/2025 theo đúng ngày hiệu lực nêu trong thông báo. |
| `serp` outline có 8 mục, ít hơn top 3 | 1 | Hệ quả trực tiếp của góp ý "gom mục II và III". Không thêm mục rỗng để đủ số — xem mục 1b. |
| `house_voice` | **0** | Sau lượt gộp mục và cân lại mật độ, bài nằm trong dải bài thật ở **cả 18 chỉ số**. Bài thật lệch trung vị 4 chỉ số, nên đây là mức tốt hơn trung bình của chính blog. |
| ~~`slug` 10 từ, nên 3–6 từ~~ | 0 | **Đã hết.** Đo slug 24 bài thật: 5–13 từ, trung vị 7 — ngưỡng cũ "3–6 từ" bắt oan 23/24 bài. Ngưỡng đã sửa theo số đo, và slug 10 từ của bài này nằm giữa dải. Câu hỏi mở số 1 vì thế đã đóng. |

## 3. Giọng nhà

Bài đi qua hai lượt nắn theo `docs/12-giong-nha-muaban.md`. Quá trình có hai lần vọt quá đà đáng ghi lại để lần sau khỏi lặp:

| Lượt | Độ dài câu TB | Câu ngắn | Mật độ từ nối | Số chỉ số lệch |
|---|---|---|---|---|
| Bản đầu | 30,4 | 0,0% | 1,13 | **8** |
| Sau lượt 1 | 22,3 | 6,4% | 10,34 | 4 |
| Sau lượt 2 | 29,9 | 0,0% | 1,13 | 4 |
| **Bản chốt** | **26,6** | **5,9%** | **4,98** | **1** |

Bài học: sửa cả bài một lượt thì dễ vọt sang thái cực kia. Lượt cuối nhắm đúng từng chỉ số còn lệch và chỉ đổi mười hai chỗ.

## 3b. Lượt danh xưng người đọc (bản 0.1.3)

Chủ dự án nhận xét bản 0.1.2 *"không giống tiếng Việt"*, *"cấu trúc nói ngược giống tiếng nước ngoài"* và *"chưa có danh xưng của người đọc như 'bạn nên ....'"*. Đo lại bằng bộ chỉ số mới (quy tắc 17) thì nhận xét đó có số đỡ:

| Chỉ số | Bản 0.1.2 | Bản 0.1.3 | Bài thật (p10–p90) |
|---|---|---|---|
| Tỷ lệ câu khuyên có "bạn" làm chủ ngữ | **18%** | **75%** | 2,7% – 85,0% (trung vị 61%) |
| Mệnh lệnh vô chủ ngữ / 1.000 từ | **4,43** | 1,47 | 0,71 – 4,20 |
| "mình" chỉ người đọc / 1.000 từ | **4,43** | 0,49 | 0 – 1,02 |
| Mật độ "bạn" / 1.000 từ | 5,90 | 9,83 | 1,2 – 10,1 |
| Số chỉ số lệch | 4 / 18 | **1 / 18** | trung vị 4 |

Chỗ sai không phải lượng chữ "bạn" — bản 0.1.2 đã nằm giữa dải bài thật — mà là **vai ngữ pháp** của nó. Chín câu khuyên viết ở dạng mệnh lệnh không chủ ngữ ("Nên để ý đèn đường...", "Hãy hỏi rõ cách tính tiền điện...") đã được đổi chủ ngữ thành "bạn", giữ nguyên nội dung. Chín chỗ dùng "mình" để chỉ người đọc đổi thành "bạn" hoặc gọi tên sự vật.

**Hai lần phải lùi lại, đáng ghi để lần sau khỏi lặp.** Lượt đầu đổi cả chín câu sang "bạn nên" và bỏ hết "mình", kết quả là mật độ "bạn" vọt lên 14,21 (trần bài thật 10,10) và mệnh lệnh vô chủ ngữ tụt về **0** — trong khi bài thật vẫn dùng 0,71–4,20. Tức 100% không phải mục tiêu: gọi người đọc quá dày cũng là lệch giọng. Bản chốt giữ lại ba mệnh lệnh vô chủ ngữ ở những chỗ nghe tự nhiên nhất.

## 4. Nội dung cố ý không có

Ba thứ bị loại theo đúng outline đã duyệt, và người duyệt cần biết vì đối thủ đều có:

**Không có con số giá thuê nào.** Cả ba đối thủ tính vào mức sàn đều nêu khoảng giá. Con số của họ là con số của họ, không phải nguồn, và chưa đếm được tin đăng thật trên Muaban.net để tính mức phổ biến. Đây là khác biệt lớn nhất so với top, và cũng là điểm yếu dễ thấy nhất của bài.

**Không có nội dung pháp lý về tạm trú và hợp đồng thuê.** Hai đối thủ có mục này; ledger `C12` và `C13` đang `GAP` vì chưa tra được văn bản gốc. Bài chỉ hướng người đọc hỏi người có chuyên môn.

**Không xếp hạng an ninh tuyến đường nào.** Mục VII nói thẳng rằng những xếp hạng kiểu đó trên mạng hiếm khi dựa trên dữ liệu, và hướng người đọc tự quan sát hai khung giờ. Nói sai về an ninh một khu dân cư có thật là rủi ro không đáng nhận.

## 5. Rủi ro chính sách Google

| Câu hỏi | Trả lời |
|---|---|
| Có ít nhất một thứ không tìm được ở top 5? | **Có.** Bảng khoanh vùng theo từng cơ sở, và cảnh báo tên phường đổi từ 01/7/2025 |
| Không có bài nào khác trên blog phục vụ cùng intent? | **Có.** Blog có cụm bài cho Sư phạm Kỹ thuật và Tài chính Marketing, chưa có UEH |
| Bỏ hết từ khóa đi, bài vẫn còn lý do tồn tại? | **Có.** Danh sách 10 cơ sở và cái bẫy tên phường vẫn dùng được |
| Đọc xong người ta làm được việc? | **Có** — năm bước ở mục I tới IV, mỗi bước nói rõ tra ở đâu |
| Tiêu đề mô tả đúng nội dung? | **Có**, không phóng đại, không hứa tìm được phòng giá rẻ |

**Scaled content abuse:** cần lưu ý. Bài này thuộc một **cụm bài sinh theo trường học** mà blog đang làm. Cụm đó chỉ an toàn khi mỗi bài có dữ liệu riêng thật; bài này có danh sách cơ sở riêng của UEH nên đạt, nhưng nếu sau này nhân bản khuôn sang trường khác mà chỉ đổi tên thì cụm sẽ thành rủi ro.

## 6. Câu hỏi mở

1. ~~**Slug**~~ — đã đóng bằng số đo, xem mục 2. Giữ `kinh-nghiem-thue-tro-gan-dai-hoc-kinh-te-tphcm`.
2. **Giá thuê** — nếu muốn có khoảng giá, cần cho phép đếm tin đăng thật trên Muaban.net theo từng phường rồi lấy trung vị, kèm số tin và kỳ quan sát.
3. **Ảnh chưa có.** Outline dự kiến bản đồ 10 cơ sở và bảng bốn nhóm; chưa có `image-manifest.csv`. Bản đồ là thứ chứng minh luận điểm chính nhanh nhất, và 12/12 bài thật đều có ảnh kèm caption.
4. **Điểm yếu cần biết:** vùng gợi ý ở mục III suy ra từ vị trí cơ sở, không phải khảo sát thực địa. Người từng ở khu đó sẽ thấy rõ khoảng cách.
5. **Volume bằng 0**, người dùng xác nhận là số thật. Đáng cân nhắc thứ tự ưu tiên so với các bài khác.

## 6b. Ghi chú cho người đăng bài

Bốn việc dưới đây thuộc khâu CMS, Markdown không diễn đạt được (`docs/07`, quy tắc 18):

| Việc | Chi tiết cho bài này |
|---|---|
| Thuộc tính liên kết ngoài | Bài có **một** URL ngoài, dùng ở hai chỗ: câu mở mục II và khối "Căn cứ" — `https://hotro.ueh.edu.vn/bai-viet/dia-chi-cac-co-so-cua-ueh-12008`. Cả hai gắn `target="_blank" rel="nofollow noopener"`. Không có liên kết tài trợ nào trong bài |
| Bộ schema | `BlogPosting` + `BreadcrumbList`, chèn ở `<head>`. **Chưa** có `ImageObject` vì bài chưa có ảnh — thêm khi dựng xong bản đồ cơ sở |
| Làm sạch code | Bản thảo là Markdown thuần, không mang `<span>`/`style=`. Sau khi dán vào trình soạn thảo, gỡ CSS inline mà nó tự sinh, giữ nội dung trong `<p>` |
| Mốc rà Content Gap | **Ngày đăng + 3 tháng.** Chỉ rà khi bài đã vào top 10–20; lấy truy vấn thật từ Search Console rồi bổ sung theo quy trình bình thường, không chèn từ khóa rời vào bài cũ |

## 7. Checklist trước khi đăng

- [ ] Chốt slug
- [ ] Kiểm lại địa chỉ 10 cơ sở trên trang UEH tại ngày đăng, phòng khi trường cập nhật tiếp
- [ ] Dựng bản đồ cơ sở và bảng bốn nhóm, thêm dòng vào `image-manifest.csv`
- [ ] Quyết định có bổ sung khoảng giá từ dữ liệu tin đăng hay không
- [ ] Mở thử hai liên kết nội bộ trước khi đăng
