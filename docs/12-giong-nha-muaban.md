# 12 — Giọng nhà Muaban.net

Tài liệu này mô tả giọng văn của blog Muaban.net bằng **số đo lấy từ bài thật**, không phải
bằng nhận xét cảm tính. `docs/03-giong-van-nguoi-that.md` nói bài viết thế nào thì nghe như
người thật nói chung; tài liệu này nói bài viết thế nào thì nghe như **tòa soạn này**.

Khi hai tài liệu mâu thuẫn, tài liệu này thắng — vì nó có bằng chứng là bài đang đăng, còn
`docs/03` là quy tắc suy ra từ lý thuyết.

> **Đọc cùng `docs/13-cu-phap-tieng-viet.md`.** Tài liệu này đo *hình dạng* của bài: câu dài bao
> nhiêu, đoạn mấy câu, mật độ từ nối. Tài liệu 13 đo *cú pháp và xưng hô*: lời khuyên có gọi người
> đọc không, câu có nói ngược kiểu dịch không. Hai chỗ bổ sung nhau, và bài 001 từng đạt tài liệu
> 12 mà vẫn trượt tài liệu 13.

## Kho bài mẫu

`reference/muaban-blog/` chứa **24 bài thật** tải về từ `muaban.net/blog/`, rút thân bài từ HTML
gốc. Mỗi file giữ nguyên cấp heading gốc và có dòng `<!-- url -->` trỏ về bản gốc.

Kho gồm mười bốn bài cụm "kinh nghiệm thuê phòng trọ / thuê trọ gần trường" (2025–2026), một bài
review khóa học, bốn bài pháp lý và đất đai — trong đó có
`bang-gia-chuyen-doi-dat-nong-nghiep-sang-dat-tho-cu-2025`, chính là bài mà bài 001 của dự án
đang cập nhật — cùng năm bài về xây và bài trí phòng trọ.

Kho đi từ 12 lên 24 bài sau khi chủ dự án chỉ ra rằng với 12 bài, p10 và p90 dao động quá mạnh
để làm ngưỡng: mật độ chữ "bạn" trải từ 0,56 đến 17,71 nên sàn p10 chỉ còn 1,64, gần như vô hiệu.
Bộ tải bài nay nằm trong dự án ở `scripts/corpus_fetch.py` — trước đây nó chỉ tồn tại trong thư
mục tạm của một phiên làm việc, nên khi cần thêm bài thì không còn gì để chạy:

```powershell
python scripts/corpus_fetch.py --category 3      # xem bai nao chua co trong kho
python scripts/corpus_fetch.py <url> [<url>...]  # tai ve, roi do lai bang house_voice_profile.py
```

**Kho này không phải nguồn dữ kiện.** Nó chỉ dùng để đo văn phong. Quy tắc 12 vẫn nguyên: bài
viết trích `source_url` gốc, không bao giờ trích blog hay wiki.

## Cách các con số được sinh ra

```powershell
python scripts/house_voice_profile.py          # do kho, ghi scripts/lexicon/house_voice.json
python scripts/house_voice_profile.py --show   # chi in bang, khong ghi
python scripts/house_voice_check.py work/<slug>/article.md
```

`house_voice_profile.py` đo 29 chỉ số trên từng bài rồi lấy p10, trung vị, p90 của cả kho, và **kiểm 18 chỉ số** trong đó.
`house_voice_check.py` đối chiếu bài đang viết với dải p10–p90 và cảnh báo khi ra ngoài.

**Không sửa tay `house_voice.json`.** Muốn đổi ngưỡng thì thêm bài thật vào kho rồi chạy lại
script. Đây là chốt chặn chống đúng một việc: nới ngưỡng cho bài của mình qua cửa.

### Ngân sách lệch

Dải p10–p90 theo định nghĩa đã bỏ ra ngoài khoảng 20% giá trị, nên **chính bài thật cũng lệch
vài chỉ số**: trung vị 4, nhiều nhất 9 trong số 18 chỉ số được kiểm. Con số này được ghi vào
hồ sơ và in ra mỗi lần kiểm, để ba cảnh báo không bị đọc nhầm thành bài hỏng.

Bài lệch **trên 9 chỉ số** là bài không giống bất kỳ bài nào đang đăng. Đó là mốc phải sửa.
Đừng nhớ con số này — nó đổi mỗi lần kho bài đổi; hãy đọc dòng máy in ra.

Riêng `BLOCK` về danh xưng người đọc (quy tắc 17) **không nằm trong ngân sách này** và
không được giải trình: mọi câu khuyên phải gọi "bạn".

## Chân dung đo được

| Chỉ số | p10 | Trung vị | p90 |
|---|---|---|---|
| Độ dài câu trung bình | 25,1 từ | **27,4 từ** | 30,8 từ |
| Tỷ lệ câu ngắn (≤10 từ) | 1,1% | **3,3%** | 11,6% |
| Tỷ lệ câu dài (≥35 từ) | 12,1% | **18,8%** | 35,9% |
| Độ dài đoạn | 43,0 từ | **55,0 từ** | 62,1 từ |
| Số câu mỗi đoạn | 1,8 | **1,9** | 2,3 |
| "bạn" trên 1.000 từ | 1,2 | **6,4** | 10,1 |
| Câu khuyên trên 1.000 từ | 2,3 | **6,3** | 11,4 |
| **Tỷ lệ câu khuyên có "bạn" làm chủ ngữ** | 2,7% | **61,3%** | 85,0% |
| **Mệnh lệnh vô chủ ngữ trên 1.000 từ** | 0,71 | **1,97** | 4,20 |
| **"mình" trên 1.000 từ** | 0,00 | **0,00** | 1,02 |
| **"việc" trên 1.000 từ** | 1,9 | **3,4** | 6,9 |
| **Câu mở bằng chủ ngữ trừu tượng** | 1,1% | **4,1%** | 7,4% |
| **Câu mở bằng mệnh đề phụ dài** | 28,8% | **42,2%** | 49,6% |
| **"điều này" / "việc này" trên 1.000 từ** | 0,00 | **0,00** | 0,49 |
| Câu hỏi trong văn xuôi | 0,0% | **0,0%** | 2,2% |
| Mật độ từ nối trên 1.000 từ | 2,9 | **4,5** | 6,9 |
| Gạch ngang dài | 0 | **0** | 0 |
| Bị động hành chính trên 1.000 từ | 0,00 | **0,00** | 0,87 (đo nhưng **không kiểm**) |
| In đậm trong văn xuôi | 0 | **0** | 0 (đo nhưng **không kiểm**, xem bên dưới) |
| Độ dài thân bài | 1.907 từ | **2.253 từ** | 2.875 từ |
| Số mục chính (H3) | 4 | **6** | 9,7 |
| Mục con trên mỗi mục chính | 0,8 | **1,5** | 2,7 |

Hai dòng đáng chú ý vì chúng tuyệt đối: **không bài nào dùng gạch ngang dài, và câu hỏi tu từ
trong thân bài gần như bằng không.**

Riêng `bold_ratio` được đo nhưng **không đưa vào bộ kiểm**: bộ rút thân bài xoá thẻ `<strong>`
nằm trong đoạn văn, nên số 0 đo được là tạo tác của công cụ chứ không phải sự thật về blog. Đối
chiếu HTML thô thì bài thật có in đậm trong văn xuôi, chỉ là rất thưa.

## Đây là blog tiếng Việt, và điều đó thay đổi vài quy tắc

Bộ từ vựng chống văn máy của dự án thích ứng từ nguồn tiếng Anh: `blader/humanizer` và trang
Wikipedia "Signs of AI writing". Phần lớn chuyển sang tiếng Việt được, nhưng có những chỗ lời khuyên
tiếng Anh **làm hỏng** văn tiếng Việt, và cách phát hiện là đếm xem pattern đó nổ bao nhiêu lần trên
kho bài thật.

> **Cơ chế này có một giới hạn đã phải trả giá.** Nó chỉ **gỡ** được pattern tiếng Anh bắt oan; nó
> không bao giờ tự **thêm** pattern tiếng Việt còn thiếu. Vì vậy suốt một thời gian dài dự án không
> có một chỉ số nào đo cú pháp hay xưng hô, và khi chủ dự án nhận xét bài "không giống tiếng Việt",
> "cấu trúc nói ngược giống tiếng nước ngoài", "chưa có danh xưng của người đọc" thì máy kiểm không
> có gì để trả lời. Phần bù nằm ở quy tắc 17 và `docs/13-cu-phap-tieng-viet.md`.

### Từ nối là phương tiện liên kết, không phải sáo ngữ

Văn tiếng Anh coi "moreover", "furthermore" là chữ thừa nên khuyên cắt. Tiếng Việt thì dùng "tuy
nhiên", "vì vậy", "ngoài ra", "bên cạnh đó" để **nối ý câu trước với câu sau**; cắt chúng đi thì mỗi
câu thành một mệnh đề độc lập và bài đọc như một danh sách.

Đo được:

| | Bài thật | Ngưỡng cũ của dự án |
|---|---|---|
| Số cụm nối mỗi bài | 0 – 11, trung vị 4 | tối đa **6** → 2/12 bài thật vi phạm; đếm lại trên 24 bài thì 23/24 bài nổ, nên ngưỡng nay là **12** |
| Mật độ cụm nối trên 1.000 từ | 3,5 – 8,7 | không đo |
| Số lần lặp một cách mở câu | 4 – 7 | tối đa **3** → **12/12** bài thật vi phạm |

Ngưỡng "lặp cách mở câu tối đa 3" là chỗ sai rõ nhất: không một bài thật nào đạt được nó. Tiếng Việt
lặp "Bạn nên...", "Ngoài ra..." ở đầu câu là bình thường và làm văn đều nhịp; ép đổi cách vào câu mỗi
lần chỉ làm văn gượng.

Đã xử lý: `filler_connectors` nâng từ 6 lên 8 và viết lại phần hướng dẫn, `MAX_SAME_OPENER` nâng từ 3
lên 7, và thêm chỉ số **`connector_per_1000`** vào bộ kiểm giọng nhà. Chỉ số này hai chiều, nên nó
cảnh báo cả khi bài **quá ít** từ nối — tức là đo đúng cái mà người duyệt gọi là "không có sự liên
kết giữa các câu".

### Không chèn ký hiệu trích dẫn vào thân bài

Bài thật có **đúng 0** ký hiệu dạng `[C01]`. Cách họ dẫn nguồn là nêu tên văn bản ngay trong câu:

> Theo Điều 8 Nghị định 103/2024/NĐ-CP, việc tính tiền sử dụng đất khi chuyển mục đích sử dụng đất
> không dựa trên một bảng giá cố định...

Dự án trước đây yêu cầu đánh dấu `[Cxx]` sau mỗi câu có claim, và bài 001 từng có 34 ký hiệu như vậy
trong văn. Nay bỏ hết theo quy tắc 16b: `claim_id` chỉ tồn tại trong `evidence-ledger.csv` và trong
khối "Căn cứ" cuối bài.

**Đánh đổi phải biết.** Khi không còn ký hiệu, `evidence_check.py` mất khả năng ghép từng câu với
từng claim. Những gì máy **vẫn** kiểm được: mọi con số trong bài phải đối chiếu được với ledger, và
claim đang ở trạng thái `GAP` không được lọt vào bài (dò bằng trùng câu chữ). Những gì máy **không**
còn kiểm được: câu này có đúng là dựa trên claim kia hay không. Phần đó từ nay do người viết và người
duyệt giữ.

## Ba chỗ dự án đã làm ngược

Đo xong mới thấy bộ kiểm cũ đang đẩy bài ra xa giọng thật chứ không kéo lại gần.

### 1. Nhịp câu — bộ kiểm cũ thưởng cho văn giật cục

`human_voice_check.py` từng đòi `burstiness ≥ 0,38` và `tỷ lệ câu ngắn ≥ 12%`. Bài thật có
trung vị **0,33** và **2,8%**. Nghĩa là **một bài Muaban.net thật sẽ trượt bộ kiểm của chính
dự án**.

Hệ quả thấy rõ ở bài 001: 25,3% câu ngắn, câu trung bình 17,9 từ, đầy những câu cụt như
"Cộng ba kết quả lại là ra." Bài đạt điểm cao ở bộ kiểm cũ, và bị người duyệt chê "cứng".

Đã xử lý: `human_voice_check.py` **bỏ hẳn** ba cảnh báo nhịp câu. Phần nhịp nay thuộc về
`house_voice_check.py`, đo theo dải thật. Hai bộ kiểm không còn khuyên ngược nhau.

### 2. Bài mẫu của dự án dạy sai giọng

`examples/fixture-dat-chuan/article.md` được `humanizer-bds` và `examples/README.md` chỉ định
làm mẫu giọng. Đo ra: câu trung bình 15,5 từ, **31,2% câu ngắn**, đoạn 24,9 từ — còn xa giọng
thật hơn cả bài 001.

Bài mẫu là văn giả lập do agent viết, chưa từng được đối chiếu với bài đang đăng. Đã viết lại
theo giọng nhà.

### 3. Bộ lọc sáo ngữ chặn nhầm giọng thương hiệu

Chạy bộ lọc lên 12 bài thật đầu tiên cho thấy `closing_boilerplate` nổ 11 lần và `empty_openers` nổ 2
lần — toàn vào đúng công thức của tòa soạn.

Đã gỡ 18 cụm khỏi hai nhóm đó và lưu lại ở khóa `house_voice_allowed` trong
`scripts/lexicon/ai_phrases.json`, kèm lý do, để người sau biết vì sao chúng vắng mặt và khôi
phục được nếu đổi ý.

Hai nhóm khác cũng nổ nhưng **không được gỡ**, vì đo kỹ thì đó không phải giọng nhà:

- `guarantees` và `hype_marketing` chỉ nổ ở một bài duy nhất, và nổ vào phần **trích tên khóa
  học** của bên thứ ba chứ không phải câu của tòa soạn. Hai nhóm này liên quan quy tắc 4
  (không hứa hẹn) nên giữ nguyên.
- `vague_link` nổ vào cụm "tài sản gắn liền với đất" — một **thuật ngữ pháp lý**, không phải
  liên hệ mơ hồ. Đây là lỗi nhận nhầm của bộ lọc, đã sửa bằng cách thu hẹp mẫu thành
  `gắn liền với (?!đất)`.

## Cái giá đã trả

Hai thay đổi dưới đây là **quyết định có ý thức của chủ dự án**, không phải kết luận kỹ thuật.
Ghi lại ở đây để người sau biết đánh đổi là gì.

**Lặp cụm từ khóa chính ở nhiều heading, từ `BLOCK` xuống `INFO`.** Bài thật lặp cụm từ khóa
chính ở 5–6 heading trong cùng một bài. Dự án trước đây chặn từ 2 heading trở lên, theo quy
tắc 6 (không tối ưu bằng nhồi từ khóa).

Đây là chỗ rủi ro thật, không phải rủi ro lý thuyết: nhồi từ khóa vào heading là một trong
những tín hiệu Google dùng để nhận diện nội dung tối ưu quá tay, và bất động sản là YMYL nên
ngưỡng chịu đựng thấp hơn. Cảnh báo được **hạ xuống `INFO` chứ không xoá**, để số lượng
heading chứa từ khóa vẫn hiện ra cho người duyệt thấy trước khi đăng.

**Công thức kết bài đóng hộp.** "Hy vọng những... sẽ giúp bạn" và "Đừng quên theo dõi
Muaban.net" là cụm mà mọi hướng dẫn viết lách đều khuyên tránh, và `docs/03` từng cấm đích
danh. Chúng được mở khoá vì đó đúng là cách blog kết bài. Đổi lại, bài sẽ nghe giống blog
nhưng kém riêng biệt hơn.

Muốn lấy lại hai thứ này thì chép các cụm từ `house_voice_allowed` ngược về nhóm cũ, và đổi
hai lời gọi `report.add("heading", INFO, ...)` trong `scripts/onpage_check.py` về `BLOCK` và
`WARN`.

## Quan hệ với các tài liệu khác

| Tài liệu | Vai trò | Khi mâu thuẫn |
|---|---|---|
| `docs/03-giong-van-nguoi-that.md` | Giọng người thật nói chung | Tài liệu 12 thắng ở phần nhịp câu và kết bài |
| `docs/02-chuan-outline.md` | Cấu trúc, đánh số, `Lời kết` | `docs/02` thắng — cấu trúc theo sheet nội bộ |
| `docs/10-quy-chuan-onpage.md` | Chuẩn on-page từ Google Sheet | `docs/10` thắng, trừ phần lặp từ khóa ở heading |
| `.claude/skills/humanizer-bds` | Gỡ dấu vết máy | Chạy **trước** `giong-muaban-bds` |

## Hai chỗ dự án cố tình khác bài thật

Không phải cái gì bài thật làm cũng đáng chép. Hai chỗ dưới đây là lựa chọn của chủ dự án:

- **`Lời kết`:** 0/24 bài thật có mục này (đã đếm lại trên cả kho mở rộng); blog kết bằng một đoạn không heading. Dự án **giữ**
  `Lời kết` theo sheet format nội bộ (quy tắc 14).
- **Mục lục:** 12/12 bài trong kho ban đầu có mục lục dạng toggle. Dự án **bỏ**, theo yêu cầu của người
  duyệt ở lượt từ chối bản 0.1.3.

Đừng "sửa lại cho giống blog" ở hai chỗ này.


## Sapo: không ngày tháng, và kết bằng lời mời đọc tiếp

Đo trên 24 bài thật: **0/24 sapo có ngày cập nhật** hay cụm "cập nhật tới". WordPress đã hiển thị
ngày sửa bài, nên nhắc lại trong sapo vừa thừa vừa làm câu mở bài cụt ý. Mốc dữ liệu vẫn bắt buộc,
nhưng nó nằm ở **khối minh bạch cuối bài**, không nằm ở sapo.

**13/24 bài thật kết sapo bằng một lời mời đọc tiếp**, kiểu *"Hãy cùng tìm hiểu chi tiết qua bài
viết sau đây của Muaban.net nhé!"*. Đó là lý do các cụm như "mời bạn cùng theo dõi" nằm trong
`house_voice_allowed` chứ không bị bộ lọc sáo ngữ chặn.

**Câu mời đó phải kéo người đọc bằng chính câu họ vừa gõ.** Người duyệt từ chối một bài vì CTA mời
đọc "để biết nên làm gì với con chuồn chuồn đang bay trong phòng", trong khi truy vấn là "chuồn
chuồn bay vào nhà là điềm gì": *"Kêu gọi xem bài viết để biết được chuồn chuồn bay vào nhà là điềm
gì chứ, đây mới là search intent người dùng muốn tìm."* Mời đọc một ý phụ là lệch intent, dù ý phụ
đó hữu ích hơn. `onpage_check.py` cảnh báo khi câu CTA không nhắc truy vấn chính. Đây là **quyết
định biên tập của chủ dự án**, không phải số đo từ kho bài thật.

**Câu mời đó nằm ở dòng sapo H2, không phải ở đoạn văn bên dưới.** Chỗ này tôi đã làm sai một lần:
kiểm đầu tiên chỉ soi đoạn văn đầu tiên nên bắt oan cả bài mẫu `fixture-dat-chuan` của chính dự án,
và lần "sửa" bài mẫu bằng cách thêm câu vào đoạn văn đã đẩy năm chỉ số giọng nhà của nó ra ngoài
dải. `onpage_check.py` nay soi cả dòng H2 lẫn đoạn đầu, và chỉ cảnh báo khi không chỗ nào có.

Cả hai điều trên sinh ra từ một lần bị từ chối thật ở cổng duyệt bài, với góp ý nguyên văn:
*"Viết không rõ ý, chưa có CTA để người đọc tiếp tục theo dõi bài viết. Xoá phần cập nhật ngày nào
vì khi đăng bài viết trên WordPress đều sẽ có."* `onpage_check.py` nay cảnh báo cả hai.

## Kết bài: khuôn của tòa soạn

Người duyệt đưa nguyên khuôn kết bài đang dùng trên blog:

> *"Trên đây là những lý giải về hiện tượng … mà Muaban.net muốn giới thiệu đến bạn đọc. Mỗi hiện
> tượng xuất hiện trong cuộc sống của bạn đều có thể liên quan tới những điều kỳ diệu … Đừng quên
> truy cập Muaban.net mỗi ngày để không bỏ lỡ những tin tức mới nhất về phong thủy, nhà đất và chia
> sẻ kinh nghiệm nhé!"*

Bốn phần theo thứ tự: **tổng kết một câu có tên Muaban.net** → **một câu về ý nghĩa của chủ đề** →
**mời bình luận** → **mời quay lại Muaban.net, kèm một liên kết nội bộ**. Các cụm "Trên đây là…" và
"Đừng quên…" nằm trong `house_voice_allowed` chính vì đây là giọng kết của tòa soạn.

Với bài **ngoài mảng bất động sản**, câu cuối này cũng là chỗ đặt liên kết nội bộ, vì mục dẫn tin
đăng đã được miễn (xem ngoại lệ ở quy tắc 15).
