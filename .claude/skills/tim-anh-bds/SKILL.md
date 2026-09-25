---
name: tim-anh-bds
description: Tim anh tren internet co giay phep ro rang (Wikimedia Commons, Openverse) cho bai blog Muaban.net, MO RA XEM tung anh truoc khi chon, tai ve, ghi image-manifest.csv, viet alt va chu thich dung voi anh, roi chen vao bai. Dung khi nguoi dung noi: tim anh, chen anh, bai chua co anh, them hinh, anh minh hoa, image plan, hoac khi onpage_check bao bai khong co anh.
---

# Tìm ảnh trên internet và chèn vào bài

Skill này lấp chỗ trống giữa **image plan** trong outline và **ảnh thật** trong bài. Nó không vẽ sơ
đồ và không sinh ảnh AI. Nó đi tìm ảnh người thật chụp, có giấy phép cho dùng thương mại, rồi chèn
vào đúng chỗ kèm ghi công.

Công cụ: `scripts/image_search.py`. Quy tắc: CLAUDE.md quy tắc 19, `docs/14` mục A6.

## Đọc trước

1. `docs/14-anh-va-ban-nhap-wordpress.md` mục A (đặc biệt A3 "tuyệt đối không dùng" và A6)
2. Mục **Image plan** trong `work/<slug>/outline.md`
3. Chính `work/<slug>/article.md`, **đoạn sẽ đặt ảnh**. Chú thích ảnh là nội dung, nên nó chịu
   quy tắc 1 như mọi câu khác.

## Bốn điều không thương lượng

**1. Mở ảnh ra xem trước khi chọn.** Tiêu đề và tag trên kho ảnh không đáng tin: tìm
"dragonfly window" trả về cả một file tên "Leaf Window" chụp chiếc lá. `search` tải bản xem trước
vào `work/<slug>/images/_preview/`; dùng công cụ Read mở **từng** file định chọn. Chưa nhìn thì
chưa được `fetch`.

**2. Ảnh không được nói ngược lời khuyên của bài.** Bài 002 khuyên *không cầm chuồn chuồn trong tay*
vì cánh dễ rách. Một ảnh chuồn chuồn đậu trên ngón tay rất đẹp đã bị loại vì lý do đó. Trước khi
chọn, bạn đọc lại đoạn sẽ đặt ảnh và hỏi: người đọc nhìn ảnh này có làm ngược điều bài vừa dặn không.

**3. Chú thích chỉ nói điều nhìn thấy trong ảnh hoặc điều bài đã có nguồn.** Được ghi "ảnh chụp ở
Bến Tre" khi mô tả trên Commons ghi Bến Tre. **Không** được ghi "chuồn chuồn trong nhà bạn" khi ảnh
chụp ngoài vườn, **không** gắn tên loài khi file không định danh, **không** gắn địa danh Việt Nam
cho ảnh chụp ở nước khác. Ảnh chụp ở nước ngoài thì chú thích tả con vật hoặc vật thể, bỏ phần
địa điểm.

**4. Chỉ nhận CC0, Public Domain, CC BY, CC BY-SA.** Công cụ đã tự loại NC (cấm thương mại), ND
(cấm phái sinh — WordPress tự cắt ảnh thành nhiều cỡ tức là tạo bản phái sinh), GFDL đơn lẻ, và
ảnh CC BY mà không rõ tác giả (không ghi công được thì không dùng được).

## Quy trình

### 1. Lập danh sách vị trí

Đọc image plan trong outline, rồi đối chiếu với bài đã viết: mục nào thực sự cần ảnh, ảnh đó
**giải thích được gì mà chữ không làm nhanh bằng**. Không trả lời được thì bỏ vị trí đó.

Nhắm **6–10 ảnh** (24 bài thật: trung vị 8), khoảng một ảnh mỗi mục La Mã. Mục trừu tượng — mơ
thấy gì, con số may mắn — thường không cần ảnh, và ép một ảnh vào đó là ảnh trang trí.

### 2. Tìm bằng danh từ cụ thể, ưu tiên ảnh chụp ở Việt Nam

```powershell
python scripts/image_search.py search "Crocothemis servilia Vietnam" --slug <slug> --source commons
python scripts/image_search.py search "damselfly Vietnam" --slug <slug>
```

- Tìm bằng **tiếng Anh và tên khoa học**: kho quốc tế gắn tag bằng tiếng Anh. Tên loài cho kết
  quả sạch hơn hẳn tên thông thường.
- Thêm **"Vietnam"**, tên tỉnh hoặc thành phố trước: ảnh đúng bối cảnh Việt Nam luôn hơn ảnh đẹp
  chụp ở châu Âu. Lần làm bài 002, "Orthetrum sabina Vietnam" trả về cả loạt ảnh chụp ở TP.HCM.
- `--source commons` trước. Openverse gom ảnh từ Flickr và nơi khác, giấy phép phải kiểm lại ở
  trang gốc (bước 4).
- Công cụ in mỗi ứng viên kèm kích thước, giấy phép, tác giả, mô tả và đường dẫn ảnh xem trước.

### 3. Xem và chọn

Mở ảnh xem trước bằng Read. Với mỗi ảnh, trả lời bốn câu:

| Câu hỏi | Loại nếu |
|---|---|
| Ảnh có đúng thứ đoạn văn đang nói không? | Chỉ "liên quan chủ đề" |
| Ảnh có nói ngược lời khuyên của bài không? | Có |
| Chủ thể có rõ, nét, không bị cắt không? | Mờ, nhỏ, lẫn nền |
| Có watermark, chữ nước ngoài, logo, mặt người nhận ra được không? | Có |

Ghi lại lý do loại những ứng viên đáng cân nhắc — nó vào `qa-report.md` để người duyệt biết bạn đã
cân nhắc những gì.

### 4. Tải về và ghi manifest

```powershell
python scripts/image_search.py fetch c014 --slug <slug> --position body-3 `
  --name chuon-chuon-kim-xanh-ben-tre.jpg `
  --alt "Chuồn chuồn kim thân mảnh màu xanh dương đậu trên lá cây, hai đôi cánh khép dọc thân" `
  --caption "Chuồn chuồn kim thân mảnh, khép cánh dọc thân khi đậu, ảnh chụp ở Bến Tre" `
  --purpose "Mục III.1: để người đọc nhận ra chuồn chuồn kim khác chuồn chuồn thường"
```

`fetch` hỏi lại nguồn (giấy phép có thể đã đổi từ lúc tìm), tải bản gốc, **cắt về đúng 800x600**
quanh `--focus x,y` (mặc định `0.5,0.5` là giữa ảnh), rồi ghi đủ 11 cột
manifest với `rights_status = CLEARED`. Ảnh từ **Openverse** được ghi `BLOCKED`: bạn mở trang gốc
mà công cụ in ra, xác nhận giấy phép ở đó, rồi chạy lại với `--verified`.

**Mở ảnh đã cắt ra xem.** Cắt từ ảnh ngang về 4:3 hay cắt mất đuôi hoặc cánh. Lệch thì cắt lại
từ bản gốc mà không phải tải lại:

```powershell
python scripts/image_search.py reframe --slug <slug> --name <ten-file.jpg> --focus 0.66,0.5
```

`x` lớn hơn 0,5 là dời khung sang phải, `y` nhỏ hơn 0,5 là dời lên trên. Ảnh gốc quá nhỏ để cắt ra
800x600 thì công cụ từ chối — tìm ảnh khác, đừng phóng to.

- **`--alt`** tả đúng ảnh cho người không nhìn thấy. Ảnh đầu bài chứa từ khoá chính nhưng vẫn phải
  tả đúng ảnh.
- **Alt và chú thích là bắt buộc** — thiếu một trong hai là `BLOCK`.
- **`--caption`** dài **7–20 từ** (công cụ từ chối ngoài dải này), gắn với ý của mục, không phải
  "Ảnh minh họa".
- **`--name`** không dấu, chữ thường, tả nội dung ảnh.

### 5. Chèn vào bài

Đặt ảnh **sau đoạn nói về nó**, trước heading kế tiếp. Có một dòng trống giữa ảnh và chú thích:

```markdown
![alt đúng như manifest](images/ten-file.jpg)

*chú thích đúng như manifest*
```

Alt và chú thích trong bài phải **giống hệt** manifest: `wp_draft.py` lấy chú thích từ manifest để
dựng `<figcaption>`, còn máy kiểm đọc chú thích từ bài.

Thêm `ImageObject` vào `schema_extra` trong front matter. Khai `ImageObject` mà bài không có ảnh là
`BLOCK`, và ngược lại có ảnh thì nên khai.

### 6. Chạy lại máy kiểm

```powershell
python scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json
python scripts/house_voice_check.py work/<slug>/article.md
```

Máy kiểm chặn (`BLOCK`) ba thứ: ảnh không có dòng manifest, dòng manifest chưa `CLEARED`, và ảnh
internet có giấy phép không dùng được hoặc thiếu thông tin ghi công.

Chú thích ảnh **không** tính vào các chỉ số giọng văn, vì kho bài thật cũng không tính. Nhưng nó
**có** tính vào giới hạn 230 chữ mỗi mục. Mục văn xuôi đã sát ngưỡng thì hai chú thích có thể đẩy
nó qua. Khi đó bạn giải trình trong `qa-report.md` kèm số chữ văn xuôi thật; đừng bỏ ảnh chỉ để
cảnh báo biến mất.

### 7. Ghi vào `qa-report.md`

Một mục **Ảnh** gồm: bảng vị trí → file → giấy phép → tác giả; ứng viên đáng chú ý đã loại và vì
sao; vị trí trong image plan còn trống và lý do. Thêm vào ghi chú cho người đăng bài: dòng ghi công
đã được `wp_draft.py` tự in dưới mỗi ảnh CC BY / CC BY-SA, **đừng xoá dòng đó** khi sửa bài trên
WordPress — xoá là vi phạm giấy phép của ảnh.

## Ghi công: vì sao không được bỏ

CC BY và CC BY-SA **bắt buộc** ghi tác giả, nguồn và giấy phép ở nơi ảnh xuất hiện. `wp_draft.py`
tự dựng dòng đó từ ba cột `creator`, `source_url`, `license_url` của manifest:

> Chuồn chuồn kim thân mảnh, khép cánh dọc thân khi đậu, ảnh chụp ở Bến Tre
> Ảnh: Charles J. Sharp / Wikimedia Commons, CC BY-SA 4.0

Dòng đó cũng được ghi vào chú thích của ảnh trong thư viện Media, vì ảnh có thể được chèn lại vào bài
khác từ thư viện. CC0 và Public Domain không bắt buộc ghi công nên không in.

## Khi không tìm được ảnh

Không tìm được ảnh đúng ngữ cảnh thì **để trống vị trí đó** và ghi vào `qa-report.md`, đừng lấy ảnh
"gần đúng" cho đủ số. Thứ tự dự phòng theo `docs/14` mục A2: sơ đồ tự dựng từ dữ liệu có nguồn, ảnh
đội ngũ tự chụp, ảnh của Muaban.net có xác nhận nội bộ. **Không bao giờ** dùng ảnh AI để minh họa một
địa điểm, giấy tờ hay công trình có thật — đó là quy tắc 1.
