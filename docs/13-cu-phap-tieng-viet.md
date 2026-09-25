# 13 — Câu tiếng Việt, không phải câu dịch

> Tài liệu này ra đời từ một nhận xét của chủ dự án: *"Ngôn ngữ và giọng văn đang không giống
> tiếng Việt. Cấu trúc nói ngược giống tiếng nước ngoài nhiều hơn. Nội dung cũng chưa có danh xưng
> của người đọc như 'bạn nên ....' vì thế kém tự nhiên."*
>
> Hai lỗi, và cả hai đều **đo được**. Tài liệu 12 trả lời câu hỏi "bài có giống bài đang đăng
> không". Tài liệu này trả lời câu hỏi hẹp hơn: **"câu này có phải câu tiếng Việt không"**.

## A. Vì sao dự án mù đúng chỗ này

`docs/03` từng mở đầu bằng câu **"Không phải vì ngữ pháp"**, rồi liệt kê ba lý do văn AI nghe ra
ngay — đều là chuyện từ vựng và độ dài. Hệ quả kéo dài suốt dự án:

- Toàn bộ 11 chỉ số của `house_voice_profile.py` là **độ dài và tần số từ**. Không một chỉ số nào
  chạm tới trật tự thông tin, danh từ hóa, chủ ngữ hay bị động.
- `nominal_verbs` trong lexicon mang nhãn "Né động từ là/có" và chỉ bắt bảy cụm hệ từ cố định —
  **không bắt một trường hợp danh từ hóa tiếng Việt nào**.
- Câu *"Việc xác định giá đất được thực hiện trên cơ sở bảng giá do UBND ban hành, điều này dẫn
  tới sự khác biệt giữa các địa phương"* đi qua sạch mọi máy kiểm của dự án.
- Nặng nhất: cụm **"điều này cho thấy"** không phải tai nạn. Nó được **kê đơn ở ba chỗ** —
  `docs/03` quy tắc 5, `seo-writer-bds` và `templates/article.md` — làm mẫu đánh dấu câu diễn giải.
  Agent viết nó ra vì được dạy viết nó ra.

Bài học chung: quy tắc 16 (`CLAUDE.md`) chỉ **gỡ** được những pattern tiếng Anh bắt oan tiếng
Việt. Nó không bao giờ tự **thêm** pattern tiếng Việt còn thiếu. Phần thiếu phải có người đi nghĩ
ra rồi đi đo.

## B. Kho bài thật nói gì (24 bài, `reference/muaban-blog/`)

Đo bằng `house_voice_profile.py`. Bảy chỉ số dưới đây là **mới**, thêm vào sau nhận xét trên.

| Chỉ số | p10 | Trung vị | p90 | Nó bắt lỗi gì |
|---|---|---|---|---|
| `advice_subject_ratio` | 0,027 | **0,613** | 0,850 | Tỷ lệ câu khuyên lấy "bạn" làm chủ ngữ |
| `bare_advice_per_1000` | 0,71 | 1,97 | **4,20** | Mệnh lệnh không chủ ngữ: "Nên hỏi...", "Hãy kiểm tra..." |
| `minh_per_1000` | 0 | 0 | **1,02** | Dùng "mình" để chỉ người đọc |
| `viec_per_1000` | 1,86 | 3,38 | **6,93** | Danh từ hóa bằng "việc" |
| `abstract_start_ratio` | 0,011 | 0,041 | **0,074** | Câu mở bằng "Việc…", "Sự…", "Điều…", "Đó là…" |
| `front_clause_ratio` | 0,288 | 0,422 | **0,496** | Câu mở bằng mệnh đề phụ dài (dấu phẩy đầu sau từ thứ 8) |
| `dem_per_1000` | 0 | 0 | **0,49** | "điều này", "việc này" làm chủ ngữ |

Hai chỗ đo xong rồi **bỏ không kiểm**, vì đo ra chúng không phân biệt được gì:

- **Bị động `được`/`bị`.** Bài thật dùng bị động hành chính tới 4,5 lần trên 1.000 từ ở các bài
  pháp lý; bài của agent dùng **ít hơn**. `humanizer-bds` xếp bị động vào nhóm "bỏ qua" từ đầu, và
  lần đo này cho thấy quyết định đó đúng với tiếng Việt. Chỉ giữ `passive_admin_per_1000` để theo
  dõi, không đặt ngưỡng.
- **"nó" làm chủ ngữ.** Gần như mọi bài thật bằng 0, và bài của agent cũng bằng 0.

Và một danh sách **13 cụm mà 24 bài thật không dùng lần nào** — đây là nhóm `translated_syntax`
mới trong lexicon, ngưỡng 0:

> "điều này cho thấy" · "điều này dẫn/kéo/khiến/đồng nghĩa" · "việc này cho thấy" · "nhằm mục
> đích" · "thông qua việc" · "đối với việc" · "trên cơ sở" · "xét về" · "mang tính chất" ·
> "được thực hiện" · "được coi là" · "được tiến hành" · "có vai trò quan trọng trong việc"

Ngược lại, bốn cụm **nghe như dịch nhưng bài thật dùng đều**, nên không được cấm: "một trong
những" (18 lần / 13 bài), "đối với" (23 / 11), "mang lại" (11 / 8), "có thể được" (10 / 6). Và
"việc" nói chung là từ bình thường của tiếng Việt — bài thật dùng 0,7 đến 10,4 lần trên 1.000 từ.
Nó chỉ sai **khi quá dày**, nên chỗ này phải dùng chỉ số, không dùng danh sách cấm.

## C. Danh xưng người đọc — quy tắc 17

Chủ dự án yêu cầu: *"Những lời khuyên, giải đáp thắc mắc cần phải bổ sung danh từ vào."*

Số đo cho thấy chỗ sai **không phải lượng** chữ "bạn". Bài 001 có 5,9 lần trên 1.000 từ, nằm giữa
dải bài thật. Chỗ sai là **vai ngữ pháp**: chỉ 18% câu khuyên của nó lấy "bạn" làm chủ ngữ, trong
khi trung vị bài thật là 61%, còn mật độ mệnh lệnh vô chủ ngữ thì cao hơn cả bài thật cao nhất.

Bốn cặp đối chiếu, cùng một nội dung:

| Bài thật | Bài agent |
|---|---|
| "Trước khi thuê, **bạn nên hỏi** người dân xung quanh hoặc người đang ở trọ về tình trạng ngập nước." | "...hàng quán và người dân xung quanh thường biết rõ, **nên hỏi** một vài người là ra." |
| "Trước khi đặt cọc, **bạn cần hỏi** rõ giá điện, nước, internet, phí gửi xe..." | "**Hãy hỏi** rõ cách tính tiền điện, tiền nước, phí gửi xe..." |
| "Với những khu trọ đông người thuê, **bạn nên kiểm tra** camera, khóa cổng, khu vực để xe..." | "**Nên để ý** đèn đường dọc lối vào, cổng khu trọ có khóa hay không..." |
| "**Bạn chỉ nên đặt cọc** sau khi đã xem phòng trực tiếp và xác minh rõ người cho thuê có quyền quản lý." | "**Hãy yêu cầu xem** bản gốc và chụp lại số vào sổ ngay tại buổi gặp." |

Khuôn của bài thật rất đều: **trạng ngữ → "bạn" → động từ khuyên → việc cụ thể.**

Mốc chặn trong `house_voice_check.py` — `ADVICE_SUBJECT_BLOCK = 0,50` — **không** đo được từ kho
bài thật, vì dải ở đó trải từ 0% đến 100% và sàn p10 chỉ 2,7%. Đây là **quyết định của chủ dự án**,
ghi rõ như quy tắc 15 đã ghi ba quyết định trước. Nó áp cho bài của dự án, và nói thẳng ra thì
**8 trong 24 bài thật nằm dưới mốc này** — dự án cố ý chặt hơn những bài yếu nhất của blog.

Mức **cảnh báo** thì không đặt cứng: máy lấy đúng **trung vị của kho bài thật** (hiện 61%) đọc từ
hồ sơ, nên nó tự đổi khi kho bài đổi. "Dưới trung vị bài thật" là một câu nói được; một con số do
người viết nghĩ ra thì không.

Một điều số đo dạy lại: **mục tiêu không phải 100%.** Bài thật vẫn dùng mệnh lệnh vô chủ ngữ
0,71–4,20 lần trên 1.000 từ. Khi nắn fixture mẫu, bản đầu đạt 100% câu khuyên có "bạn" và lập tức
vượt trần `ban_per_1000` — gọi người đọc quá dày cũng là lệch giọng.

Máy kiểm in ra **từng câu** thiếu danh xưng kèm số dòng, vì cách sửa là đổi chủ ngữ của chính câu
đó, không phải viết lại cả mục.

## D. Sáu phép sửa cú pháp

Mỗi phép giữ nguyên thông tin, chỉ đổi trật tự. Không phép nào được thêm hay bớt dữ kiện.

**1. Danh từ hóa → động từ có người làm**

> Trước: Việc xác định vị trí cơ sở học tập là bước quan trọng trước khi tìm trọ.
> Sau: Trước khi tìm trọ, bạn cần biết mình sẽ học ở cơ sở nào.

**2. Chủ ngữ trừu tượng → người đọc hoặc chủ thể thật**

> Trước: Điều này cho thấy tên phường trong tin đăng có thể chưa cập nhật.
> Sau: Vì vậy, nhiều tin đăng vẫn ghi tên phường theo cách gọi trước đây.

**3. Mệnh đề phụ dài → đưa nòng cốt câu lên trước**

> Trước: Sau khi đã xem phòng trực tiếp và xác minh người cho thuê có quyền quản lý căn phòng,
> bạn mới nên đặt cọc.
> Sau: Bạn chỉ nên đặt cọc sau khi đã xem phòng trực tiếp và xác minh người cho thuê có quyền
> quản lý căn phòng.

Lưu ý: bài thật **vẫn** mở câu bằng trạng ngữ ngắn rất nhiều ("Trước khi đặt cọc,", "Vì vậy,").
Dải `front_clause_ratio` của họ là 0,288–0,496, tức gần một nửa câu. Phép sửa này chỉ nhắm vào
mệnh đề phụ **dài** dồn lên trước, không nhắm vào trạng ngữ ngắn.

**4. Mệnh lệnh vô chủ ngữ → "bạn" làm chủ ngữ**

> Trước: Nên chạy thử quãng đường vào đúng khung giờ mình sẽ học.
> Sau: Bạn nên chạy thử quãng đường vào đúng khung giờ mình sẽ học.

**5. "mình" chỉ người đọc → "bạn"**

> Trước: cơ sở mình học, lịch học của mình
> Sau: cơ sở bạn học, lịch học của bạn

**6. Bị động hành chính → chủ động, nếu biết ai làm**

> Trước: Giá thuê được niêm yết trong tin đăng không phải giá giao dịch.
> Sau: Giá người cho thuê ghi trong tin đăng không phải giá giao dịch.

Phép 6 là phép **nhẹ nhất** trong sáu phép: bài thật dùng bị động nhiều hơn bài agent, nên chỉ sửa
khi biết rõ ai là người làm. Không biết thì để nguyên.

## E. Tài liệu ngoài đã tra, và lấy được gì

Chủ dự án yêu cầu tra "tài liệu uy tín trên internet". Kết quả thật thà: phần lớn hướng dẫn tiếng
Việt trên mạng nói chung chung, và **phần nhiều xác nhận lại những gì dự án đã có**. Ba chỗ thật
sự thêm được điều gì:

| Nguồn | Lấy vào | Không lấy |
|---|---|---|
| [Wikipedia tiếng Việt — Cẩm nang biên soạn/Dịch thuật](https://vi.wikipedia.org/wiki/Wikipedia:Cẩm_nang_biên_soạn/Dịch_thuật) | Hai lời khuyên cụ thể và đúng với tiếng Việt: **tách câu dài thành câu ngắn** và **chuyển bị động sang chủ động khi phù hợp**. Cùng cảnh báo rằng dịch từng chữ tạo ra câu "tối nghĩa, vô nghĩa hoặc sai ngữ pháp". | Yêu cầu "giữ văn phong trang trọng, tránh lối thân mật" — đó là quy ước **bách khoa**, ngược hẳn với blog. Áp vào đây sẽ ra đúng giọng mà chủ dự án đang chê. |
| [Microsoft Vietnamese Localization Style Guide](https://download.microsoft.com/download/b/f/e/bfecb1b4-21ab-48fd-a48c-c2471b026f8f/vie-vnm-StyleGuide.pdf) (bản PDF, [danh mục](https://learn.microsoft.com/en-us/globalization/reference/microsoft-style-guides)) | Nguyên tắc chọn **một đại từ chuẩn cho người đọc và dùng xuyên suốt**, và cấm dịch từng chữ vì bản dịch sẽ không tự nhiên. Đây là chỗ đỡ cho quyết định "bạn" xuyên suốt, không lẫn "quý khách"/"các bạn". | Thang trang trọng của tài liệu kỹ thuật, không dùng cho blog. |
| [GTV SEO — Cách viết content hay](https://gtvseo.com/marketing/cach-viet-content-hay/) | Ba điều khớp với số đo của kho bài thật: dùng **"bạn"** chứ không "các bạn" vì nội dung là đối thoại một–một; ưu tiên **câu chủ động**; dùng **động từ mạnh** thay động từ mơ hồ. | Các mẹo về tiêu đề giật và kể chuyện cá nhân — vướng quy tắc 1 và quy tắc 4. |
| [Brands Vietnam — Dấu hiệu nhận biết nội dung do AI viết](https://help.brandsvietnam.com/vi/article/dau-hieu-nhan-biet-noi-dung-duoc-viet-boi-ai-3zy07d/) | Một xác nhận độc lập bằng tiếng Việt cho những gì lexicon đã bắt: mở bài "Trong bối cảnh…", cấu trúc "không chỉ… mà còn", từ nối máy móc, kết bằng "Tóm lại", gạch ngang dài, và bịa nguồn. Sáu dấu hiệu, dự án đã có cả sáu. | Không có gì mới về cú pháp. |

Điều đáng ghi nhất về vòng tra này: **không nguồn ngoài nào đo được giọng của blog này.** Chúng chỉ
cho vài nguyên tắc chung. Con số vẫn phải lấy từ 24 bài thật — đúng như quy tắc 16 đã nói.

## F. Chỗ này không mâu thuẫn với tài liệu 12

Tài liệu 12 nói blog viết **câu dài và đều**, trung bình 27 từ, và cách làm dài là **mệnh đề phụ**.
Tài liệu 13 nói **đừng dồn mệnh đề phụ lên trước nòng cốt câu**. Hai điều này đi cùng nhau: câu
dài của bài thật là câu có mệnh đề phụ **kéo về sau**, kiểu

> "Bạn nên khảo sát thêm vào buổi trưa hoặc sau khi mưa để kiểm tra khả năng chống nóng, tình
> trạng thấm dột và hệ thống thoát nước."

Chủ ngữ "bạn" đứng đầu, động từ ngay sau, mọi thứ khác nối về sau. Dài 25 từ mà không có một mệnh
đề nào chen trước chủ ngữ. Đó là khuôn cần bám.
