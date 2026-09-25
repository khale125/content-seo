---
name: giong-muaban-bds
description: "Viet bai theo dung giong cua blog Muaban.net that, do bang so chu khong bang cam tinh. Goi nguoi doc la 'ban' va dat 'ban' lam chu ngu cua moi cau khuyen; sua cau noi nguoc kieu dich (danh tu hoa, chu ngu tru tuong, menh de phu don len truoc); ap cong thuc sapo, cach mo muc, muc dan ve tin dang va doan ket cua toa soan; giu nhip cau dai va deu thay vi cau cut. Dung khi nguoi dung noi: viet theo giong Muaban.net, giong nha, bai doc cung qua, dien dat cung, khong giong tieng Viet, cau truc noi nguoc, thieu danh xung nguoi doc, hoac khi house_voice_check.py bao lech."
---

# Giọng nhà Muaban.net

Skill này trả lời đúng một câu hỏi: **bài này có giống bài đang đăng trên
`muaban.net/blog/nha-dat/` không?**

Đó là câu hỏi hẹp hơn `humanizer-bds`. Skill kia hỏi "văn có giọng máy không" và sửa theo
quy tắc chung cho mọi văn bản tiếng Việt. Skill này hỏi "văn có giọng **tòa soạn này**
không" và sửa theo một khuôn cụ thể đo được từ bài thật.

Hai skill không thay thế nhau. Thứ tự đúng: `humanizer-bds` gỡ dấu vết máy trước,
`giong-muaban-bds` nắn vào khuôn nhà sau.

## Vì sao skill này tồn tại

Bài 001 của dự án bị người duyệt từ chối ba lần, lần cuối với nhận xét *"cách diễn đạt vẫn
đang rất cứng"*. Đo ra thì nguyên nhân không mơ hồ chút nào:

| Chỉ số | Bài 001 | Blog thật (p10–p90) |
|---|---|---|
| Độ dài câu trung bình | 17,9 từ | 22,3 – 28,8 |
| Tỷ lệ câu ngắn (≤10 từ) | **25,3%** | 1,0% – 15,1% |
| Tỷ lệ câu dài (≥35 từ) | 7,2% | 11,8% – 28,0% |
| Độ dài đoạn trung bình | 36,3 từ | 40,4 – 64,7 |

Bài viết bằng những câu cụt đặt cạnh nhau — "Cộng ba kết quả lại là ra.", "Đừng mặc định
chọn thửa to nhất." — trong khi blog viết câu dài, đều, có mệnh đề phụ. **Đó chính là chữ
"cứng".**

Trớ trêu là bộ kiểm cũ đã *thưởng* cho lối viết đó: `human_voice_check.py` từng đòi
`burstiness ≥ 0,38` và `tỷ lệ câu ngắn ≥ 12%`, trong khi bài thật có trung vị lần lượt là
**0,33** và **2,8%**. Một bài Muaban.net thật sẽ trượt chính bộ kiểm của dự án. Nay
`house_voice_check.py` sở hữu phần nhịp câu, còn `human_voice_check.py` đã bỏ ba ngưỡng đó.

## Đọc trước

1. `CLAUDE.md` — đặc biệt quy tắc 14 (cấu trúc) và 15 (giọng nhà)
2. `docs/12-giong-nha-muaban.md` — bản đầy đủ, có nguồn gốc từng con số
3. `reference/muaban-blog/` — **kho 24 bài thật**. Đọc ít nhất hai bài trước khi viết, ưu tiên bài cùng loại với bài đang làm.
   Không bài nào trong đây do agent viết ra.

## Khuôn bài

Cấu trúc lấy theo sheet format nội bộ (quy tắc 14), **không** lấy theo bài cũ trên blog:

```
## <câu dẫn đầu tiên của sapo>        ← sapo nằm ở H2, không để nguyên chữ "Sapo"
### I. <mục chính>
#### 1. <mục con>
### II. <mục chính>
### V. Tìm <loại hình> <địa bàn> trên Muaban.net   ← bắt buộc, áp chót
### Lời kết
## Phạm vi, căn cứ và giới hạn
```

Một H2 duy nhất, mục chính ở **H3 đánh số La Mã**, mục con ở **H4 đánh số Ả Rập**.
Cả 24 bài thật đều đúng hình này — đã đối chiếu trên HTML gốc, không phải qua bản chuyển
markdown. Bản chuyển làm lệch cấp heading một bậc và từng khiến chính tôi kết luận sai rằng
blog khác sheet.

Hai chỗ bài thật làm khác mà dự án **vẫn giữ theo sheet**: 0/12 bài có mục `Lời kết`, và
12/12 bài có mục lục. Dự án giữ `Lời kết`, bỏ mục lục. Đây là lựa chọn của chủ dự án,
không phải sơ suất — đừng "sửa lại cho giống blog".

## Sáu công thức của tòa soạn

### 1. Sapo — ba câu, câu cuối mời đọc kèm tên thương hiệu

Câu 1 nêu bối cảnh hoặc nhu cầu. Câu 2 nêu cái khó hoặc sự đa dạng. Câu 3 hứa bài sẽ giúp gì.

> Thủ Đức là khu vực tập trung nhiều trường đại học, Khu Công nghệ cao TP.HCM và các khu dân
> cư lớn, nên nhu cầu thuê phòng trọ luôn duy trì ở mức cao. Thị trường có nhiều lựa chọn với
> mức giá và tiện ích khác nhau tùy từng khu vực. Trước khi quyết định thuê, bạn nên tìm hiểu
> kỹ về vị trí, chi phí và điều kiện sinh hoạt để chọn được phòng phù hợp với nhu cầu.

Biến thể câu cuối, nguyên văn từ kho: *"Bài viết dưới đây của Muaban.net sẽ cập nhật đầy đủ
các thông tin mới nhất giúp bạn nắm rõ những thay đổi liên quan."* · *"Cùng Mua Bán tìm hiểu
toàn bộ nội dung này qua những thông tin sau đây!"*

Với bài YMYL, câu 3 vẫn phải mang **phạm vi và mốc thời gian** (quy tắc 3). Ghép được cả hai
vào một câu là đạt.

### 2. Mở mục — danh từ chủ đề đứng đầu câu, rồi gọi người đọc ngay sau

Câu **đầu** của mục đặt chủ thể lên trước, không mở bằng câu cụt. Bài thật hay mở bằng
`<chủ thể> + là/có + ...`:

> Thủ Đức có nguồn cung phòng trọ phong phú, từ phòng giá rẻ dành cho sinh viên đến căn hộ
> mini cho người đi làm.

Nhưng **chỉ câu đầu tiên**. Từ câu thứ hai trở đi, mục phải nói với người đọc, và **mỗi mục
chính cần ít nhất một câu lấy "bạn" làm chủ ngữ của lời khuyên** (quy tắc 17). Bản trước của
skill này viết "Không mở mục bằng một câu cụt hay một mệnh lệnh", và câu đó bị hiểu rộng thành
"đừng dùng cầu khiến", nên cả mục thành văn trình bày:

> Sai: Khu này đông sinh viên nên nguồn phòng nhiều. Nên đi xem sớm vì phòng tốt hết nhanh.
> Đúng: Khu này đông sinh viên nên nguồn phòng nhiều. Tuy nhiên, **bạn nên** đi xem sớm, vì
> những phòng tốt thường hết ngay đầu học kỳ.

### 3. Câu khuyên — dày, nhưng nhẹ giọng

Đo lại trên 24 bài thật: trung vị **9 câu khuyên trên 1.000 từ**, và **48% trong số đó lấy
"bạn" làm chủ ngữ**. Khuôn của tòa soạn rất đều:

> **trạng ngữ → "bạn" → động từ khuyên → việc cụ thể**
>
> *"Trước khi đặt cọc, **bạn cần hỏi** rõ giá điện, nước, internet, phí gửi xe, phí rác."*
> *"Với những khu trọ đông người thuê, **bạn nên kiểm tra** camera, khóa cổng, khu vực để xe."*
> *"**Bạn chỉ nên đặt cọc** sau khi đã xem phòng trực tiếp."*

Khuôn được dùng: *"Bạn nên..."*, *"Bạn cần..."*, *"Bạn chỉ nên..."*, *"Bạn cũng nên..."*,
*"Nếu bạn..."*, *"Lưu ý..."*.

**Mệnh lệnh không chủ ngữ là lỗi**, không phải một biến thể: *"Nên hỏi chủ trọ..."*,
*"Hãy kiểm tra công tơ..."*. Dự án đặt ngưỡng `BLOCK` khi dưới 50% câu khuyên gọi người đọc —
xem quy tắc 17 và `docs/13-cu-phap-tieng-viet.md`. Bài 001 từng đạt mọi lượt kiểm khác mà chỉ
có 10%, và đó đúng là bài bị chê "kém tự nhiên".

Giọng cảnh báo **nhẹ**, thiên về nhắc nhở thủ tục. Bài thật không dọa người đọc. Câu như
"Sai chỗ này thì mọi phép tính sau đều sai" là quá gắt so với khuôn nhà.

### 4. Xưng hô

"bạn" xuyên suốt, trung vị **6,4 lần trên 1.000 từ** (đo lại trên 24 bài). Không dùng
**"mình"** để chỉ người đọc — bài thật gần như không dùng, trong khi bài 001 dùng 9 lần
("cơ sở mình học"); viết "cơ sở **bạn** học". Không "tôi" nếu chưa có tác giả thật đứng tên.

Thương hiệu tự xưng ở **ngôi thứ ba** trong thân bài — "Muaban.net", "Mua Bán". **"Chúng tôi"**
dùng ở đúng hai chỗ: **khối minh bạch** khi nói về phương pháp hoặc giới hạn ("chúng tôi chưa
tìm được văn bản công bố thống nhất, bạn cần hỏi trực tiếp"), và câu kêu gọi cuối bài. Bản
trước của skill này cấm "chúng tôi" gần như tuyệt đối, và điều đó đánh nhau với `docs/03` quy
tắc 4 và 6: cấm ngôi thứ nhất thì câu thừa nhận giới hạn — thứ `evidence_check.py` bắt buộc
phải có — chỉ còn cách viết ở thể vô ngôi, tức đẩy bài về đúng lỗi cú pháp dịch.

### 5. Mục dẫn về tin đăng — bắt buộc, áp chót

Tên mục theo mẫu **"Tìm/Mua [loại hình] [địa bàn] trên Muaban.net"**. Đây là mục nội dung
thật, không phải một dòng quảng cáo: nêu cách lọc tin, các khu vực lân cận, khoảng giá.
Liên kết phải trỏ đúng danh mục và địa bàn của bài. `house_voice_check.py` **chặn** bài
thiếu mục này.

### 6. Đoạn kết

Ba nhịp: chốt lại → "Hy vọng..." → lời mời về Muaban.net.

> Hy vọng những kinh nghiệm thuê phòng trọ tại Thủ Đức trên sẽ giúp bạn lựa chọn được nơi ở
> phù hợp, thuận tiện cho việc học tập, làm việc và sinh hoạt. Đừng quên theo dõi Muaban.net
> để cập nhật kinh nghiệm và các tin đăng cho thuê phòng trọ mới nhất bạn nhé.

Các cụm này **trước đây bị `closing_boilerplate` chặn**. Chúng đã được gỡ khỏi bộ lọc và
lưu ở khóa `house_voice_allowed` trong `scripts/lexicon/ai_phrases.json`, vì đo ra chúng nằm
trong 11 chỗ của bài thật. Dùng được, và nên dùng.

## Năm cái bẫy hay gặp nhất

| Bẫy | Dấu hiệu | Sửa |
|---|---|---|
| **Câu cụt liên tiếp** | 3 câu dưới 10 từ đứng cạnh nhau | Gộp thành một câu có mệnh đề phụ |
| **Bài tự nói về chính nó** | "bài không nêu", "bài cố ý để trống" | Nói thẳng với người đọc việc họ cần làm |
| **Gạch ngang dài** | dấu `—` | 0/24 bài thật dùng. Thay bằng dấu phẩy hoặc hai chấm |
| **In đậm giữa đoạn** | `**...**` trong văn xuôi | Kho bài thật gần như không dùng (số 0 đo được có phần do bộ rút bài, xem `docs/12`). In đậm chỉ ở tiêu đề và nhãn danh sách |
| **Câu hỏi tu từ trong thân bài** | "Vậy tính thế nào?" | Bài thật gần như không có. Câu hỏi chỉ ở tiêu đề hoặc mục hỏi đáp |
| **Lời khuyên không có chủ ngữ** | "Nên hỏi...", "Hãy kiểm tra..." | Thêm "bạn" làm chủ ngữ. `BLOCK` khi dưới 50% (quy tắc 17) |
| **"mình" chỉ người đọc** | "cơ sở mình học" | Đổi thành "cơ sở bạn học" |
| **Danh từ hóa động từ** | "việc xác định giá đất..." | "bạn xác định giá đất bằng..." |
| **Chủ ngữ trừu tượng** | "Điều này cho thấy...", "Việc này dẫn tới..." | Gọi tên chính sự vật, hoặc đưa "bạn" lên làm chủ ngữ. 24/24 bài thật dùng **0** lần |
| **Mệnh đề phụ dài dồn lên trước** | "Sau khi đã xem phòng và xác minh..., bạn mới nên cọc" | Đưa nòng cốt lên trước: "Bạn chỉ nên cọc sau khi..." |
| **Câu đứng rời nhau** | mật độ từ nối dưới 3,5/1.000 từ | Thêm "tuy nhiên", "vì vậy", "ngoài ra" giữa các câu, hoặc gộp hai câu thành một câu có mệnh đề phụ |
| **Ký hiệu `[Cxx]` trong bài** | `[C01]` giữa câu văn | Bỏ hết. Nêu tên văn bản trong câu, giữ `claim_id` ở ledger (quy tắc 16b) |

## Cú pháp — sáu phép sửa câu nói ngược

Đây là lượt sửa **thứ hai** của skill, thêm vào sau khi chủ dự án nhận xét *"cấu trúc nói
ngược giống tiếng nước ngoài nhiều hơn"*. Lượt trên nắn nhịp và khuôn mục; lượt này nắn từng
câu. Số đo và bằng chứng đầy đủ ở `docs/13-cu-phap-tieng-viet.md`.

Mỗi phép **giữ nguyên thông tin, chỉ đổi trật tự**. Không phép nào được thêm hay bớt dữ kiện.

| # | Sửa từ | Thành | Vì sao |
|---|---|---|---|
| 1 | "Việc xác định vị trí cơ sở là bước quan trọng" | "Trước khi tìm trọ, bạn cần biết mình học ở cơ sở nào" | Động từ bị biến thành danh từ thì mất người làm |
| 2 | "Điều này cho thấy tên phường có thể chưa cập nhật" | "Vì vậy, nhiều tin đăng vẫn ghi tên phường theo cách gọi cũ" | 24/24 bài thật dùng "điều này" **0** lần |
| 3 | "Sau khi đã xem phòng và xác minh…, bạn mới nên cọc" | "Bạn chỉ nên cọc sau khi đã xem phòng và xác minh…" | Nòng cốt câu phải đứng trước, mệnh đề phụ về sau |
| 4 | "Nên chạy thử quãng đường vào giờ cao điểm" | "Bạn nên chạy thử quãng đường vào giờ cao điểm" | Quy tắc 17 |
| 5 | "cơ sở mình học", "lịch học của mình" | "cơ sở bạn học", "lịch học của bạn" | Bài thật gần như không dùng "mình" cho người đọc |
| 6 | "Giá thuê được niêm yết trong tin đăng" | "Giá người cho thuê ghi trong tin đăng" | Chỉ sửa khi biết rõ ai làm; không biết thì để nguyên |

**Phép 3 không phải lệnh cắt trạng ngữ.** Bài thật mở câu bằng trạng ngữ ngắn rất nhiều —
"Trước khi đặt cọc,", "Vì vậy," — và dải `front_clause_ratio` của họ là 0,288–0,496, tức gần
một nửa số câu. Phép này chỉ nhắm vào mệnh đề phụ **dài** chen trước chủ ngữ.

**Phép 1 không phải lệnh xóa chữ "việc".** "Việc" và "sự" là từ bình thường của tiếng Việt;
bài thật dùng 0,7–10,4 lần trên 1.000 từ. Chúng chỉ sai khi quá dày, nên chỗ này theo chỉ số
`viec_per_1000`, không theo danh sách cấm.

Mười ba cụm **phải bỏ hẳn** vì 24 bài thật không dùng lần nào — nhóm `translated_syntax`,
ngưỡng 0: "điều này cho thấy", "điều này dẫn/kéo/khiến/đồng nghĩa", "việc này cho thấy",
"nhằm mục đích", "thông qua việc", "đối với việc", "trên cơ sở", "xét về", "mang tính chất",
"được thực hiện", "được coi là", "được tiến hành", "có vai trò quan trọng trong việc".

## Bốn rào cứng vẫn nguyên

Giọng nhà **không** được phép làm hỏng những thứ sau. Khi mâu thuẫn, các quy tắc này thắng:

1. **Không thêm dữ kiện** (quy tắc 1). Viết lại cho mượt không được sinh ra số, ngày, tên
   văn bản hay URL nào. Thiếu chi tiết thì viết câu đơn giản hơn.
2. **Giữ nguyên bảy thứ không được chạm** — như `humanizer-bds` đã liệt kê: front matter,
   tên và số hiệu văn bản được dẫn trong câu, mọi con số và ngày, khối minh bạch YMYL, link map,
   bảng và URL, tiêu đề nhận truy vấn chính.
3. **Không bỏ tín hiệu YMYL** (quy tắc 3). Phạm vi, mốc dữ liệu, giới hạn, khuyến nghị tham
   vấn phải còn đủ bốn. Giọng blog nhẹ nhàng hơn, nhưng không được nhẹ đến mức mất cảnh báo.
4. **Không hứa hẹn** (quy tắc 4). `guarantees` vẫn là `BLOCK` và không được gỡ.

## Làm xong thì kiểm

```powershell
python scripts/house_voice_check.py work/<slug>/article.md
python scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json
```

`house_voice_check.py` in ra số chỉ số lệch kèm mốc đo được từ chính kho bài thật — đừng nhớ
con số, hãy đọc dòng máy in ra, vì mốc đổi mỗi lần kho bài đổi. **Vượt mốc là bài chưa giống
bất kỳ bài nào đang đăng** — sửa tiếp. Trong mốc thì các cảnh báo còn lại đem giải trình trong
`qa-report.md`.

Riêng `BLOCK` về danh xưng (quy tắc 17) **không nằm trong ngân sách lệch** và không được giải
trình — phải sửa. Máy in ra từng câu kèm số dòng; sửa đúng từng câu đó.

Ngưỡng nằm ở `scripts/lexicon/house_voice.json` và **do máy sinh ra**, không phải người đặt.
Thấy ngưỡng vô lý thì thêm bài thật vào `reference/muaban-blog/` rồi chạy lại
`scripts/house_voice_profile.py`; đừng sửa tay file JSON, và tuyệt đối đừng nới ngưỡng để
bài qua cửa.
