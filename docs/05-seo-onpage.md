# 05 — SEO on-page

Nguyên tắc chung: on-page là việc **mô tả trung thực** nội dung cho máy đọc. Mọi kỹ thuật vượt quá
việc mô tả trung thực đều là rủi ro, không phải lợi thế.

> **Quy chuẩn chi tiết của dự án** (title, H1, độ dài mỗi mục, vị trí từ khóa, TOC, caption, schema,
> outlink) nằm ở [`10-quy-chuan-onpage.md`](10-quy-chuan-onpage.md) — lấy từ file Google Sheet quy
> chuẩn, kèm phần ghi rõ chỗ nào đã điều chỉnh và vì sao. Tài liệu 05 này giữ phần nguyên tắc.

## Title

- Nhắm 50–60 ký tự để không bị cắt trên di động. Đây là mục tiêu biên tập; `onpage_check.py`
  chỉ cảnh báo khi ra ngoài khoảng **40–65**, nên 62 ký tự không bị máy chặn.
- Chứa truy vấn chính **một lần**, ở nửa đầu, viết tự nhiên.
- Thêm yếu tố phân biệt: năm (chỉ khi nội dung thật sự theo năm), địa bàn, con số, phạm vi.
- Không nhồi: `Thủ tục sang tên sổ đỏ | Sang tên sổ đỏ mới nhất | Sang tên nhà đất` là spam.
- Không hứa hẹn, không "bí quyết", "bật mí", "100%".
- Title trên SERP và H1 có thể khác nhau chút ít, nhưng phải cùng lời hứa.

Tốt: `Thủ tục sang tên sổ đỏ 2026: hồ sơ, chi phí, thời gian xử lý`

## Meta description

- Nhắm 140–160 ký tự; `onpage_check.py` cảnh báo khi ra ngoài **120–165**.
  Không phải tín hiệu xếp hạng, nhưng quyết định tỷ lệ nhấp.
- Nói **kết quả người đọc nhận được**, không tóm tắt bài.
- Chứa truy vấn chính nếu vào tự nhiên, không ép.
- Không lặp lại nguyên văn title.

## Slug / URL

- Ngắn, không dấu, gạch nối, 3–6 từ: `thu-tuc-sang-ten-so-do`.
- Không nhét năm vào slug nếu bài sẽ được cập nhật hằng năm (URL sẽ phải đổi hoặc bị cũ).
- Không tạo nhiều slug gần trùng cho cùng intent.
- Slug đã publish thì **không đổi**; nếu buộc phải đổi thì cần 301 và đó là quyết định của người thật.

## Cấu trúc heading

- **Một H1 duy nhất** — là tiêu đề bài.
- H2 cho các mục chính, H3 cho mục con. Không nhảy cấp (H2 rồi H4).
- Heading là **câu hỏi hoặc mệnh đề có thông tin**, không phải cụm từ khóa.
- Không dùng heading để nhét biến thể từ khóa.
- Mỗi H2 nên trả lời xong một câu hỏi và đứng độc lập được — đây cũng là điều kiện để đoạn đó có cơ
  hội được trích dẫn.

> Title, meta description, slug và schema khai báo trong **front matter của `article.md`**,
> không tách file riêng.
>
> Nếu bài sẽ đưa lên WordPress của Muaban.net, xem thêm hợp đồng trình bày của Affiliate Blog trong
> project `Create content blog` (H1 là `post_title`, sapo là H2 không in đậm, mục chính đánh số La Mã).
> Project này để nội dung ở dạng Markdown trung lập; việc chuyển đổi nằm ngoài phạm vi.

## Đoạn mở đầu

Đây là phần có giá trị SEO cao nhất và hay bị viết hỏng nhất.

- 2–4 câu, trả lời **trực tiếp** truy vấn chính.
- Nêu phạm vi và mốc thời gian nếu nội dung phụ thuộc thời điểm.
- Không dẫn dắt, không lặp lại tiêu đề, không "Trong bối cảnh...".
- Viết sao cho cắt riêng đoạn này ra vẫn có nghĩa và vẫn đúng.

## Thực thể quan trọng hơn mật độ từ khóa

Không đặt mục tiêu mật độ. Thay vào đó, đảm bảo bài **nhắc đúng các thực thể** liên quan:
tên cơ quan, tên văn bản, tên địa bàn, tên loại giấy tờ, tên khoản thuế/phí, tên loại hình.
Danh sách thực thể đã chốt ở `brief.yaml`.

`scripts/onpage_check.py` báo `WARN` khi truy vấn chính xuất hiện quá dày (mặc định trên 2,5%),
vì đó thường là dấu hiệu viết gượng, và báo `WARN` khi thực thể trong brief không xuất hiện lần nào.

## Liên kết nội bộ

- Tối thiểu **1 liên kết tới danh mục hoặc trang tin đăng Muaban.net** đúng loại hình và địa bàn.
- Thêm liên kết tới các bài liên quan trên blog, đặt ở chỗ người đọc thật sự cần đọc tiếp.
- Anchor **mô tả đích đến**: "tin đăng bán căn hộ tại Bình Tân", không phải "tại đây", "xem thêm",
  "click vào đây".
- Không nhồi liên kết. Khoảng 3–8 liên kết nội bộ cho một bài 1200–1800 chữ là hợp lý.
- Mỗi liên kết phải có lý do trong link map (mục "Link map" của `outline.md`).

### Liên kết tới bài khác trên blog: khuôn "Xem thêm"

Liên kết tới **một bài viết khác của blog** không viết thành câu văn trong đoạn, mà nằm trên **một
dòng riêng giữa hai mục**:

```markdown
**Xem thêm:** [Bướm bay vào nhà là điềm gì? Luận giải con số may mắn liên quan](https://muaban.net/blog/buom-bay-vao-nha-532268/)
```

Anchor là **tiêu đề bài đích**, lấy đúng như tiêu đề đang đăng. `onpage_check.py` cảnh báo khi một
liên kết `muaban.net/blog/...` nằm lẫn trong câu văn thay vì trên dòng "Xem thêm" riêng.

Khuôn này do chủ dự án đưa kèm ảnh chụp bài đang đăng, sau khi hai cách dẫn khác đều bị từ chối ở
cổng duyệt: một lần viết thành câu chen giữa mục, một lần dựng hẳn một mục lạc đề để chứa liên kết.
**Không có chỗ nào tự nhiên để đặt thì bỏ liên kết**, đừng thêm mục cho nó.

Dòng "Xem thêm" **không tính vào phép đo giọng văn** — `house_voice_profile.py` loại nó khỏi văn
xuôi ở cả kho bài thật lẫn bài đang viết, vì tiêu đề bài đích hay kết bằng dấu hỏi và sẽ đẩy chỉ số
"câu hỏi trong thân bài" lên oan.

### Kho URL để chọn đích internal link

Không tự nghĩ ra URL danh mục. Kho `reference/internal-links-mbn.csv` giữ **2.137 dòng /
1.217 URL** của Muaban.net, nhập từ sheet *BĐS MBN* trong file từ khoá nội bộ (nguồn ghi ở
`reference/internal-links-mbn.meta.json`).

```powershell
python scripts/internal_links.py find "phòng trọ quận 10"
python scripts/internal_links.py find --brief work/<slug>/brief.yaml
python scripts/internal_links.py stats
```

Lệnh trả về URL kèm **anchor đề xuất** lấy từ cột `Keyword mục tiêu` của sheet, cộng loại giao
dịch, loại bất động sản và địa bàn suy từ slug. Ba điều cần biết khi đọc kết quả:

- **Trang danh mục được cộng điểm so với trang `/tags/`**, vì quy tắc trên đòi liên kết tới danh
  mục đúng địa bàn và loại hình. Cần trang tag thì thêm `--kind tag`.
- Bài không nhắc quận nào thì trang cấp tỉnh hoặc toàn quốc **đúng hơn** trang của một quận bất kỳ;
  máy đã trừ điểm theo hướng đó.
- Anchor phải đọc trôi trong câu. Cụm keyword của sheet là gợi ý, không phải mệnh lệnh — nhồi
  nguyên văn một cụm không vào được câu thì viết lại anchor cho tự nhiên.

Địa bàn và loại giao dịch trong kho **suy từ slug URL**, không lấy từ cột phân loại của sheet: đo
trên chính dữ liệu đó cho thấy cột `Tỉnh/Tp` lệch với URL ở 24/1.076 dòng danh mục và 47/51 dòng
trang tag, còn cột `SubCate 2` ghi ngược mua bán / cho thuê ở 58 dòng. Cột gốc vẫn được giữ ở
`sheet_province` và `sheet_district` để đối chiếu.

Làm mới kho khi sheet đổi:

```powershell
curl -sL "https://docs.google.com/spreadsheets/d/<id>/export?format=csv&gid=0" -o bds-mbn.csv
python scripts/internal_links.py build --from bds-mbn.csv
```

## Liên kết ngoài

- Bài có dữ liệu phải có ít nhất **1 liên kết tới nguồn gốc**. Dẫn nguồn không làm mất traffic;
  nó là điều kiện để bài đáng tin.
- Trỏ tới **trang chứa thông tin cụ thể**, không trỏ về trang chủ của nguồn.
- HTTPS, mở tab mới, `rel="noopener"`. Liên kết có trả tiền thêm `rel="sponsored nofollow"`.
- Không trỏ tới đối thủ trực tiếp trong mảng rao vặt/tin đăng.
- **Hai loại link out, không phải một** (file quy chuẩn, tab *Kĩ thuật SEO*): link out **định nghĩa**
  nằm ngay trong câu đang nói về khái niệm hoặc văn bản đó, anchor là từ khóa semantic; link out
  **tham khảo** nằm ở khối "Căn cứ" cuối bài. Dồn hết liên kết xuống cuối là `WARN`.
- **Miền của liên kết ngoài phải có trong `evidence-ledger.csv`.** File quy chuẩn đòi nguồn có
  DR ≥ 20; dự án không đo được DR và không được bịa con số đó, nên thay bằng điều kiện đo được này.
- **Wikipedia** được dùng làm link out định nghĩa, **không** được làm `source_url` cho claim —
  `docs/04` không nhận trang tổng hợp làm nguồn.
- Bài thật đặt `target="_blank"` và `nofollow` cho **toàn bộ** liên kết ngoài (đo 20/20 liên kết
  trên 24 bài). Markdown không mang được hai thuộc tính này nên chúng nằm trong ghi chú bàn giao.

## Hình ảnh

- **Alt text mô tả nội dung ảnh cho người không nhìn thấy**, không phải chỗ nhét từ khóa.
  Tốt: "Mẫu tờ khai lệ phí trước bạ nhà đất, mục kê khai giá trị tài sản". Xấu: "sang tên sổ đỏ
  thủ tục sang tên sổ đỏ 2026".
- Ảnh trang trí thuần túy dùng `alt=""`.
- Tên file mô tả, không dấu: `to-khai-le-phi-truoc-ba.jpg`.
- Kích thước hợp lý, nén, ưu tiên WebP. Khai báo `width`/`height` để tránh nhảy bố cục.
- Chỉ dùng ảnh có quyền rõ ràng. Lưu nguồn, tác giả, giấy phép, ngày lấy trong image manifest.
- Biểu đồ tự dựng từ dữ liệu có nguồn là loại ảnh giá trị nhất — ưu tiên hơn ảnh stock minh họa.
- **Số ảnh nhắm 6–10 mỗi bài** (đo 24 bài thật, trung vị 8), chú thích 7–20 từ. Bài không có ảnh
  nào là `WARN`. Cách tìm ảnh, nguồn được phép và nguồn bị cấm: `docs/14-anh-va-ban-nhap-wordpress.md`.
- Mỗi ảnh phải có một dòng trong `image-manifest.csv` với `rights_status = CLEARED` — thiếu dòng
  hoặc chưa CLEARED đều là `BLOCK`.

## Dữ liệu có cấu trúc (schema)

Chỉ khai báo schema **khớp với nội dung hiển thị**. Schema mô tả thứ không có trên trang là vi phạm
chính sách structured data.

| Loại bài | Schema hợp lệ |
|---|---|
| Mọi bài blog | **`BlogPosting`** + `BreadcrumbList` + `ImageObject` cho ảnh đại diện, kèm `author` + `datePublished` + `dateModified`. Cả 24 bài thật dùng `BlogPosting`, không dùng `Article` |
| Bài thủ tục | `HowTo` — chỉ khi bài thật sự là các bước thao tác có thứ tự |
| Bài có FAQ | `FAQPage` — chỉ khi câu hỏi và trả lời **hiển thị trên trang** |
| Bài có bảng giá | Không dùng `Product`/`Offer` cho bài blog |

Khai vào hai trường `schema` và `schema_extra` của front matter; `onpage_check.check_schema` đọc
đúng hai trường đó. **Khai một loại mà bài không có thứ tương ứng là `BLOCK`** — ảnh cho
`ImageObject`, mục hỏi đáp cho `FAQPage`, video nhúng cho `VideoObject`. Số đo và bảng mức ở
`docs/10-quy-chuan-onpage.md` mục E3.

Không dùng `Review`/`AggregateRating` cho nội dung biên tập. Không gắn `author` cho người chưa xác minh.

## Tín hiệu tươi mới và cập nhật

- Hiển thị **ngày cập nhật** khi bài phụ thuộc thời điểm, và chỉ đổi ngày khi **thật sự có sửa nội dung**.
  Đổi ngày mà không sửa gì là thủ thuật, dễ phản tác dụng.
- Ghi rõ **đã sửa gì** trong ghi chú cập nhật với bài pháp lý/số liệu.
- Đặt `review_after` trong `brief.yaml`.

## Những gì KHÔNG làm

- Không nhồi từ khóa, không văn bản ẩn, không doorway page.
- Không sinh hàng loạt bài gần trùng cho từng quận/huyện nếu nội dung chỉ khác tên địa bàn.
  Đó chính là scaled content abuse (xem `06-chinh-sach-google.md`).
- Không đặt mục tiêu số chữ để "dài hơn đối thủ".
- Không copy rồi viết lại (spin) nội dung của trang khác.
- Không trao đổi/mua liên kết.
- Không dùng schema sai lệch.
- Không mang HTML trang trí vào bản thảo: `<span>`, `<font>`, `<center>`, `style="..."`. Bản thảo là
  Markdown thuần để khi lên CMS nội dung nằm gọn trong `<p>` (`docs/10` mục E2).
