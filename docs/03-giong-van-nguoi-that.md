# 03 — Giọng văn người thật

> **Đọc `docs/12-giong-nha-muaban.md` trước khi áp dụng Quy tắc 2 và phần kết bài của Quy tắc 3,
> và `docs/13-cu-phap-tieng-viet.md` trước khi sửa bất kỳ câu nào.**
> Tài liệu này mô tả giọng người thật nói chung, suy ra từ lý thuyết. Tài liệu 12 mô tả giọng của
> chính blog Muaban.net, đo từ 24 bài đang đăng — và ở hai chỗ đó, bài thật làm khác hẳn: blog viết
> câu dài và đều (trung bình 27 từ) chứ không giật cục, và blog **có** dùng công thức kết bài
> "Hy vọng... Đừng quên theo dõi Muaban.net". Khi mâu thuẫn, tài liệu 12 thắng vì nó có bằng chứng.

## Vì sao văn AI nghe ra ngay

**Bốn** lý do, xếp theo mức độ nặng:

1. **Không có thông tin cụ thể.** Không biết con số nào, không biết trường hợp nào, nên phải nói
   nguyên tắc chung. Nguyên tắc chung nói mãi thành sáo ngữ.
2. **Không gọi người đọc.** Lời khuyên được viết ở dạng mệnh lệnh không chủ ngữ — "Nên hỏi chủ
   trọ...", "Hãy kiểm tra công tơ..." — thay vì "Bạn nên hỏi chủ trọ...". Đọc lên nghe như văn
   bản hướng dẫn nội bộ, không như một người đang nói với một người. Xem quy tắc 6 và
   `docs/13-cu-phap-tieng-viet.md`.
3. **Cú pháp dịch.** Câu nói ngược so với cách người Việt nói: động từ bị biến thành danh từ
   ("việc xác định giá đất"), chủ ngữ là một cụm trừu tượng ("Điều này cho thấy..."), mệnh đề phụ
   dài dồn lên trước nòng cốt câu. Chi tiết và cách sửa ở `docs/13-cu-phap-tieng-viet.md`.
4. **Không có lập trường.** Không dám nói cái nào hơn cái nào, không dám nói "đừng làm thế",
   không dám nói "chỗ này tôi cũng không chắc".

Sửa được bốn thứ đó thì bài tự nghe như người viết. Không sửa được thì mọi thủ thuật "nhân hóa"
chỉ là trang trí.

> **Lý do số 2 và số 3 được thêm vào sau.** Tài liệu này từng mở đầu bằng câu "Không phải vì ngữ
> pháp", và câu đó đã khóa cả bộ kiểm của dự án: không một script nào đo cú pháp hay xưng hô, tất
> cả chỉ đo **từ vựng** và **độ dài**. Khi chủ dự án nhận xét bài "không giống tiếng Việt" và
> "cấu trúc nói ngược giống tiếng nước ngoài", máy kiểm không có gì để trả lời. Một tiền đề sai
> ở một dòng tài liệu đã làm cả bộ đo mù đúng chỗ cần thấy.

> **Lưu ý về công cụ dò AI:** các bộ dò hiện có độ chính xác không ổn định, hay báo nhầm văn người
> thật, và **không phải** tín hiệu xếp hạng của Google. Không lấy điểm detector làm mục tiêu và
> không viết méo mó đi chỉ để né detector. Mục tiêu là bài có ích và đọc trôi.

---

## Quy tắc 1 — Cụ thể đánh bại chung chung

| Thay vì | Viết |
|---|---|
| "Giá bất động sản khu vực này có xu hướng tăng" | "Giá chào bán căn hộ ở Bình Tân trên Muaban.net quý II/2026 phổ biến 38–45 triệu/m², cao hơn quý I khoảng 3%" *(kèm nguồn, số tin)* |
| "Thủ tục tương đối phức tạp" | "Hồ sơ gồm 5 loại giấy tờ, nộp một cửa tại Văn phòng đăng ký đất đai, thời gian giải quyết 10 ngày làm việc" |
| "Bạn nên cân nhắc kỹ trước khi mua" | "Trước khi đặt cọc, **bạn nên** yêu cầu bên bán cho xem bản gốc sổ và tra cứu tình trạng thế chấp tại văn phòng đăng ký. Hai việc này tốn một buổi nhưng chặn được phần lớn rủi ro" |
| "Nhiều chuyên gia cho rằng..." | Nêu tên người, nơi phát biểu, ngày — hoặc bỏ hẳn câu đó |

**Nếu không có dữ liệu để viết cụ thể, đó là tín hiệu thiếu nghiên cứu, không phải tín hiệu cần
viết chung chung hơn.** Quay lại evidence ledger.

> **Đọc kỹ dòng thứ ba của bảng.** Chỗ sai của câu bên trái là *"cân nhắc kỹ"* — một lời khuyên
> rỗng, không nói được phải làm gì. Chỗ sai **không phải** là hai chữ *"Bạn nên"*. Bản viết lại
> vì thế **giữ nguyên "bạn nên"** và chỉ thay phần rỗng bằng việc cụ thể.
>
> Trước đây bản viết lại ở đây là một câu không có chủ ngữ ("Trước khi đặt cọc, yêu cầu bên
> bán..."), nên bài học agent rút ra từ bảng này là "thay *Bạn nên X* bằng mệnh lệnh không chủ
> ngữ". Đó chính là lỗi mà chủ dự án đã chỉ ra: bài "chưa có danh xưng của người đọc". Một ô
> trong một bảng ví dụ đủ sức dạy sai cả một quy tắc.

## Quy tắc 2 — Nhịp không đều

Văn người thật có câu 5 chữ đứng cạnh câu 30 chữ. Văn máy thì câu nào cũng 18–22 chữ.

- Cho phép câu rất ngắn để nhấn: *"Không nộp được."* *"Chỗ này hay sai."*
- Đoạn văn từ 1 đến 5 câu, thay đổi liên tục. Đoạn một câu là hợp lệ.
- Không phải mục nào cũng cần bullet. Trộn đoạn văn, bảng, danh sách đánh số theo đúng nhu cầu.
- Danh sách không cần đều số lượng. Mục này 2 ý, mục kia 6 ý, miễn là đúng.

> **Ba ngưỡng nhịp câu của quy tắc này đã bị bỏ khỏi `human_voice_check.py`.** Đo trên kho bài
> thật cho thấy blog viết câu **dài và đều** — trung bình 27 từ, gần như không dùng câu dưới 10
> từ — nên ba ngưỡng cũ đòi văn giật cục là đòi sai. Quyền đo nhịp câu nay thuộc
> `house_voice_check.py` với dải lấy từ chính bài thật. Quy tắc 2 vẫn đúng ở phần **đoạn** và
> **danh sách**: đoạn dài ngắn xen kẽ, danh sách không cần đều số lượng.

## Quy tắc 3 — Cắt sáo ngữ

Danh sách đầy đủ ở `scripts/lexicon/ai_phrases.json`, được script kiểm tự động. Nhóm chính:

**Mở đầu rỗng** — "Trong bối cảnh...", "Trong thời đại ngày nay...", "Với sự phát triển không ngừng của...",
"Không thể phủ nhận rằng...", "Có thể nói rằng...", "Như chúng ta đã biết..."
→ Cắt thẳng. Bắt đầu bằng thông tin.

**Nối câu công nghiệp** — "Bên cạnh đó", "Ngoài ra", "Hơn nữa", "Đồng thời", "Chính vì vậy",
"Do đó", "Tuy nhiên" dùng ở đầu mọi đoạn.
→ Giữ lại tối đa vài lần trong bài, ở chỗ thật sự cần nối logic. Phần lớn xóa đi câu vẫn đứng được.

**Khen suông** — "đóng vai trò quan trọng", "góp phần không nhỏ", "mang lại nhiều lợi ích",
"vô cùng cần thiết", "là yếu tố then chốt", "không thể thiếu".
→ Thay bằng việc nó làm được gì cụ thể.

**Sáo ngữ bất động sản** — "vị trí đắc địa", "tiềm năng tăng giá bền vững", "an cư lạc nghiệp",
"kênh đầu tư hấp dẫn", "cơ hội vàng", "đón đầu xu hướng", "điểm sáng thị trường", "cú hích",
"đòn bẩy tài chính" (khi không giải thích), "sinh lời hấp dẫn".
→ Phần lớn là ngôn ngữ quảng cáo. Ngoài việc nghe như máy, nó còn vi phạm quy tắc không hứa hẹn.

**Kết bài đóng hộp** — "Hy vọng bài viết đã cung cấp cho bạn những thông tin hữu ích",
"Chúc bạn thành công", "Tóm lại, có thể thấy rằng...", "Trên đây là toàn bộ thông tin về...".
→ Thay bằng bước tiếp theo cụ thể người đọc làm được ngay.

**Cấu trúc lặp** — "không chỉ ... mà còn", "vừa ... vừa ...", bộ ba tính từ
("nhanh chóng, hiệu quả và tiết kiệm").
→ Đếm lại trên 24 bài thật: 8 bài dùng, nhiều nhất **4 lần** một bài. Đây là cấu trúc liên kết
bản địa của tiếng Việt, không phải dấu vết máy, nên ngưỡng `repetitive_structures` đã nâng từ 2
lên 4. Dùng được, chỉ đừng lặp quá dày. Riêng **bộ ba tính từ** thì vẫn cắt.

## Quy tắc 4 — Có lập trường, có giới hạn

Văn người thật dám nói:

- **Khuyên ngược:** *"Nếu bạn chỉ có 15% giá trị căn nhà, đừng vay. Áp lực trả nợ 20 năm không đáng."*
- **Nói thẳng cái dở:** *"Mặt bằng tầng hầm rẻ hơn 20% nhưng rất khó cho thuê lại, nên coi là chi phí chìm."*
- **Thừa nhận không biết:** *"Mức phí này mỗi chi nhánh áp dụng khác nhau; chúng tôi chưa tìm được
  văn bản công bố thống nhất, bạn cần hỏi trực tiếp."*
- **Nêu điều kiện thay vì nói chung chung:** *"Đúng với nhà riêng lẻ đã có sổ. Nhà trong dự án chưa
  bàn giao thì quy trình khác hẳn."*

Đây cũng là tín hiệu Trust trong E-E-A-T: minh bạch về giới hạn đáng tin hơn giọng chắc nịch.

**Ranh giới:** lập trường phải là **diễn giải từ dữ kiện có nguồn**, không phải trải nghiệm bịa.
Được viết *"Với mức lãi suất thả nổi hiện tại, khoản vay 20 năm khiến tổng lãi vượt 70% gốc, con số
này thường khiến người vay bất ngờ."* Không được viết *"Tôi từng tư vấn cho một khách hàng..."* nếu
không có ca thật đã được xác minh và đồng ý.

## Quy tắc 5 — Đánh dấu rõ loại phát ngôn

Người đọc phải phân biệt được bốn thứ. Dùng từ ngữ khác nhau:

| Loại | Cách viết | Ví dụ |
|---|---|---|
| Dữ kiện | Khẳng định + nguồn + ngày | "Lệ phí trước bạ nhà đất là 0,5% (theo Nghị định ..., ngày ...)" |
| Diễn giải | "có thể lý giải", "cách hiểu là", "số này nói lên" | "Mức chênh này có thể do nguồn cung thứ cấp tăng" |
| Dự báo | "nếu ... thì", nêu điều kiện | "Nếu lãi suất giữ nguyên tới cuối năm, áp lực trả nợ sẽ..." |
| Trải nghiệm | Chỉ khi có bằng chứng và được phép | ghi rõ ai, khi nào, quan sát gì |

Không được trộn: một dự báo viết ở thể khẳng định trở thành thông tin sai.

## Quy tắc 6 — Viết như đang trả lời một người

Trước khi viết mỗi mục, tự hỏi: *người đọc vừa hỏi gì để tôi viết đoạn này?* Nếu không hình dung
được câu hỏi, đoạn đó không cần tồn tại.

Xưng hô: **"bạn" cho người đọc, và "bạn" phải là chủ ngữ của mọi câu khuyên** — "Bạn nên hỏi chủ
trọ...", không phải "Nên hỏi chủ trọ...". Đây là quy tắc 17 trong `CLAUDE.md`, và
`house_voice_check.py` chặn bài có dưới 50% câu khuyên gọi người đọc.

Thương hiệu tự xưng ở **ngôi thứ ba** trong thân bài — "Muaban.net", "Mua Bán". Chỉ dùng
**"chúng tôi"** ở đúng hai chỗ: khối minh bạch khi nói về phương pháp hoặc giới hạn ("chúng tôi
chưa tìm được văn bản công bố thống nhất"), và câu kêu gọi cuối bài. Không dùng "tôi" nếu chưa
có tác giả thật đứng tên, và không dùng "mình" để chỉ người đọc.

## Quy tắc 7 — Định dạng phục vụ việc đọc, không phải trang trí

- **In đậm** để người đọc lướt nhanh bắt được ý, tối đa vài lần mỗi mục. Không bôi đậm cả câu.
- Bảng chỉ dùng khi thật sự so sánh từ 2 chiều trở lên. Bảng một cột là danh sách.
- Emoji: không dùng trong bài bất động sản.
- Dấu gạch ngang dài (—): dùng được nhưng đừng thay mọi dấu phẩy bằng nó. Script sẽ cảnh báo nếu lạm dụng.
- Không lặp lại tiêu đề bài ở câu đầu tiên của thân bài.

---

## Quy trình tự sửa sau khi có bản nháp

Chạy đúng thứ tự, đừng gộp:

1. **Lượt dữ kiện.** Đối chiếu từng câu có số, ngày hoặc tên riêng với evidence ledger. Câu nào không
   truy được về một `claim_id` thì xóa hoặc thu hẹp.
2. **Lượt cắt.** Xóa mọi câu không thêm thông tin. Thường cắt được 15–25% bản nháp đầu.
   Mục tiêu là bài ngắn hơn và đặc hơn.
3. **Lượt sáo ngữ.** Chạy `python scripts/human_voice_check.py work/<slug>/article.md` và xử lý từng
   cảnh báo. Không thay sáo ngữ này bằng sáo ngữ khác; cắt hẳn hoặc viết lại bằng thông tin cụ thể.
4. **Lượt nhịp.** Đọc thành tiếng. Chỗ nào hụt hơi thì cắt câu; chỗ nào cụt lủn liên tục thì nối.
   Kiểm tra độ dài đoạn có thay đổi không.
5. **Lượt lập trường.** Mỗi mục lớn có ít nhất một câu nói rõ điều gì nên làm, không nên làm, hoặc
   chỗ nào cần thận trọng.
6. **Lượt người đọc.** Đọc lại từ đầu với vai người mua nhà lần đầu. Chỗ nào phải đọc hai lần thì viết lại.

## Bảng đối chiếu nhanh

| Dấu hiệu máy viết | Cách sửa |
|---|---|
| Mở bài dẫn dắt 3 câu mới vào việc | Xóa, bắt đầu bằng câu trả lời |
| Mục nào cũng đúng 3 bullet | Cho số lượng khác nhau theo nội dung thật |
| Câu nào cũng khoảng 20 chữ | Chèn câu ngắn, gộp câu dài |
| "Bên cạnh đó" mở 4 đoạn liên tiếp | Xóa 3 cái, nối lại bằng nội dung |
| Toàn tính từ, không có số | Quay lại nghiên cứu, bổ sung dữ liệu có nguồn |
| Không câu nào dám khuyên | Thêm khuyến nghị có điều kiện |
| Kết bài chúc may mắn | Thay bằng checklist hoặc bước tiếp theo |
| Lặp từ khóa ở mọi heading | Viết heading thành câu hỏi thật |

## Sửa thế nào

Tài liệu này mô tả giọng **đúng**; `scripts/human_voice_check.py` **báo** chỗ sai. Phương pháp
**sửa** nằm ở skill `humanizer-bds` — quy trình bốn bước (đánh dấu, viết nháp, đối chiếu, chốt)
thích ứng từ [blader/humanizer](https://github.com/blader/humanizer) (MIT).

Điểm quan trọng nhất của bản thích ứng: nó **khoá** hai pattern của bản gốc lại. Bản gốc bảo cắt
bớt từ rào đón và bỏ câu rào về giới hạn thông tin; ở đây mọi câu nêu phạm vi áp dụng, mốc dữ
liệu, giới hạn và khuyến nghị tham vấn đều **giữ nguyên**, vì `evidence_check.py` đòi đủ bốn tín
hiệu YMYL. Viết lại mà cắt chúng thì bài FAIL máy kiểm.
