---
name: seo-qa-bds
description: "QA và đóng gói bàn giao cho bài bất động sản: chạy máy kiểm (giọng văn, on-page, bằng chứng), đối chiếu từng con số với evidence ledger, kiểm tra rủi ro chính sách Google (scaled content abuse, YMYL, hứa hẹn), kiểm liên kết và ảnh, rồi dựng gói bàn giao kèm câu hỏi mở. Dùng khi người dùng nói: QA, kiểm tra bài, rà soát, fact check, kiểm tra trước khi đăng, đóng gói bàn giao, hoặc bài có bị coi là spam AI không."
---

# QA và bàn giao

Skill này chạy **Bước 4**. Đầu ra là gói bàn giao trong `work/<slug>/`, được đẩy lên Lark cho người
duyệt. **Không publish, không gọi CMS.**

## Đọc trước

1. `CLAUDE.md`
2. `docs/07-qa-va-ban-giao.md`
3. `docs/06-chinh-sach-google.md`
4. `docs/04-chinh-sach-nguon.md`
5. `docs/08-dong-bo-lark.md`
6. `docs/11-wiki-tri-thuc.md` (kết quả kiểm lại phải chảy ngược vào wiki)

## 1. Máy kiểm

```powershell
python scripts/run_qa.py work/<slug>/article.md --json work/<slug>/qa-report.json
python scripts/wiki_lint.py
```

Script tự tìm `evidence-ledger.csv` và `brief.yaml` cùng thư mục; SEO fields đọc từ front matter của bài.
Chạy riêng khi cần khoanh vùng: `human_voice_check.py`, `onpage_check.py`, `evidence_check.py`.

`wiki_lint.py` chạy trên toàn bộ `wiki/` và `work/`, không riêng bài này. Nó bắt thứ `run_qa.py`
không thấy được: dòng ledger có `wiki_ref` trỏ tới trang **đã hết hiệu lực** hoặc trang không tồn
tại. Một bài `PASS` mà dẫn căn cứ hết hiệu lực vẫn là bài sai.

- Mọi `BLOCK` **phải sửa**. Không bỏ qua bằng cách nới ngưỡng trong lexicon.
- Bài chưa đi qua skill `humanizer-bds` thì **chưa được đẩy lên cổng duyệt** (quy tắc 13).
  `qa-report.md` phải ghi rõ đã áp dụng và đổi những gì.
- Bài phải đúng format hệ Blog Muaban.net (quy tắc 14); cảnh báo `house_format` nào còn lại đều
  phải sửa hoặc giải trình.
- **Thân bài không được còn ký hiệu `[Cxx]` nào** (quy tắc 16b). `human_voice_check.py` cảnh báo
  nếu còn. Kiểm luôn mật độ từ nối: dưới 3,5 cụm trên 1.000 từ là các câu đang đứng rời nhau.
- Bài chưa đi qua skill `giong-muaban-bds` thì **chưa được đẩy lên cổng duyệt** (quy tắc 15 và 17).
  Chạy `python scripts/house_voice_check.py work/<slug>/article.md`: vượt mốc lệch mà máy in ra là
  chưa đạt, vì không bài thật nào trong `reference/muaban-blog/` lệch quá mốc đó. Đừng nhớ con số —
  nó đổi mỗi lần kho bài đổi. Thiếu mục dẫn về tin đăng Muaban.net là `BLOCK`. `qa-report.md` phải
  ghi số chỉ số lệch và giải trình từng cái còn lại.
- **Danh xưng người đọc là `BLOCK`, không giải trình được** (quy tắc 17). Dưới 50% câu khuyên lấy
  "bạn" làm chủ ngữ là chặn; máy in ra từng câu kèm số dòng, sửa đúng từng câu đó bằng cách thêm
  chủ ngữ. Hai chỗ hay đi kèm: mật độ "mình" chỉ người đọc, và mật độ mệnh lệnh vô chủ ngữ.
  Coi cả mục hỏi đáp: câu trả lời cũng phải gọi "bạn".
- **Ba chỉ số cú pháp** cũng nằm trong bộ kiểm: danh từ hóa bằng "việc", câu mở bằng chủ ngữ trừu
  tượng, câu mở bằng mệnh đề phụ dài. Vượt dải là dấu hiệu bài đang viết theo cú pháp dịch — sáu
  phép sửa ở `docs/13-cu-phap-tieng-viet.md` mục D. Đừng sửa bằng cách xóa hết chữ "việc": "việc"
  là từ bình thường của tiếng Việt, chỉ sai khi quá dày.
- **Đừng vượt ngược lên.** Gọi người đọc quá dày cũng là lệch giọng: `ban_per_1000` có trần, và bài
  thật vẫn dùng mệnh lệnh vô chủ ngữ 0,71–4,20 lần trên 1.000 từ. Mục tiêu không phải 100%.
- Mọi `WARN` còn lại phải có một dòng giải trình trong `qa-report.md`.
- `--lenient` chỉ dùng khi rà soát sơ bộ, không dùng ở lượt bàn giao.

> Máy chỉ bắt được lỗi cơ học. Bài có **đúng** không, có **hữu ích** không, có **bịa** không —
> ba thứ đó chỉ agent và người duyệt kiểm được. `PASS` không có nghĩa là xong.

## 2. Đối chiếu bằng chứng — làm thủ công, không tin script hoàn toàn

Với **từng** số, tỷ lệ, ngày, số hiệu văn bản trong bài:

- Tìm dòng ledger đỡ nó, đọc `supporting_quote`, xác nhận nguồn **thật sự chứa** thông tin đó.
  Nguồn cùng chủ đề nhưng không chứa claim thì không phải nguồn của claim đó.
- Mở lại `source_url`; chết thì tìm bản thay thế hoặc hạ claim.
- Văn bản pháp luật: kiểm tra **đã bị sửa đổi hoặc thay thế chưa** tại thời điểm bàn giao.
- Cập nhật `retrieved_date` đúng ngày kiểm cuối.

Mọi dòng `GAP` phải đã được xử lý: bỏ, thu hẹp, hoặc chuyển thành hướng dẫn tự tra cứu.
Không để `GAP` lọt vào bài dưới dạng câu khẳng định.

**Kết quả kiểm lại phải chảy ngược vào wiki.** Đây là lượt xác minh kỹ nhất của cả quy trình; bỏ
phí nó thì bài sau lại đi kiểm từ đầu:

- Nguồn còn sống và còn đúng → cập nhật `retrieved_date` của claim và `updated` của trang wiki.
- Văn bản đã bị thay thế → đặt `status: het-hieu-luc` + `superseded_by` cho trang cũ, rồi chạy lại
  `wiki_lint.py`. Nó sẽ gọi tên **mọi bài khác** đang dẫn văn bản đó, không chỉ bài đang QA.
- Nguồn chết → hạ claim xuống `PARTIAL` hoặc `GAP` trên wiki, đừng chỉ sửa trong ledger của bài này.

Ghi một dòng `wiki/log.md` cho mỗi thay đổi, rồi `python scripts/wiki_index.py build`.

## 3. Rủi ro chính sách Google

Trả lời **có/không**, không trả lời "gần như":

- Bài có ít nhất một thứ không tìm được ở 5 kết quả đầu hiện tại?
- Không có bài nào khác trên blog phục vụ cùng intent (hoặc đã quyết định gộp/cập nhật)?
- Nếu bỏ hết từ khóa đi, bài vẫn còn lý do tồn tại?
- Đọc xong người ta làm được việc, không phải đi tìm tiếp?
- Tiêu đề mô tả đúng nội dung, không phóng đại?

**Kiểm scaled content abuse:** lấy bài này và một bài cùng cụm đặt cạnh nhau. Nếu đổi tên địa bàn
hoặc từ khóa mà bài vẫn đúng, hai bài đó nên là một — đề xuất gộp.

**Kiểm YMYL:** phạm vi, mốc dữ liệu, căn cứ có liên kết, giới hạn, khuyến nghị tham vấn, đường báo lỗi.

**Kiểm hứa hẹn:** không câu nào bảo đảm kết quả tài chính hoặc pháp lý.

## 4. Liên kết, schema và ảnh

Mở **thật** từng liên kết trong bài, đối chiếu với link map ở `outline.md`. HTTPS, còn sống,
đúng trang chứa thông tin cụ thể (không trỏ về trang chủ của nguồn). Anchor mô tả đích đến.
External có `rel="noopener"`.

Ba thứ của tab *Kĩ thuật SEO* (quy tắc 18, chi tiết ở `docs/10` mục E):

- **Link out định nghĩa nằm trong thân bài**, gắn vào chính tên văn bản đã nêu trong câu. Mọi liên
  kết ngoài dồn xuống khối "Căn cứ" là `WARN`.
- **Miền của liên kết ngoài phải có trong ledger.** Không có thì thêm dòng ledger cho nguồn đó, hoặc
  bỏ liên kết. Đây là chỗ dự án thay tiêu chí DR ≥ 20 của file quy chuẩn bằng một tiêu chí đo được.
- **Schema khai đúng bộ**: `BlogPosting` + `BreadcrumbList`, thêm `ImageObject` khi có ảnh và
  `FAQPage` khi có mục hỏi đáp. Khai một loại mà bài không có thứ tương ứng là `BLOCK`.

### Ghi chú cho người đăng bài — bắt buộc trong `qa-report.md`

Bốn việc này thuộc khâu CMS, Markdown không diễn đạt được, nên không ghi ra là mất hẳn:

1. Từng URL ngoài kèm `target="_blank" rel="nofollow noopener"` (liên kết tài trợ:
   `rel="sponsored nofollow noopener"`). Bài thật gắn cho **20/20** liên kết ngoài.
2. Bộ schema đã khai, nhắc chèn ở `<head>`.
3. Nhắc gỡ CSS inline mà trình soạn thảo sinh ra, giữ nội dung trong `<p>`.
4. Mốc rà Content Gap: **ngày đăng + 3 tháng**. Chưa biết ngày đăng thì ghi đúng cụm đó.

Mỗi ảnh có một dòng `image-manifest.csv` với nguồn, tác giả, giấy phép, ngày lấy, alt. Máy kiểm
đối chiếu từng ảnh trong bài với manifest: thiếu dòng hoặc `rights_status` chưa `CLEARED` là `BLOCK`.
Bài không có ảnh nào là `WARN` — 23/24 bài thật có ảnh, thường 6–10 ảnh (quy tắc 19).
Rights không rõ → đặt `BLOCKED`, dùng placeholder hoặc image brief, ghi vào phần câu hỏi mở của `qa-report.md`.

## 4b. Sau khi cổng duyệt bài mở: tạo bản nháp trên WordPress

```powershell
python scripts/wp/wp_draft.py work/<slug> --dry-run
python scripts/wp/wp_draft.py work/<slug>
```

Chỉ chạy **sau khi** `lark_sync.py gate work/<slug>` trả về exit 0 — chính script cũng tự kiểm lại
điều đó, cộng với QA `PASS` chạy lại tại chỗ và mọi ảnh `CLEARED`. Script gửi `status: draft` cố
định và dừng nếu bài trên WordPress đã `publish`: **nhấn Publish là việc của người thật** (quy tắc 9).
Lần chạy sau cập nhật đúng bản nháp cũ nhờ `work/<slug>/.wp.json`.

## 5. Gói bàn giao

```
work/<slug>/
├── brief.yaml              # intent, truy vấn, thực thể, câu hỏi, url_decision, người đọc, CTA
├── serp-notes.md           # ghi chép SERP và khoảng trống đã tìm được
├── competitors.json        # heading của top 5 — thiếu file này thì serp_outline.py exit 2
├── evidence-ledger.csv     # một dòng mỗi claim, có supporting_quote; wiki_ref nếu lấy lại từ wiki
├── outline.md              # sườn + link map + image plan
├── article.md              # bài hoàn chỉnh; SEO fields nằm trong front matter
├── qa-report.md            # kết quả máy kiểm + giải trình WARN + câu hỏi mở + checklist
├── qa-report.json          # kết quả máy đọc được
└── image-manifest.csv      # chỉ khi bài có ảnh
```

**Tám file, cộng `image-manifest.csv` khi bài có ảnh.** `.lark.json` là trạng thái đồng bộ do
`lark_sync.py` quản lý — không sửa tay, không thuộc gói bàn giao.

Phần **câu hỏi mở** trong `qa-report.md` là phần quan trọng nhất với người duyệt: claim nào phải bỏ
và vì sao, chỗ nào cần chuyên gia xác nhận, dữ liệu nội bộ nào cần xin, rủi ro còn lại và mức độ.

**Không giấu khoảng trống bằng câu mơ hồ.** Một bài trung thực về giới hạn của nó đáng tin hơn
một bài trông hoàn hảo.

## 6. Đẩy lên Lark

```powershell
python scripts/lark/lark_sync.py push work/<slug>
```

Push đưa lên: ô **Máy kiểm** dạng `ĐẠT · 0 chặn · 3 cảnh báo`, ô **Tóm tắt bằng chứng** dạng
`12 đã xác minh · 1 thiếu nguồn`, toàn bộ evidence ledger vào bảng **Bằng chứng**, và bốn tệp
Markdown (brief, outline, bài, qa-report) lên Drive.

Chỉ push để xin duyệt bài khi máy kiểm `ĐẠT`. Còn lỗi chặn thì sửa trước; đẩy một bài còn lỗi chặn
lên cổng duyệt là đẩy việc của mình sang người khác.

Giải trình từng `WARN` còn lại nằm trong `qa-report.md` — đó là chỗ người duyệt đọc để biết bạn đã
cân nhắc hay bỏ qua.

## 7. Chờ duyệt, không tự duyệt

```powershell
python scripts/lark/lark_sync.py gate work/<slug>
```

Exit 0 nghĩa là người thật đã duyệt đúng bản hiện tại. Agent **không bao giờ** ghi "Đồng ý" vào
ô Kết quả duyệt; chỉ được xóa trắng cụm duyệt khi nội dung đổi.

Nếu bị từ chối: đọc ô **Góp ý**, sửa, rồi `push` (số Bản tự tăng, cụm duyệt tự xóa) và chờ duyệt lại.

## 8. Báo cáo

Tóm tắt cho người duyệt trong vài dòng:

- Trạng thái máy kiểm: `PASS`/`FAIL`, số `BLOCK` đã sửa, số `WARN` còn lại.
- Số claim `VERIFIED` / `PARTIAL` / `GAP`.
- Việc người duyệt **bắt buộc** phải làm trước khi đăng (nếu có).
- `review_after` và các trigger làm mới.
- Đường dẫn Base và `content_id` của bản ghi.

Việc đăng bài, gắn tác giả, tạo bản nháp CMS thuộc quy trình của
`D:\Codex\workspaces\Create content blog`. Skill này không đụng tới.
