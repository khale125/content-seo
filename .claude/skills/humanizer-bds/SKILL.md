---
name: humanizer-bds
description: "Viết lại đoạn văn nghe như máy thành văn người thật, mà không đổi nội dung và không thêm dữ kiện. Dùng khi human_voice_check.py báo sáo ngữ, khi bài đọc trôi nhưng rỗng, hoặc khi người dùng nói: viết lại cho tự nhiên, bỏ giọng AI, humanize, nghe như máy, sửa giọng văn, đoạn này khô quá. Thích ứng từ blader/humanizer (MIT) cho nội dung bất động sản tiếng Việt."
---

# Viết lại giọng máy thành giọng người

`human_voice_check.py` **chỉ báo lỗi**. Skill này **sửa**. Đó là toàn bộ khác biệt, và cũng là lý do
nó tồn tại: trước đây agent biết câu nào hỏng nhưng không có phương pháp sửa, nên hay thay sáo ngữ
này bằng sáo ngữ khác.

Nguồn gốc: [blader/humanizer](https://github.com/blader/humanizer) (MIT) và Wikipedia
["Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). Bản này đã cắt
phần không áp dụng cho tiếng Việt và **khoá lại hai chỗ đánh nhau với quy tắc YMYL**.

## Bốn rào cứng — đọc trước khi sửa một chữ

Bản gốc viết cho văn phổ thông. Dự án này viết nội dung YMYL có cổng duyệt và có máy đối chiếu
bằng chứng, nên bốn rào dưới đây đứng trên mọi pattern.

**0. Đây là văn tiếng Việt cho người Việt đọc** (quy tắc 16). Bản gốc `blader/humanizer` viết cho
văn tiếng Anh, nơi từ nối bị coi là thừa. Tiếng Việt thì ngược lại: "tuy nhiên", "vì vậy",
"ngoài ra" là thứ **nối câu trước với câu sau**, và cắt chúng đi là cách nhanh nhất để bài thành
một chuỗi câu rời rạc. Bài thật dùng 3,5–8,7 cụm nối trên 1.000 từ. Muốn gọn thì gộp hai câu
thành một câu có mệnh đề phụ, **đừng cắt cụm nối**.

**1. Không thêm bất kỳ dữ kiện nào.** Hard rule 1. Không thêm số, ngày, tên văn bản, tên dự án, URL,
trích dẫn, trải nghiệm. Nếu câu viết lại cần một chi tiết bạn không có, **viết câu đơn giản hơn**,
đừng lấp. Nhận định và lập trường thì được, miễn suy ra từ dữ kiện đã có nguồn.

**2. Không chạm vào bảy thứ này.** Chỉ sửa văn xuôi:

| Không chạm | Vì sao |
|---|---|
| Front matter (`title`, `meta_description`, `slug`, `schema`) | `onpage_check.py` đo trực tiếp |
| Tên văn bản, số hiệu, điều khoản được dẫn trong câu | Đó là cách bài thật dẫn nguồn; mất là mất truy xuất |
| Mọi con số, ngày, tỷ lệ, số hiệu văn bản | Đổi một chữ số là bịa đặt |
| **Khối minh bạch** (mốc dữ liệu, phạm vi, giới hạn, tham vấn, căn cứ) | Bắt buộc với YMYL |
| Link map và anchor | Phải khớp với `outline.md` |
| Bảng, khối code, đường dẫn, URL | Không phải văn xuôi |
| Tiêu đề nhận truy vấn chính | `outline_check` và `onpage_check` đều đo |

**3. Hai pattern của bản gốc bị khoá ở đây.**

- **§9 Cắt bớt từ rào đón** — bản gốc bảo cắt. Ở đây **giữ nguyên** mọi câu nêu phạm vi áp dụng, mốc
  thời gian, giới hạn và khuyến nghị tham vấn. `evidence_check.py` đòi đủ bốn tín hiệu YMYL; cắt
  chúng làm bài **FAIL** máy kiểm. Chỉ cắt khi rào đón chồng lên nhau vô nghĩa ("có thể có khả năng
  là đôi khi").
- **§23 Bỏ câu rào về giới hạn thông tin** — chỉ áp dụng cho câu rào **mơ hồ, không nguồn** ("tính
  đến thời điểm hiện tại"). Câu mốc dữ liệu **có ngày cụ thể** ("cập nhật tới 15/09/2026") là bắt
  buộc, giữ nguyên. Riêng phần "không bao giờ trình bày phỏng đoán như dữ kiện" thì áp dụng tuyệt
  đối — nó trùng với hard rule 1.

**3b. Không chạm vào danh xưng người đọc.** Quy tắc 17: mọi câu khuyên phải lấy **"bạn"** làm chủ
ngữ. Viết lại cho "gọn" mà cắt mất chữ "bạn" là làm hỏng đúng thứ dự án vừa sửa — cụ thể, đừng đổi
*"Bạn nên hỏi chủ trọ..."* thành *"Nên hỏi chủ trọ..."*. Sáu phép sửa cú pháp nằm ở skill
`giong-muaban-bds` và `docs/13-cu-phap-tieng-viet.md`.

**4. Sửa xong phải chạy lại máy kiểm.** Viết lại có thể vô tình làm mất tín hiệu YMYL hoặc làm một
con số mất neo ledger:

```powershell
python scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json
```

Còn `BLOCK` thì chưa xong.

## Quy trình bốn bước

**1. Đánh dấu.** Đọc hết một lượt, đánh dấu mọi pattern, mạnh trước. Nhìn cả hình dạng đoạn chứ không
chỉ câu: một tương phản trải dài hai câu, ba ví dụ song song, cùng một câu chốt sau mỗi mục — đều là
cùng một lỗi ở quy mô lớn hơn.

**2. Viết nháp.** Giữ mọi claim có nguồn. Được rút gọn, gộp hoặc tách đoạn, đổi cấu trúc, nhưng không
mất thông tin. Khi gộp hai câu cùng dẫn nguồn, **giữ đủ tên cả hai văn bản**.

**3. Đối chiếu.** Đọc to, rồi hỏi hai câu:

- Bản mới có **thêm** dữ kiện nào không có trong ledger không? Thêm là lỗi.
- Bản mới có **mất** claim, số, ngày hay tên văn bản nào không? Mất là lỗi, trừ khi chính pattern
  yêu cầu cắt.

Rồi tìm năm thứ hay sống sót qua một lượt viết lại: tương phản rỗng, câu chốt một dòng, gạch ngang
dài, bộ ba, nhãn in đậm.

**4. Chốt.** Nói thẳng từng ý thay vì vá từng cụm bị đánh dấu. Câu nào vẫn gượng thì viết lại cả đoạn
quanh ý chính của nó. Câu ngắn đứng cạnh câu dài.

## Giọng để bám theo

Người dùng đưa mẫu văn thì **mẫu thắng mọi quy tắc bên dưới**, kể cả quy tắc gạch ngang.

Không có mẫu thì bám **`reference/muaban-blog/`** — kho 24 bài thật đang đăng trên blog, kèm số đo
văn phong ở `docs/12-giong-nha-muaban.md`. Bám nhịp câu, cách mở mục, cách khuyên. **Đừng chép nội
dung của chúng.**

Trước đây mục này trỏ tới `examples/fixture-dat-chuan/article.md`. Đó là văn giả lập do agent viết,
và đo ra thì nó lệch giọng thật còn nhiều hơn cả bài đang bị chê cứng — 31% câu ngắn so với 2,8% của
bài thật. Fixture nay đã được viết lại theo giọng nhà, nhưng **kho bài thật mới là mẫu gốc**.

Sửa xong bằng skill này thì chạy tiếp `giong-muaban-bds` để nắn vào khuôn tòa soạn (quy tắc 15).

## 25 pattern, chia theo tình trạng trong dự án

### Nhóm A — máy đã bắt, bạn chỉ cần biết sửa thế nào

| Pattern gốc | Máy bắt bằng |
|---|---|
| §22 Tàn dư chatbot | `ai_artifacts` (BLOCK) |
| §17 Viện dẫn mơ hồ | `vague_authority` (BLOCK) |
| §16 Ngôn ngữ bán hàng | `hype_marketing`, `re_cliches` |
| §4 Vào đề vòng vo | `empty_openers` |
| §2 Câu chốt sáo | `closing_boilerplate` + kiểm `closer` |
| §6 Bộ ba gượng | kiểm bộ ba "A, B và C" |
| §7 Mở câu lặp | `MAX_SAME_OPENER` |
| §8 Gạch ngang dài | `MAX_EMDASH_PER_1000` |
| §19 In đậm trang trí | `MAX_BOLD_RATIO` + kiểm danh sách nhãn |
| §20 Tiêu đề trang trí | kiểm emoji + kiểm mũi tên |
| §24 Tiêu đề lặp ở câu đầu | kiểm trùng H1 |

### Nhóm B — mới thêm vào máy từ bản thích ứng này

| Pattern | Category | Ví dụ tiếng Việt |
|---|---|---|
| §1 Tương phản rỗng | `hollow_contrast` | "Đây không phải chi phí mà là khoản đầu tư" |
| §3 Câu nghe sâu sắc | `deep_sounding` | "về bản chất", "câu hỏi đặt ra là", "mấu chốt nằm ở" |
| §5 Cãi với người không có mặt | `straw_man` | "nói vậy không có nghĩa là", "thoạt nghe có vẻ" |
| §18 Né động từ "là" | `nominal_verbs` | "dự án sở hữu mặt tiền", "đóng vai trò là" |
| §23 Rào trước rồi đoán | `hedged_guess` | "tính đến thời điểm hiện tại", "nhiều khả năng là" |
| §14 Liên hệ mơ hồ | `vague_link` | "gắn liền với", "có mối liên hệ mật thiết" |
| **Cú pháp dịch** | `translated_syntax` | "điều này cho thấy", "nhằm mục đích", "trên cơ sở", "được thực hiện" — 13 cụm, 24/24 bài thật dùng **0** lần |

Ngưỡng nằm trong `scripts/lexicon/ai_phrases.json`. **Đừng nới ngưỡng để bài qua cửa** — sau mỗi lần
sửa lexicon, chạy lại ba fixture bài viết trong `examples/`.

### Nhóm C — không chuyển sang tiếng Việt được, bỏ qua

- **§10 Cụm gạch nối** (`data-driven`, `cross-functional`) — tiếng Việt không có dạng này.
- **§21 Dấu nháy cong** — quy ước sắp chữ tiếng Anh. Tiếng Việt dùng nháy cong là bình thường, và
  `supporting_quote` trong ledger cũng vậy.
- **§25 Viết về phiên bản cũ** — **ngược lại** ở đây. Bài `url_decision: UPDATE` thường **phải** nói
  rõ quy định cũ khác quy định mới chỗ nào; đó chính là lý do bài được cập nhật. Đừng cắt.
- **§11 Câu bị động** — tiếng Việt ít bị động hơn tiếng Anh, "được" thường là cấu trúc bình thường
  chứ không phải dấu vết máy. **Đã đo lại và giữ nguyên quyết định này:** bài thật dùng bị động
  hành chính tới 4,5 lần trên 1.000 từ ở các bài pháp lý, còn bài của agent dùng *ít hơn*.
  `passive_admin_per_1000` chỉ được đo để theo dõi, không có ngưỡng. Chỉ đổi sang chủ động khi
  **biết rõ ai là người làm**; không biết thì để nguyên.

## Ví dụ

**Tương phản rỗng (§1)**

> Trước: Đây không chỉ là chi phí phải nộp, mà là khoản đầu tư cho giá trị lâu dài của thửa đất.
>
> Sau: Theo Nghị quyết 254/2025/QH15, tiền sử dụng đất là khoản phải nộp một lần khi chuyển mục đích.

**Né động từ "là" (§18)**

> Trước: Thửa đất sở hữu vị trí giáp đường lớn, đóng vai trò là yếu tố quyết định giá đất ở.
>
> Sau: Thửa đất giáp đường lớn nên giá đất ở trong bảng giá cao hơn [C06].

**Rào trước rồi đoán (§23)**

> Trước: Tính đến thời điểm hiện tại, nhiều khả năng mức thu sẽ được điều chỉnh trong năm nay.
>
> Sau: Thông tin cập nhật tới 15/09/2026. Chưa có văn bản nào công bố việc điều chỉnh mức thu.

**Câu chốt lặp (§2)**

> Trước: ...nên cân nhắc kỹ. Đó mới là điều đáng bàn.
>
> Sau: (cắt câu chốt, kết ở dữ kiện cuối cùng)

## Khi nào KHÔNG sửa

Mỗi pattern mô tả một lựa chọn mặc định, và người thật có thể cố ý chọn đúng như vậy. Pattern yếu chỉ
tính khi nhiều dấu hiệu tụ lại trong cùng một đoạn. Để yên khi cụm từ nằm trong **trích dẫn nguyên
văn**, trong tên riêng, trong tên văn bản pháp luật, hoặc trong đoạn đang bàn về chính cụm từ đó.

Giữ những thứ mang giọng người, trừ khi chúng làm hỏng nghĩa:

- Chi tiết cụ thể và bất thường: một con số lẻ, một câu hỏi thật của người đọc, một mốc thời gian lạ.
- Cảm nhận chưa dứt khoát: "chỗ này tôi thấy chưa thuyết phục, nhưng chưa có số để nói chắc".
- Một lựa chọn ngôi thứ nhất mà người viết giải thích được.
- Lời tự đính chính, ngoặc đơn, câu chen ngang thật.

**Bỏ dấu vết máy mới chỉ là một nửa.** Nửa còn lại là bản viết lại phải nghe như người thật viết.

## Chế độ trả về

- **Đoạn dán vào hội thoại:** trả bản nháp, danh sách pattern còn sót, rồi bản chốt.
- **Sửa file:** chạy đủ bốn bước nhưng **chỉ ghi bản chốt** vào file, rồi tóm tắt đã đổi gì. Chạy lại
  `run_qa.py` và báo kết quả.
- **Gọi từ skill khác** (`seo-writer-bds` lượt 3): chỉ trả văn bản đã chốt.
