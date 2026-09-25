# Content SEO — Bất động sản (Muaban.net)

Công cụ AI để **nghiên cứu intent → lên outline → viết bài chuẩn SEO** cho chủ đề bất động sản,
với ba ràng buộc không được thương lượng: **không bịa đặt**, **giọng văn người thật**,
**không rơi vào nhóm nội dung bị Google coi là spam quy mô lớn**.

Khác với `D:\Codex\workspaces\Create content blog` (pipeline duyệt Lark → WordPress),
project này chỉ lo **chất lượng nội dung và SEO**. Không có quyền publish, không gọi CMS.

## Đọc trước khi làm bất cứ việc gì

| Việc | Đọc |
|---|---|
| Bất kỳ | `docs/00-nguyen-tac.md` |
| Tự tìm chủ đề từ nguồn chính thống (**tùy chọn**, ngoài quy trình chính) | `docs/09-phat-hien-chu-de.md` |
| Tra cứu hoặc cập nhật kho tri thức | `docs/11-wiki-tri-thuc.md` + `wiki/schema.md` |
| Nhận từ khóa + volume từ người dùng, phân loại intent | `docs/01-intent-va-keyword.md` |
| Lên outline | `docs/02-chuan-outline.md` + `templates/outline.md` |
| Đọc sườn top 5 và tìm mức sàn | `docs/02-chuan-outline.md` + `scripts/serp_outline.py` |
| Viết bài | `docs/03-giong-van-nguoi-that.md` + `docs/04-chinh-sach-nguon.md` |
| Viết lại đoạn nghe như máy (**bắt buộc**, xem quy tắc 13) | `.claude/skills/humanizer-bds/SKILL.md` |
| Nắn vào giọng nhà Muaban.net (**bắt buộc**, xem quy tắc 15) | `docs/12-giong-nha-muaban.md` + `.claude/skills/giong-muaban-bds/SKILL.md` |
| Sửa câu nói ngược kiểu dịch, và gọi người đọc (**bắt buộc**, xem quy tắc 17) | `docs/13-cu-phap-tieng-viet.md` |
| SEO on-page, internal link, schema | `docs/05-seo-onpage.md` |
| Chọn URL đích cho internal link | `scripts/internal_links.py` + `reference/internal-links-mbn.csv` |
| Quy chuẩn on-page của dự án (từ Google Sheet) | `docs/10-quy-chuan-onpage.md` |
| Schema, link out, làm sạch code — kỹ thuật SEO (**bắt buộc**, xem quy tắc 18) | `docs/10-quy-chuan-onpage.md` mục E |
| Rủi ro chính sách Google | `docs/06-chinh-sach-google.md` |
| QA trước khi bàn giao | `docs/07-qa-va-ban-giao.md` |
| Tìm ảnh cho bài, và đưa bản nháp lên WordPress (**bắt buộc**, xem quy tắc 19) | `docs/14-anh-va-ban-nhap-wordpress.md` |
| Tìm ảnh trên internet, xem, chọn, ghi manifest và chèn vào bài | `.claude/skills/tim-anh-bds/SKILL.md` + `scripts/image_search.py` |
| Đồng bộ và duyệt trên Lark | `docs/08-dong-bo-lark.md` |
| Dựng dự án trên máy chủ (tài liệu cho đội IT, không phải quy tắc nội dung) | `docs/15-trien-khai-vps.md` |
| Đưa repo lên GitHub, cài trên máy mới, làm việc chung trên một Base | `docs/16-dua-len-github.md` |

## Hard rules

1. **Zero fabrication.** Không tự tạo số liệu, giá, quy hoạch, văn bản pháp lý, ngày ban hành,
   tên chuyên gia, trích dẫn, khảo sát, URL nguồn, hay trải nghiệm cá nhân. Thiếu bằng chứng thì
   ghi `GAP` vào evidence ledger và **thu hẹp câu chữ**, không lấp bằng câu chung chung.
2. **Mọi claim vật chất phải có nguồn + ngày.** Một dòng trong `evidence-ledger.csv` cho mỗi claim.
   Nguồn phải thực sự chứa thông tin đó; không dùng nguồn "có vẻ liên quan".
   Ledger là nơi giữ `claim_id`; **thân bài không chèn ký hiệu `[Cxx]`** mà nêu tên văn bản ngay
   trong câu (quy tắc 16b).
3. **Không viết thay chuyên gia.** Không gán tác giả, chức danh, bằng cấp chưa xác minh.
   Bất động sản là YMYL: câu chữ về pháp lý, thuế, tín dụng, đầu tư phải có phạm vi, mốc thời gian,
   giới hạn và khuyến nghị tham vấn chuyên môn.
4. **Không hứa hẹn.** Cấm mọi câu bảo đảm tăng giá, sinh lời, thanh khoản, thắng kiện, duyệt vay,
   hay thứ hạng Google.
5. **Outline phải tổng hợp từ top 5, theo bốn quy tắc.** (a) Chép danh sách heading của top 5 vào
   `competitors.json`, ghi đúng thứ hạng thật — vị trí 6 trở xuống không tính. (b) Chủ đề đối thủ
   có thì mình phải có; muốn bỏ thì khai báo kèm lý do, bỏ im lặng không được chấp nhận.
   (c) Phải có ít nhất một mục không ai có. (d) Heading viết rõ ý và **không trùng câu chữ** của họ
   — cùng chủ đề thì được, cùng câu chữ là đạo văn. `serp_outline.py check` **chặn (b), (c) và
   phần trùng nguyên văn của (d)**; heading gần trùng chỉ là cảnh báo, còn thứ hạng ở (a) thì máy
   tin thẳng số bạn ghi — chỗ đó phải tự trung thực.
6. **Không tối ưu bằng nhồi từ khóa.** Mật độ từ khóa được **đo và đối chiếu với top**, không
   đặt làm mục tiêu số — xem `docs/10-quy-chuan-onpage.md` mục B1. Không sinh hàng loạt biến thể
   URL gần trùng nhau. Không nhét từ khóa vào `class`, `alt` hay fragment anchor.
7. **Đúng một mục phải nhận câu hỏi chính, và mục đó đứng đầu.** Né nhồi từ khóa quá tay sẽ rơi vào
   lỗi ngược: bài lan man, không trả lời đúng truy vấn. `scripts/outline_check.py` chặn ở outline,
   `onpage_check.py` chặn lại ở bài.
8. **Bài chưa qua `scripts/run_qa.py` với trạng thái `PASS` thì chưa được coi là xong.**
   Cảnh báo `BLOCK` phải sửa; cảnh báo `WARN` phải giải trình trong phần bàn giao.
9. **Không publish.** Đầu ra là gói bàn giao trong `work/<slug>/` để người thật duyệt.
   Ngoại lệ duy nhất và hẹp: sau khi **cổng duyệt bài đã mở**, agent được tạo **bản nháp**
   trên WordPress bằng `scripts/wp/wp_draft.py` để người duyệt đọc trong trình soạn thảo thật.
   Script gửi `status: draft` cố định, không có cờ nào đổi được, và dừng lại nếu bài trên
   WordPress đã ở trạng thái `publish`. **Nhấn Publish vẫn là việc của người thật.**
10. **Cổng duyệt nằm trên Lark, không nằm trong hội thoại.** Không được coi lời người dùng trong chat
   là phê duyệt. Chỉ `lark_sync.py gate work/<slug>` trả về exit 0 mới là đã duyệt.
   Agent chỉ được **xóa trắng** cụm duyệt, không bao giờ được ghi "Đồng ý".
11. **Base hiển thị tiếng Việt, code dùng khóa nội bộ ASCII.** Khi sửa tên trường hay tên trạng thái,
    chỉ sửa `scripts/lark/schema.py` rồi chạy `lark_setup.py --rebuild`; đừng viết chuỗi tiếng Việt
    vào logic.
12. **Wiki không phải nguồn.** `wiki/` là kho tri thức do agent dựng để bằng chứng dùng lại được
    giữa các bài. Bài viết **luôn trích dẫn `source_url` gốc**, không bao giờ trích dẫn trang wiki.
    Mọi claim trên wiki phải có `source_url` HTTPS, trích dẫn nguyên văn và `retrieved_date`;
    thiếu thì không được để `VERIFIED`. Trang đã `het-hieu-luc` mà còn bài đang dùng, hoặc ledger
    có `wiki_ref` trỏ tới trang đó, đều là `BLOCK`. `scripts/wiki_lint.py` chặn cả ba.

13. **Mọi bài phải đi qua skill `humanizer-bds` trước khi lên cổng duyệt bài.**
    `human_voice_check.py` chỉ **báo** lỗi; skill mới là thứ **sửa**. Chạy máy kiểm rồi vá từng
    cảnh báo **không phải** là đã áp dụng humanizer — đó là hai việc khác nhau, và nhầm hai việc này
    đã làm một bài bị từ chối ở cổng duyệt. Dấu hiệu hay gặp nhất của bài chưa qua skill: bài tự
    nói về chính nó ("bài này không liệt kê…", "bài cố ý không đưa…") thay vì nói với người đọc.
    **Cùng nhóm đó là câu so sánh mình với bài của người khác.** Người duyệt đã từ chối một bài với
    lý do nguyên văn *"Không ai viết theo kiểu so với các bài viết khác như nội dung này"*, câu bị
    chỉ ra là *"Phần này là chỗ mà hầu hết bài viết cùng chủ đề bỏ trống…"*. Người đọc không quan
    tâm bài khác viết gì, họ cần câu trả lời. Khoảng trống của đối thủ là thứ để ghi vào
    `serp-notes.md` cho người duyệt đọc, không phải để viết vào bài. Nhóm `self_comparison` trong
    lexicon nay bắt cả kiểu câu này lẫn kiểu dẫn đường trong bài ("như mục II vừa nói").
    `qa-report.md` phải ghi rõ đã áp dụng và đổi những gì.
14. **Outline và bài viết đều theo format hệ Blog Muaban.net.** Hai dòng `Title:` và `H1:` mở đầu
    outline, dòng `Mọi thắc mắc liên hệ người lên outline <tên>`, sapo đặt ở **H2**, mục chính đánh
    số **La Mã** (`I.`, `II.`), mục con đánh số **Ả Rập** (`1.`, `2.`), và **`Lời kết`** là mục cuối.
    Bài viết giữ nguyên cấu trúc đó, không tự thêm mục lục hay đổi cấp heading.
    Chi tiết và ba chỗ đã điều chỉnh so với sheet gốc: `docs/02` mục "Format outline của hệ Blog
    Muaban.net". `outline_check.py` kiểm outline, `onpage_check.py` kiểm bài — cả hai ở mức `WARN`
    vì đây là quy ước trình bày, không phải ràng buộc nội dung.

15. **Mọi bài phải đi qua skill `giong-muaban-bds`, và phải có mục dẫn về tin đăng
    Muaban.net đặt áp chót.** Giọng nhà không còn là chuyện cảm tính: ngưỡng được **đo từ 24
    bài thật** đang đăng, lưu ở `reference/muaban-blog/`, sinh ra bởi
    `house_voice_profile.py` và đối chiếu bởi `house_voice_check.py`. Thiếu mục
    "Tìm ... trên Muaban.net" là `BLOCK`.

    **Một ngoại lệ, và nó phải được khai báo.** Blog không chỉ có bất động sản — chuyên mục
    "Điềm báo" có 140 bài — và gắn mục tin đăng vào một bài điềm báo dân gian thì rất gượng. Người
    duyệt đã yêu cầu bỏ: *"Bài viết này không thuộc bất động sản nên khó có thể cho thêm heading
    IX. Tìm nhà đất và phòng trọ trên Muaban.net vào. Hãy xoá đi."* Bài ngoài mảng bất động sản
    được miễn khi `brief.yaml` ghi `muaban_listing_section: false` **kèm**
    `listing_section_skip_reason`; `house_voice_check.py` khi đó hạ `BLOCK` xuống một dòng `INFO`
    ghi lại lý do cho người duyệt sau đọc. Không có brief, hoặc khai mà không ghi lý do, thì không
    được miễn. Liên kết nội bộ vẫn phải còn — chuyển vào câu kết bài.
    Quy tắc này đã **sửa ngược ba thứ** mà dự án từng làm sai, vì đo ra chúng đẩy bài xa khỏi
    giọng thật: (a) `human_voice_check.py` không còn kiểm nhịp câu — ba ngưỡng cũ đòi văn
    giật cục trong khi bài thật viết câu dài và đều; (b) các cụm kết bài như "Hy vọng...",
    "Đừng quên theo dõi Muaban.net" và cụm mở bài "Bài viết dưới đây sẽ..." đã được gỡ khỏi
    bộ lọc sáo ngữ, giữ lại ở khóa `house_voice_allowed`; (c) lặp cụm từ khóa chính ở nhiều
    heading hạ từ `BLOCK` xuống `INFO`.
    Ba thay đổi (b) và (c) là **quyết định của chủ dự án**, không phải nới ngưỡng cho bài qua
    cửa. Riêng (c) vẫn là rủi ro chính sách Google đã biết và được chấp nhận có ý thức — ghi
    rõ ở `docs/12-giong-nha-muaban.md` mục "Cái giá đã trả".
    Bốn rào không đổi: không bịa đặt, không hứa hẹn, đủ bốn tín hiệu YMYL, không chạm bảy thứ
    mà `humanizer-bds` đã khoá.

16. **Đây là blog tiếng Việt, viết cho người Việt đọc.** Bộ từ vựng chống văn máy của dự án
    thích ứng từ nguồn tiếng Anh (blader/humanizer, Wikipedia "Signs of AI writing"), nên mỗi khi
    một quy tắc gốc tiếng Anh đánh nhau với cách viết tiếng Việt bình thường thì **cách viết tiếng
    Việt thắng**. Cách phân xử: đếm xem pattern đó nổ bao nhiêu lần trên kho bài thật ở
    `reference/muaban-blog/` (nay **24 bài**); nổ trên bài thật thì không phải lỗi.

    **Cơ chế này chỉ áp cho pattern thừa hưởng từ nguồn tiếng Anh, không áp cho pattern
    tồn tại để giữ quy tắc 1 và quy tắc 4.** Đếm lại toàn bộ lexicon trên 24 bài thật cho
    thấy bốn nhóm vẫn nổ trên bài thật mà dự án **cố ý giữ nguyên**: `re_cliches`
    ("tiềm năng tăng giá", "vị trí đắc địa" — 4 bài dùng), `guarantees` ("không có rủi
    ro" — 1 bài), `vague_authority` ("theo thống kê", "theo các chuyên gia" — 3 bài) và
    `empty_openers` (1 bài). Bài thật dùng chúng không làm chúng hết là hứa hẹn hay hết là
    bịa nguồn. Ba nhóm đã nới theo cơ chế trên vì chúng thuần là chuyện văn phong tiếng
    Việt: `filler_connectors` 8 → 12 (23/24 bài nổ, nhiều nhất 11 lần),
    `repetitive_structures` 2 → 4 ("không chỉ... mà còn", "vừa... vừa" là cấu trúc liên
    kết bản địa), và ba cụm `bí quyết` / `bí kíp` / `bật mí` chuyển sang `house_voice_allowed`
    (12 bài dùng — đó là từ vựng đặt tiêu đề của tòa soạn).

    Cơ chế này chỉ **gỡ** được pattern bắt oan; nó không bao giờ tự **thêm** pattern tiếng
    Việt còn thiếu, và chỗ thiếu đó chính là quy tắc 17. Hai hệ quả bắt buộc:

    (a) **Các câu phải liên kết với nhau.** Từ nối như "tuy nhiên", "vì vậy", "ngoài ra",
    "bên cạnh đó" là phương tiện liên kết của tiếng Việt, **không phải sáo ngữ**. Bài thật dùng
    3,5–8,7 cụm trên 1.000 từ; `house_voice_check.py` đo chỉ số `connector_per_1000` và cảnh báo
    cả khi quá thấp. Không được cắt từ nối hàng loạt cho "gọn câu" — đó là lời khuyên của văn
    tiếng Anh, và nó đã làm một bài bị từ chối vì các câu đứng rời nhau. Muốn gọn thì **gộp hai
    câu thành một câu có mệnh đề phụ**, đừng cắt cụm nối rồi để hai câu cụt cạnh nhau.
    Hai ngưỡng đã sửa vì lý do này: `filler_connectors` từ 6 lên 8, và `MAX_SAME_OPENER` từ 3 lên
    7 (ngưỡng 3 khiến **cả 12/12** bài thật bị cảnh báo oan, đo khi kho còn 12 bài).

    (b) **Không chèn ký hiệu trích dẫn `[Cxx]` vào thân bài.** Bài thật có đúng **0** ký hiệu;
    họ dẫn nguồn bằng cách nêu tên văn bản ngay trong câu, ví dụ *"Theo Điều 8 Nghị định
    103/2024/NĐ-CP, ..."*. Truy xuất nguồn **không mất đi**: nó nằm ở `evidence-ledger.csv` và ở
    khối "Căn cứ" cuối bài. Đánh đổi phải biết: khi không còn ký hiệu, `evidence_check.py` không
    còn đối chiếu được từng câu với từng claim, chỉ còn đối chiếu **con số** với ledger và dò
    trùng câu chữ với claim `GAP`. Phần ghép câu với claim từ nay do người viết và người duyệt
    giữ, không có chốt chặn bằng máy.

17. **Gọi người đọc là "bạn", và "bạn" phải là chủ ngữ của mọi câu khuyên.** Chủ dự án yêu cầu:
    *"Những lời khuyên, giải đáp thắc mắc cần phải bổ sung danh từ vào."* Viết **"Bạn nên hỏi chủ
    trọ..."**, không viết "Nên hỏi chủ trọ..." hay "Hãy kiểm tra...". Câu trả lời trong mục hỏi đáp
    cũng vậy. Không dùng **"mình"** để chỉ người đọc.

    Chỗ sai **không phải lượng** chữ "bạn" mà là **vai ngữ pháp** của nó: bài 001 có mật độ "bạn"
    nằm giữa dải bài thật, nhưng chỉ 18% câu khuyên lấy "bạn" làm chủ ngữ — trung vị bài thật là
    61% — còn mật độ mệnh lệnh vô chủ ngữ thì cao hơn cả bài thật cao nhất. Vì vậy đừng rắc thêm chữ "bạn" ở chỗ khác — hãy đổi
    chủ ngữ của chính câu khuyên. `house_voice_check.py` in ra từng câu thiếu danh xưng kèm số dòng,
    `BLOCK` khi dưới 50% và `WARN` khi dưới 75%. Hai mốc này **không** đo được từ kho bài thật (dải
    ở đó trải từ 0% tới 100%, trung vị 48%); chúng là **quyết định của chủ dự án**, như ba quyết
    định đã ghi ở quy tắc 15.

    Quy tắc này đi cùng một bộ **bảy chỉ số cú pháp** mới, đo từ 24 bài thật: `advice_subject_ratio`,
    `bare_advice_per_1000`, `minh_per_1000`, `viec_per_1000`, `abstract_start_ratio`,
    `front_clause_ratio`, `dem_per_1000`. Chúng bắt lỗi thứ hai mà chủ dự án chỉ ra — **"cấu trúc
    nói ngược giống tiếng nước ngoài"**: danh từ hóa động từ, chủ ngữ trừu tượng, mệnh đề phụ dài
    dồn lên trước nòng cốt câu. Sáu phép sửa cụ thể ở `docs/13-cu-phap-tieng-viet.md` mục D.

    Ba thứ đã phải sửa ngược vì chúng **dạy sai** đúng quy tắc này: (a) `docs/03` từng đặt câu
    *"Bạn nên cân nhắc kỹ trước khi mua"* ở cột **phải tránh** và thay bằng một câu không chủ ngữ —
    trong khi chỗ sai thật của câu đó là "cân nhắc kỹ" rỗng nghĩa, không phải hai chữ "Bạn nên";
    (b) cụm **"điều này cho thấy"** từng được kê đơn ở ba chỗ làm mẫu câu diễn giải, nay nằm trong
    nhóm `translated_syntax` với ngưỡng 0 vì 24/24 bài thật không dùng nó lần nào; (c) `docs/03`
    từng mở đầu bằng **"Không phải vì ngữ pháp"**, và câu đó đã khóa cả bộ kiểm khỏi việc đo cú
    pháp — suốt thời gian đó mọi chỉ số chỉ đo từ vựng và độ dài.

18. **Khai schema đúng bộ, và khai gì thì bài phải thật sự có thứ đó.** Tab *Kĩ thuật SEO* của
    file quy chuẩn đưa thêm năm công đoạn vào dự án — external link, làm sạch HTML code, schema,
    Content Gap, on-page nâng cao — đối chiếu từng mục ở `docs/10-quy-chuan-onpage.md` mục E.
    Bốn việc trong đó thuộc người viết, và `onpage_check.py` kiểm cả bốn:

    (a) **Schema**: `BlogPosting` + `BreadcrumbList` (đo 24/24 bài thật; không dùng `Article`), thêm
    `ImageObject` khi bài có ảnh và `FAQPage` khi bài có mục hỏi đáp. Khai một loại mà bài không có
    thứ tương ứng là `BLOCK`, vì đó là nói sai về chính bài viết — cùng hướng với quy tắc 1.
    (b) **Link out định nghĩa phải nằm trong thân bài**, gắn vào chính tên văn bản mà quy tắc 16b đã
    đòi nêu ngay trong câu. Khối "Căn cứ" cuối bài giữ vai trò danh sách tham khảo; dồn hết liên kết
    ngoài xuống đó là `WARN`.
    (c) **Miền của liên kết ngoài phải có trong `evidence-ledger.csv`.** File quy chuẩn đòi nguồn có
    DR ≥ 20; dự án không có số đo đó và **bịa một con số DR là vi phạm quy tắc 1**, nên thay bằng
    điều kiện đo được này. Wikipedia được làm link out định nghĩa nhưng không được làm `source_url`
    cho claim (`docs/04`) — hai việc khác nhau, và cũng khác quy tắc 12 vốn nói về thư mục `wiki/`.
    (d) **Bản thảo là Markdown thuần**, không mang `<span>`, `<font>`, `style="..."` vào bài.

    Việc của khâu CMS thì Markdown không diễn đạt được — `target="_blank"`, `nofollow` cho mọi liên
    kết ngoài (bài thật làm với **20/20** liên kết), gỡ CSS inline, và mốc rà Content Gap bằng ngày
    đăng + 3 tháng — nên cả bốn phải được ghi thành **ghi chú cho người đăng bài** trong
    `qa-report.md`. Không ghi thì chúng biến mất khỏi quy trình. Mẫu ở `docs/07`.

    Hai bài học đi kèm. Thứ nhất, mục A8 của `docs/10` liệt kê đủ bộ schema từ 2026-09-15 nhưng
    **không một dòng code nào đọc trường `schema`**, nên bài 001 khai `Article` vẫn qua sạch — đúng
    loại lỗ hổng đã xảy ra với meta description, và cách chữa vẫn là đo bài thật rồi đặt ngưỡng.
    Thứ hai, 16/24 bài thật **không có liên kết ngoài nào**, nhưng ngưỡng "phải có ít nhất một liên
    kết nguồn" **vẫn giữ nguyên**: nó tồn tại để đỡ quy tắc 1 và quy tắc 2, không phải một quy tắc
    văn phong thừa hưởng từ tài liệu tiếng Anh, nên cơ chế phân xử của quy tắc 16 không áp vào đây.

19. **Bài phải có ảnh, và mỗi ảnh phải truy được về nguồn cùng giấy phép.** Chủ dự án chỉ ra
    bài đầu ra không có ảnh nào. Đo 24 bài thật: **6–10 ảnh mỗi bài** (trung vị 8, tức khoảng một
    ảnh cho mỗi mục La Mã), chỉ 1/24 bài không có ảnh, và **0/1.377** thẻ `<img>` có `alt` rỗng.
    Chú thích dài 7–20 từ và gắn với ý của mục, không phải "Ảnh minh họa".

    Thứ tự ưu tiên khi tìm ảnh: (a) tự dựng từ dữ liệu đã có nguồn — sơ đồ, bản đồ, bảng, biểu đồ;
    (b) ảnh chụp thật của đội ngũ; (c) kho ảnh có giấy phép rõ ràng, ghi đủ `source_url`, `creator`,
    `license`, `license_url`, `retrieved_date`; (d) ảnh của chính Muaban.net khi có xác nhận nội bộ.
    Không tìm được ảnh đúng ngữ cảnh Việt Nam thì **dựng sơ đồ**, đừng lấy ảnh nước ngoài cho có.

    **Ảnh AI dựng ra để minh họa một địa điểm, giấy tờ hay công trình có thật là vi phạm quy tắc 1** —
    nó trông như bằng chứng mà không phải. Ảnh AI chỉ dùng cho hình trang trí trừu tượng và phải ghi
    rõ trong manifest.

    `onpage_check.py` nay đọc `image-manifest.csv`: ảnh trong bài không có dòng manifest, hoặc dòng
    manifest chưa `CLEARED`, đều là `BLOCK`; bài không có ảnh nào là `WARN`. Trước ngày 24/09/2026
    quy chuẩn này đã nằm trong `docs/05` và `docs/07` nhưng **không có chỗ nào đọc file manifest** —
    cùng loại lỗ hổng đã xảy ra với meta description và với schema. Chi tiết ở
    `docs/14-anh-va-ban-nhap-wordpress.md`.

    **Ảnh từ internet đi qua skill `tim-anh-bds`**, công cụ `scripts/image_search.py`, nguồn
    Wikimedia Commons và Openverse. Ba điều bắt buộc: (a) **mở từng ảnh ra xem** trước khi chọn —
    tiêu đề trên kho không đáng tin; (b) ảnh **không được nói ngược lời khuyên** của bài, và chú
    thích chỉ nói điều nhìn thấy trong ảnh hoặc điều mô tả gốc ghi — không gắn địa danh Việt Nam
    cho ảnh chụp ở nước khác; (c) chỉ nhận **CC0, Public Domain, CC BY, CC BY-SA**. Ảnh có giấy phép
    NC hoặc ND, hoặc ảnh CC BY thiếu tác giả, là `BLOCK`. Ghi công do `wp_draft.py` tự in dưới mỗi
    ảnh CC BY; trước 25/09/2026 nó không in, tức là mọi ảnh CC BY đưa qua script đều vi phạm giấy
    phép — người đăng bài **không được xoá dòng ghi công** trên WordPress.

## Quy trình

```
bạn gõ từ khóa + volume trên Base, tích ô "Duyệt từ khoá"
       → intake kéo xuống máy → intent + SERP gap → evidence ledger → outline
       → [cổng outline] → draft → QA → [cổng bài] → bàn giao
```

**Đầu vào của quy trình là từ khóa chính và volume search do bạn cung cấp**, gõ thẳng vào bảng
Điều phối. Agent **không bao giờ** tự điền hay ước lượng volume — không có thì để trống, đúng
quy tắc 1.

Ô **`Duyệt từ khoá`** là công tắc chạy, **không phải cổng duyệt thứ ba**: nó không dùng cụm
`Kết quả duyệt` + `Người duyệt`, không đi qua `gate_status`, và không bị xóa trắng khi nội dung đổi.
Chưa tích thì dòng nằm im, nên bạn cứ nhập dở nhiều dòng rồi tích sau. **Agent không bao giờ tự tích
ô này.**

`lark_sync.py intake` kéo mọi dòng đã tích xuống máy: sinh slug từ truy vấn chính, tạo
`work/<slug>/` với brief + ledger rỗng + serp-notes, rồi ghi `Trạng thái = Đang lên outline` lên
Base. Chính việc ghi trạng thái đó là chốt chống chạy hai lần — lượt `intake` sau bỏ qua dòng đã có
trạng thái. Không có cổng duyệt chủ đề nữa: bạn đã chọn đề tài bằng chính việc đưa từ khóa.

Còn **hai cổng**, đều nằm trên Lark. Không nhảy từ từ khóa thẳng sang bài hoàn chỉnh: outline phải
được người thật duyệt trước khi viết, vì sửa outline rẻ hơn sửa bài rất nhiều.

Radar (`seo-radar-bds`) **không còn nằm trong quy trình chính**. Nó vẫn dùng được khi bạn muốn tìm ý
tưởng từ nguồn chính thống, nhưng đầu ra của nó chỉ là gợi ý để bạn chọn từ khóa, không tự tạo bản
ghi chờ duyệt.

`wiki/` chạy **song song** với quy trình này, không phải một bước trong đó và không có cổng duyệt.
Trước khi đi tìm nguồn cho một claim, tra wiki đã; sau khi xác minh được nguồn mới, ghi ngược vào
wiki để bài sau dùng lại. Chi tiết ở `docs/11-wiki-tri-thuc.md`.

**Duyệt xong thì luồng tự chạy tiếp, không cần nhắc.** Ba lớp cùng canh cụm duyệt: kênh theo dõi
`lark_watch.py` gắn qua Monitor (≈60 giây), hook `Stop` chạy `--todo` ở cuối mỗi lượt trả lời, và
hook `SessionStart` chạy `--once` + `--todo` mỗi lần mở phiên. Agent **phải gắn Monitor ngay sau mỗi
`push`** và gắn lại khi hết hạn. Giới hạn đã biết: không lớp nào chạy khi không có phiên nào mở, vì
phiên `@larksuite/cli` nằm trên máy này và bước sau khi duyệt là viết nội dung. Chi tiết ở
`docs/08-dong-bo-lark.md` mục "Duyệt là tự chạy".

Cả hai cổng dùng chung **một** cụm hai ô trên bảng Điều phối: `Kết quả duyệt = Đồng ý` +
`Người duyệt`. Trường `Trạng thái` cho biết đang duyệt cái gì. Phê duyệt tự hết hiệu lực khi nội dung
đổi hoặc khi vừa được dùng để qua một cổng. Chi tiết ở `docs/08-dong-bo-lark.md`.

## Lệnh thường dùng

```powershell
# Doc suon top 5 va kiem outline truoc khi dua len duyet
python scripts/serp_outline.py analyze work/<slug>/competitors.json
python scripts/outline_check.py work/<slug>/outline.md
python scripts/serp_outline.py check work/<slug>/outline.md

# QA bai viet
python scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json

# Giong nha Muaban.net (nguong do tu kho bai that, khong sua tay file JSON)
python scripts/house_voice_check.py work/<slug>/article.md
python scripts/house_voice_profile.py --show     # xem lai nguong do duoc tu kho
python scripts/corpus_fetch.py --category 3      # xem bai nao tren blog chua co trong kho
python scripts/corpus_fetch.py <url> [<url>...]  # tai them bai that vao kho, roi do lai

# Kho URL de di internal link (nhap tu sheet BDS MBN)
python scripts/internal_links.py find --brief work/<slug>/brief.yaml
python scripts/internal_links.py find "phong tro quan 10"
python scripts/internal_links.py stats
python scripts/internal_links.py build --from bds-mbn.csv   # lam moi khi sheet doi

# Ban nhap tren WordPress (chi chay khi cong duyet bai da mo; KHONG BAO GIO publish)
python scripts/wp/wp_draft.py --check                 # thu dang nhap
python scripts/wp/wp_draft.py work/<slug> --dry-run   # xem se gui gi
python scripts/wp/wp_draft.py work/<slug>             # tao / cap nhat ban nhap

# Lark
python scripts/lark/lark_sync.py intake                 # keo dong da tich cong tac tu Base ve may
python scripts/lark/lark_sync.py intake --content-id 001
python scripts/lark/lark_sync.py push   work/<slug>
python scripts/lark/lark_sync.py gate   work/<slug>
python scripts/lark/lark_sync.py pull   work/<slug>
python scripts/lark/lark_sync.py status

# Bao khi co ket qua duyet (hook SessionStart tu chay --once moi khi mo phien)
python scripts/lark/lark_workflow.py --show
python -u scripts/lark/lark_watch.py            # theo doi, tu dung sau 29 phut
python -u scripts/lark/lark_watch.py --once     # kiem mot luot (bao THAY DOI)
python scripts/lark/lark_watch.py --todo        # viec DANG CHO, exit 3 = co viec

# Wiki tri thuc (khong co cong duyet)
python scripts/wiki_lint.py
python scripts/wiki_index.py build
python scripts/wiki_index.py check

# Radar
python scripts/radar/radar.py sources
python scripts/radar/radar.py check --url "<url>" --event "<mô tả>"
python scripts/radar/radar.py add <file.json>
```
