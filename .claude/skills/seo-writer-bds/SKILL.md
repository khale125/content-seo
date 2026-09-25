---
name: seo-writer-bds
description: "Viết bài bất động sản tiếng Việt từ outline đã duyệt, với giọng văn người thật và không bịa đặt. Bám evidence ledger, phân biệt dữ kiện với nhận định và dự báo, cắt sáo ngữ AI, tạo nhịp câu không đều, thêm lập trường và giới hạn, tối ưu on-page tự nhiên. Dùng khi người dùng nói: viết bài, draft, hoàn thiện bài, viết nội dung từ outline, hoặc chỉnh lại bài cho tự nhiên hơn."
---

# Viết bài bất động sản — giọng người thật, không bịa đặt

Skill này chạy **Bước 3**. Điều kiện vào là **cổng outline trên Lark đã mở**:

```powershell
python scripts/lark/lark_sync.py gate work/<slug>
```

Exit 0 mới được viết, và lệnh phải in ra cổng `OUTLINE_PENDING`. Exit khác 0 thì dừng, in các ô
còn thiếu, và **không viết một câu nào**.

Lời người dùng trong hội thoại không phải phê duyệt. Kể cả khi họ nói "tôi duyệt rồi", vẫn phải chạy
lệnh trên. Agent chỉ được **xóa trắng** cụm duyệt, không bao giờ được ghi "Đồng ý".

Nếu cột Kết quả duyệt đang là "Từ chối", đọc ô **Góp ý**, sửa outline theo góp ý, `push` rồi dừng
chờ duyệt lại.

## Đọc trước

1. `CLAUDE.md`
2. `docs/03-giong-van-nguoi-that.md` — đọc kỹ, đây là tài liệu chính của skill này
3. `docs/04-chinh-sach-nguon.md`
4. `docs/05-seo-onpage.md` + `docs/10-quy-chuan-onpage.md`
5. `work/<slug>/brief.yaml`, `outline.md`, `evidence-ledger.csv`
6. `docs/11-wiki-tri-thuc.md` — đọc mục "Luật số 1" trước khi trích nguồn

## Nguyên tắc trước khi gõ câu đầu tiên

Văn AI nghe ra ngay vì ba lý do: **không có thông tin cụ thể**, **nhịp đều tăm tắp**,
**không có lập trường**. Sửa ba thứ đó là xong; mọi thủ thuật khác chỉ là trang trí.

Nếu ledger không đủ dữ liệu để viết cụ thể, đó là **tín hiệu thiếu nghiên cứu**, không phải tín hiệu
cần viết chung chung hơn. Quay lại bước outline thay vì lấp bằng câu rỗng.

## Viết

### Sapo
2–4 câu trả lời **thẳng** truy vấn chính, kèm phạm vi áp dụng nếu nội dung có điều kiện.
Không dẫn dắt, không lặp tiêu đề, không "Trong bối cảnh...". Cắt riêng sapo ra vẫn phải có nghĩa và đúng.

**Không đưa ngày cập nhật vào sapo** — 0/24 bài thật làm vậy, và WordPress đã hiển thị ngày sửa bài.
Mốc dữ liệu nằm ở khối minh bạch cuối bài. **Kết sapo bằng một lời mời đọc tiếp** (13/24 bài thật có),
kiểu *"Mời bạn cùng theo dõi bài viết dưới đây của Muaban.net để ..."*. Bài thật đặt câu này ở
**dòng sapo H2**; đặt ở đoạn văn đầu cũng được, máy chấp nhận cả hai chỗ.

**Câu mời phải nhắc chính truy vấn người đọc vừa gõ**, không phải một ý phụ trong bài. Mời đọc "để
biết X là điềm gì" khi truy vấn là "X là điềm gì"; mời đọc "để biết nên làm gì với X" là lệch search
intent và đã bị người duyệt từ chối một lần. Cả hai đều bị `onpage_check.py` cảnh báo
nếu thiếu, và cả hai sinh ra từ một lần bị từ chối thật ở cổng duyệt bài.

### Thân bài
- Bám đúng sườn đã duyệt. Đổi cấu trúc thì phải nêu lý do trong báo cáo.
- Mỗi câu có số, ngày hoặc tên riêng phải truy được về một `claim_id` trong ledger, nhưng
  **không chèn ký hiệu `[Cxx]` vào bài** (quy tắc 16b). Dẫn nguồn theo cách bài thật làm: nêu
  tên văn bản ngay trong câu, ví dụ "Theo Điều 8 Nghị định 103/2024/NĐ-CP, ...", rồi liệt kê
  đầy đủ kèm liên kết ở khối "Căn cứ" cuối bài.
- Phân biệt bốn loại phát ngôn bằng **từ ngữ khác nhau**: dữ kiện (khẳng định + nguồn), diễn giải
  ("có thể lý giải", "cách hiểu là", "số này nói lên"), dự báo ("nếu ... thì", nêu điều kiện),
  trải nghiệm (chỉ khi có bằng chứng thật và được phép). **Không dùng "điều này cho thấy"** —
  24/24 bài thật không dùng nó lần nào, và nó từng được kê đơn ở đây nên agent viết ra suốt
  (quy tắc 17, `translated_syntax`).
- Dữ liệu tin đăng Muaban.net là **giá chào**, không phải giá giao dịch. Bắt buộc kèm số tin, kỳ,
  phạm vi địa lý, loại hình. Dùng trung vị, không dùng trung bình.

### Liên kết câu (quy tắc 16a)
Các câu phải nối được với nhau. Từ nối tiếng Việt là phương tiện liên kết, không phải sáo ngữ:
bài thật dùng 3,5–8,7 cụm trên 1.000 từ, và `house_voice_check.py` cảnh báo khi bài xuống dưới
mức đó. Đừng viết từng câu như một mệnh đề độc lập rồi xếp cạnh nhau.

### Nhịp
- Câu 5 chữ đứng cạnh câu 30 chữ. Đoạn 1–5 câu, thay đổi liên tục. Đoạn một câu là hợp lệ.
- Danh sách **không cần đều số lượng**. Mục này 2 ý, mục kia 6 ý.
- Không phải mục nào cũng cần bullet. Trộn đoạn văn, bảng, danh sách đánh số.

### Lập trường và danh xưng người đọc (quy tắc 17)
Mỗi mục lớn có ít nhất một câu nói rõ **bạn nên làm gì, bạn không nên làm gì, hoặc bạn cần cẩn
thận chỗ nào** — và câu đó phải lấy **"bạn" làm chủ ngữ**. Khuôn của bài thật:

> **trạng ngữ → "bạn" → động từ khuyên → việc cụ thể**
>
> *"Trước khi đặt cọc, **bạn cần hỏi** rõ giá điện, nước, internet, phí gửi xe, phí rác."*

Viết "Nên hỏi chủ trọ...", "Hãy kiểm tra công tơ..." là **lỗi**, không phải một biến thể:
`house_voice_check.py` chặn bài có dưới 50% câu khuyên gọi người đọc và in ra từng câu phải sửa.
Câu trả lời trong mục hỏi đáp cũng phải gọi "bạn". Không dùng "mình" để chỉ người đọc.

Dám khuyên ngược, dám nói cái dở, dám thừa nhận không biết. Câu thừa nhận giới hạn được dùng
"chúng tôi" ("chúng tôi chưa tìm được văn bản công bố thống nhất, bạn cần hỏi trực tiếp").

Ranh giới: lập trường là **diễn giải từ dữ kiện có nguồn**, không phải trải nghiệm bịa.
Không bao giờ viết "Tôi từng tư vấn cho một khách hàng..." nếu không có ca thật đã xác minh.

### Kết
Không có mục "Kết luận" tóm tắt lại bài. Thay bằng **việc cụ thể người đọc làm được ngay**.
Không "hy vọng bài viết hữu ích", không "chúc bạn thành công".

### Khối minh bạch (bắt buộc với YMYL — bất động sản luôn là YMYL)
Mốc dữ liệu, phạm vi áp dụng, giới hạn, khuyến nghị tham vấn, danh sách căn cứ có liên kết.

## Cấm tuyệt đối

Không sinh ra nếu không có nguồn: con số bất kỳ, tên và số hiệu văn bản, ngày ban hành/hiệu lực,
tên dự án và chủ đầu tư, thông tin quy hoạch, tên chuyên gia và phát ngôn, khảo sát, **URL nguồn**,
trải nghiệm cá nhân, tác giả và bằng cấp.

Không câu nào bảo đảm tăng giá, sinh lời, thanh khoản, duyệt vay, thắng kiện, hay thứ hạng Google.

**Không trích dẫn wiki.** `wiki/` là tri thức do agent tự dựng, không phải nguồn. Dòng ledger có
`wiki_ref` vẫn phải trích `source_url` gốc trong bài và trong khối căn cứ — `wiki_ref` chỉ nói claim
đó lấy lại từ đâu trong kho nội bộ. Đặt liên kết tới một trang `wiki/` trong bài là lỗi nặng hơn
thiếu nguồn, vì nó trông như đã có nguồn.

Thiếu bằng chứng thì chọn một trong ba: **bỏ claim**, **thu hẹp tới mức nguồn chịu được**, hoặc
**chuyển thành hướng dẫn để người đọc tự tra cứu** (tra ở đâu, hỏi ai, mang gì).

## Tự sửa — chạy đúng thứ tự, đừng gộp

1. **Lượt dữ kiện** — đối chiếu từng câu có số/ngày/tên với ledger.
2. **Lượt cắt** — xóa mọi câu không thêm thông tin. Thường cắt được 15–25%.
3. **Lượt sáo ngữ — BẮT BUỘC gọi skill `humanizer-bds`** (CLAUDE.md quy tắc 13).
   Chạy `python scripts/human_voice_check.py work/<slug>/article.md` rồi vá từng cảnh báo **không
   phải** là đã áp dụng humanizer. Máy chỉ **báo**; skill mới **sửa**. Nhầm hai việc này đã làm một
   bài bị từ chối ở cổng duyệt. Dấu hiệu bài chưa qua skill: bài tự nói về chính nó ("bài này không
   liệt kê…", "bài cố ý không đưa…") thay vì nói với người đọc.
   Không thay sáo ngữ này bằng sáo ngữ khác; cắt hẳn hoặc viết lại bằng thông tin cụ thể.
   Máy chỉ **báo** lỗi. Cách **sửa** nằm ở skill `humanizer-bds`: gọi nó cho từng đoạn bị đánh dấu,
   hoặc cho cả bài khi nhiều cảnh báo tụ lại. Skill đó biết bảy thứ không được chạm — tên văn bản,
   con số, khối minh bạch, front matter, link map, bảng, tiêu đề nhận truy vấn chính.
4. **Lượt nhịp** — đọc thành tiếng, sửa chỗ hụt hơi và chỗ cụt lủn liên tục.
5. **Lượt lập trường** — mỗi mục lớn có khuyến nghị.
6. **Lượt người đọc** — đọc lại với vai người mua nhà lần đầu; chỗ nào phải đọc hai lần thì viết lại.
7. **Lượt giọng nhà — BẮT BUỘC gọi skill `giong-muaban-bds`** (quy tắc 15 và 17). Sáu lượt trên
   làm bài đúng và dễ đọc; lượt này làm bài **giống bài đang đăng trên blog**. Đây là hai việc
   khác nhau: bài 001 từng đạt mọi lượt trên mà vẫn bị từ chối vì "cách diễn đạt rất cứng", rồi
   lần sau bị chê "không giống tiếng Việt" và "chưa có danh xưng của người đọc".
   Skill đó gồm hai lượt: nắn khuôn mục và nhịp câu, rồi **sáu phép sửa cú pháp** (danh từ hóa,
   chủ ngữ trừu tượng, mệnh đề phụ dồn lên trước, mệnh lệnh vô chủ ngữ, "mình", bị động).
   Kiểm bằng `python scripts/house_voice_check.py work/<slug>/article.md`: `BLOCK` về danh xưng
   phải sửa hết, và số chỉ số lệch phải nằm trong mốc máy in ra.

## On-page

SEO fields nằm trong **front matter của `article.md`**, không tách file.

**Title** — nhắm 55–63 ký tự (24 bài thật: 49–70, trung vị 59), truy vấn chính **một lần** ở nửa
đầu, không hứa hẹn. Blog tạo CTR bằng **con số** chứ không bằng tính từ: 58% title thật có chữ số
("12+ cách…", "Top 3 khu vực…", "6 ưu điểm…"). **Không đưa tên thương hiệu vào title** — 0/24 bài
thật làm vậy.

**Meta** — nhắm 138–161 ký tự (bài thật 116–164, trung vị 147), theo đúng khuôn đo được:

> **`<động từ dẫn>` + `<cụm truy vấn chính>` + `:` hoặc `với` + `<3–5 thứ bài trả lời>` +
> `<lợi ích người đọc nhận được>`**
>
> *"Kinh nghiệm thuê phòng trọ Bình Chánh: cách chọn vị trí, giá thuê, kiểm tra phòng và lưu ý
> hợp đồng để tránh rủi ro."*

Hai điều bắt buộc, `onpage_check.py` chặn: **meta phải chứa truy vấn chính** (21/24 bài thật có)
và phải đặt nó **trong 60 ký tự đầu** (21/21 bài thật đặt vậy, vị trí trung vị là ký tự thứ 9).
Người đọc quét trang kết quả bằng chính chữ họ vừa gõ. Tên thương hiệu trong meta thì tùy — chỉ
29% bài thật có.

**Slug** 3–6 từ không dấu.

Các con số trên là mục tiêu biên tập. `onpage_check.py` rộng hơn: nó chỉ cảnh báo khi title ra
ngoài **40–65** và meta ra ngoài **120–165**, nên đừng tưởng máy im là đã đạt chuẩn.

**Dấu ngoặc kép trong meta:** front matter dùng YAML, nên nếu meta có ngoặc kép bên trong thì bọc
cả chuỗi bằng **ngoặc đơn** (`meta_description: '... "gần trường" ...'`). Đừng bỏ ngoặc kép đi cho
hết lỗi cú pháp — làm vậy một lần đã khiến cả vế đầu của meta mất nghĩa và bài bị từ chối.

Theo `docs/10-quy-chuan-onpage.md`, thêm sáu ràng buộc máy kiểm được:

- **H1 không trùng nguyên văn Title, không trùng URL.**
- Từ khóa chính nằm trong **100 chữ đầu** và được **in đậm** một lần.
- **Đoạn kết thân bài** nhắc lại từ khóa chính một cách tự nhiên.
- **Mỗi mục tối đa 230 chữ** — dài hơn thì tách heading con.
- **Bài trên 1.200 chữ phải có mục lục (TOC).**
- **Mỗi ảnh có caption**; alt ảnh đầu chứa từ khóa chính nhưng **vẫn phải mô tả đúng ảnh**.

Cụm từ khóa chính chỉ xuất hiện nguyên văn ở **một** sub-heading. Từ hai chỗ trở lên là quá tối ưu.

**Cấu trúc bài theo format hệ Blog Muaban.net** (quy tắc 14): một H2 cho sapo đứng trước mọi mục
chính, mục chính ở **H3 đánh số La Mã**, mục con ở **H4 đánh số Ả Rập**, **`Lời kết`** là mục cuối.
Không tự thêm mục lục. `onpage_check.py` kiểm phần này.

**Mục áp chót phải là mục dẫn về tin đăng Muaban.net** (quy tắc 15), tên theo mẫu
"Tìm/Mua [loại hình] [địa bàn] trên Muaban.net", đặt ngay trước `Lời kết`. Đây là mục nội dung thật
— cách lọc tin, khu vực lân cận, khoảng giá — không phải một dòng quảng cáo. Thiếu là `BLOCK`.

**Nhịp câu theo giọng nhà, không theo bản năng.** Blog viết câu dài và đều: trung bình 27 từ mỗi câu,
2 câu mỗi đoạn, và gần như không dùng câu dưới 10 từ. Đừng chẻ câu cho "có nhịp" — đó chính là lỗi
làm bài 001 bị chê cứng. Chi tiết ở `docs/12-giong-nha-muaban.md`.

**Câu dài của bài thật là câu có mệnh đề phụ kéo về SAU**, không phải câu có mệnh đề chen trước
chủ ngữ. Làm dài bằng cách dồn mệnh đề lên đầu là rơi vào cú pháp dịch — xem
`docs/13-cu-phap-tieng-viet.md`.

Một H1. Heading không nhảy cấp, là câu hỏi hoặc mệnh đề có thông tin.
Không đặt mục tiêu mật độ từ khóa — đảm bảo các `entities` trong brief xuất hiện tự nhiên.

Liên kết: ≥1 nội bộ tới danh mục/tin đăng Muaban.net đúng địa bàn và loại hình, ≥1 ngoài tới nguồn gốc.

**Liên kết tới bài khác trên blog đi theo khuôn "Xem thêm"**: một dòng riêng giữa hai mục,
`**Xem thêm:** [<tiêu đề bài đích>](<url>)`, anchor lấy đúng tiêu đề đang đăng. Không viết thành câu
văn chen giữa mục, và **không dựng thêm mục lạc đề để chứa liên kết** — người duyệt đã từ chối cả
hai cách đó. Không có chỗ nào tự nhiên để đặt thì bỏ liên kết. Liên kết tới **danh mục tin đăng** thì
khác: nó nằm trong mục dẫn tin đăng hoặc ở câu kết bài.

**Đích internal link lấy từ kho, không tự nghĩ URL:**

```powershell
python scripts/internal_links.py find --brief work/<slug>/brief.yaml
python scripts/internal_links.py find "phòng trọ quận 10"
```

Kho `reference/internal-links-mbn.csv` có 1.217 URL Muaban.net kèm keyword mục tiêu để làm anchor.
Chi tiết cách đọc kết quả ở `docs/05-seo-onpage.md` mục "Kho URL để chọn đích internal link".
Anchor mô tả đích đến, không dùng "tại đây"/"xem thêm". Đối chiếu với link map trong `outline.md`;
`onpage_check.py` đọc liên kết trực tiếp từ bài.

**Hai loại link out** (quy tắc 18): link out **định nghĩa** đặt ngay trong câu đang nhắc tên văn bản
hoặc khái niệm — đúng chỗ quy tắc 16b đòi nêu tên văn bản trong câu — và link out **tham khảo** ở
khối "Căn cứ" cuối bài. Dồn hết liên kết ngoài xuống cuối là `WARN`. **Miền của liên kết ngoài phải
có trong `evidence-ledger.csv`**; Wikipedia được dùng làm link out định nghĩa nhưng không được làm
`source_url` cho claim.

Alt text mô tả nội dung ảnh cho người không nhìn thấy, không nhồi từ khóa. Mọi ảnh phải có bản quyền
rõ ràng và một dòng trong `image-manifest.csv`. Không hotlink, không lấy ảnh báo/đối thủ.

**Bài phải có ảnh** (quy tắc 19): nhắm **6–10 ảnh**, khoảng một ảnh cho mỗi mục La Mã, theo image plan
đã duyệt ở outline. Ưu tiên ảnh tự dựng từ dữ liệu có nguồn — sơ đồ, bản đồ, bảng so sánh — vì đó là
loại ảnh chắc chắn đúng ngữ cảnh và sạch bản quyền. Lưu file vào `work/<slug>/images/`, ghi một dòng
manifest cho mỗi ảnh với `rights_status = CLEARED`, rồi chèn kèm chú thích in nghiêng ngay dưới:

```markdown
![Công tơ điện riêng gắn trước cửa từng phòng trọ](images/cong-to-dien-phong-tro.webp)

*Phòng có công tơ riêng giúp bạn đối chiếu số điện mỗi tháng thay vì tin vào cách tính khoán*
```

Ảnh không có dòng manifest, hoặc dòng chưa `CLEARED`, là `BLOCK`. **Ảnh AI dựng để minh họa một địa
điểm hay giấy tờ có thật là vi phạm quy tắc 1.** Cách tìm ảnh: `docs/14-anh-va-ban-nhap-wordpress.md`.

Schema chỉ khai báo khi **khớp nội dung hiển thị**. Không gắn `author` cho người chưa xác minh.
Khai vào `schema` và `schema_extra` của front matter: **`BlogPosting` + `BreadcrumbList`** (24/24 bài
thật, không dùng `Article`), thêm `ImageObject` khi bài có ảnh và `FAQPage` khi bài có mục hỏi đáp.
Khai một loại mà bài không có thứ tương ứng là `BLOCK` (quy tắc 18).

**Bản thảo là Markdown thuần.** Không mang `<span>`, `<font>`, `<center>` hay `style="..."` vào bài —
để khi dán lên CMS nội dung nằm gọn trong `<p>`. Ngoại lệ duy nhất: `<blockquote cite="...">` cho
trích dẫn thật.

## Ra khỏi skill

```powershell
python scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json
python scripts/lark/lark_sync.py push work/<slug>
```

Sửa hết `BLOCK` trước khi push. Khi QA đạt `PASS`, push đưa trạng thái sang "Chờ duyệt bài",
tăng số Bản và xóa trắng cụm duyệt — bài mới phải được duyệt lại từ đầu.
Giải trình từng `WARN` còn lại vào `qa-report.md` trước khi push.

Sau đó chuyển sang skill `seo-qa-bds` để đóng gói bàn giao.
