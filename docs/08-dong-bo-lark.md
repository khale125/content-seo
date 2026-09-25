# 08 — Đồng bộ Lark Base

Base Lark là nơi bạn duyệt. `work/<slug>/` trên máy là nơi agent làm việc.

**Base:** xem `base_url` trong `scripts/lark/config.json`.


## Bạn chỉ phải nhìn hai trường và điền hai ô

Mở bảng **Điều phối** — hoặc nhanh hơn, mở view **Đang chờ tôi duyệt**, nó đã lọc sẵn đúng những
bản ghi đang đứng ở một cổng và chưa ai duyệt. Đọc trường **Trạng thái** và **Việc kế tiếp**.

## Nhập từ khoá trên Base để luồng chạy

Pipeline đi hai chiều. `push` đẩy artifact từ máy lên Base; **`intake` đi chiều ngược lại** và là
cách duy nhất một dòng bạn gõ tay trên Base biến thành thư mục làm việc dưới máy.

```powershell
python scripts/lark/lark_sync.py intake                  # moi dong da tich cong tac
python scripts/lark/lark_sync.py intake --content-id 001  # chi mot ma bai
```

Dòng được nhặt phải đủ **ba** điều kiện: ô `Duyệt từ khoá` đã tích, `Truy vấn chính` đã điền, và
`Trạng thái` **còn trống**. Thiếu một trong ba thì lệnh bỏ qua và nói rõ vì sao.

`intake` làm năm việc:

1. Sinh slug bằng `qa_common.make_slug()` — bỏ dấu, nối gạch ngang, **không** cắt ngắn và **không**
   bỏ hư từ. Cắt ngắn theo số từ sẽ làm đứt từ ghép tiếng Việt (`thổ cư` thành `tho`), còn bỏ hư từ
   thì ngược với chính blog: slug thật của tòa soạn giữ "gan" trong
   `kinh-nghiem-thue-tro-gan-truong-dai-hoc-su-pham-ky-thuat-tphcm`. Trùng thư mục đã có của bản ghi
   khác thì thêm hậu tố số.
2. Tạo `work/<slug>/` với `brief.yaml`, `evidence-ledger.csv` (chỉ header), `serp-notes.md`,
   `competitors.json`. **Không** tạo `outline.md`: một template chưa điền vẫn là file có nội dung,
   và sẽ bị `substantive()` tính nhầm là outline đã viết xong.
3. Điền vào brief: mã bài, slug, truy vấn chính, và **volume đúng bằng con số bạn gõ, kể cả khi
   là 0**.
4. Ghi `.lark.json` kèm `record_id` để `push` / `pull` / `gate` sau này bám đúng dòng.
5. Ghi `Trạng thái = Đang lên outline` lên Base. **Đây là chốt chống chạy hai lần**, không phải chỉ
   để hiển thị.

Watcher báo dòng từ khoá mới ngay **lần đầu** thấy:

```
[LARK] TU KHOA MOI 001 "kinh nghiem thue tro gan truong..." vol=0 next=intake+seo-outline-bds
```

Nhánh này cố ý phá lệ "lần đầu chỉ lấy mốc" của ba nhánh còn lại. Lý do: dòng đó do bạn vừa gõ tay
trên Base chứ không phải do agent push lên, nên lần đầu thấy chính là lúc cần báo.

## Thứ tự cột đọc từ trái sang phải theo luồng công việc

Cột trên bảng Điều phối được xếp thành sáu nhóm, đúng theo thứ tự việc diễn ra:

| Nhóm | Cột | Ai điền |
|---|---|---|
| Bạn đưa đề bài | Mã bài · Truy vấn chính · Volume · **Duyệt từ khoá** | bạn gõ từ khóa, volume, rồi tích công tắc |
| Luồng đang ở đâu | Trạng thái · Việc kế tiếp · Bản | agent |
| Tài liệu để bạn đọc | Brief · Outline · Bài viết | agent |
| Tín hiệu chất lượng | Tóm tắt bằng chứng · Máy kiểm · Claim | agent |
| Cụm bạn bấm | Kết quả duyệt · Người duyệt · Góp ý | **bạn** |
| Thứ sẽ lên Google | Quyết định URL · Slug · Tiêu đề · Mô tả meta | agent lấy từ front matter, bạn sửa tay nếu cần |

Cột **Mã bài** buộc đứng đầu: đó là trường chính, và API của Lark tự đẩy trường chính lên vị
trí một dù xếp thế nào.

Thứ tự này do `PIPELINE_COLUMNS` trong `scripts/lark/schema.py` quyết định. Đổi thứ tự ở đó rồi
chạy `lark_setup.py --rebuild` là Base đổi theo, **trên mọi view** chứ không chỉ view đầu tiên —
người duyệt làm việc trên view đã lọc sẵn, để view đó lệch thì coi như chưa sắp gì. `--verify`
báo `[COT ]` khi thứ tự trên Base lệch khỏi schema, vì cột mới thêm luôn bị Lark đẩy xuống cuối.

Ẩn cột thì **không phải lỗi**. Người duyệt có quyền ẩn vài cột trong view của mình, và khi đó
`--verify` báo `[AN ]` kèm số cột đang ẩn rồi vẫn trả exit 0 — miễn thứ tự các cột còn lại đúng.
Trước đây hai việc này bị gộp làm một, nên một view có cột ẩn bị báo là "thứ tự cột lệch", và cách
sửa duy nhất là `--rebuild` — tức hiện lại đúng những cột người duyệt đã cố ý ẩn.

Trường có trên Base mà không nằm trong schema — như cột **Claim** liên kết ngược từ bảng Bằng
chứng — được chèn ngay sau mốc khai báo ở `VIEW_EXTRA_AFTER`, để nó nằm cạnh nhóm bằng chứng
thay vì bị đẩy xuống cuối.
Khi Việc kế tiếp nói *"Bạn duyệt ..."*, mở link tương ứng (**Brief** / **Outline** / **Bài viết**),
đọc, rồi:

- **Duyệt:** `Kết quả duyệt = Đồng ý`, `Người duyệt = tên bạn`. Xong.
- **Từ chối:** `Kết quả duyệt = Từ chối`, `Người duyệt = tên bạn`, `Góp ý = lý do cụ thể`.

Không có gì khác phải điền. `Kết quả duyệt` là trường lựa chọn, bấm chứ không gõ — và khác với
dropdown của bảng tính, Base **từ chối** giá trị lạ chứ không chỉ cảnh báo.

## Vì sao chỉ có một cụm duyệt cho cả hai cổng

Một bản ghi tại một thời điểm chỉ đứng ở đúng một cổng. Trường **Trạng thái** cho biết bạn đang
duyệt cái gì:

| Trạng thái | Bạn đang duyệt | Mở trường nào |
|---|---|---|
| Đang lên outline | *không phải cổng duyệt* — agent đang nghiên cứu | — |
| Chờ duyệt outline | Sườn bài | **Outline** |
| Chờ duyệt bài | Bài hoàn chỉnh | **Bài viết** (giải trình cảnh báo QA nằm ở `work/<slug>/qa-report.md`) |
| Đang viết bài | — (agent đang làm) | |
| Đã duyệt, chờ bàn giao | — (xong) | |

Ba cụm duyệt riêng tốn 12 trường để diễn đạt đúng một thông tin mà trường Trạng thái đã nói.

## Phê duyệt cũ không bao giờ được dùng lại

Đây là điều kiện để mô hình một cụm duyệt vẫn an toàn. Agent **xóa trắng** cụm duyệt trong
hai trường hợp:

1. **Nội dung đã đổi** — checksum của `outline.md` + `article.md` + `evidence-ledger.csv` khác
   lần trước. Kèm theo đó số **Bản** tăng lên.
2. **Phê duyệt vừa được dùng để qua một cổng** — nó không còn áp dụng cho chặng tiếp theo.

Nghĩa là bạn luôn duyệt đúng thứ đang nằm trước mặt, và không bao giờ có chuyện một chữ
"Đồng ý" còn sót lại từ chặng trước tự mở cổng sau.

**Ràng buộc quan trọng nhất:** agent chỉ được phép **xóa trắng** ô duyệt, không bao giờ được ghi
"Đồng ý". Xóa là đóng cổng; ghi là tự cho phép mình. Chỉ hành động đầu là an toàn.

Cả payload và việc xóa trắng đi trong **một** lệnh cập nhật bản ghi, nên không có khoảnh khắc nào
bản ghi mang trạng thái mới mà vẫn còn phê duyệt cũ.

## Bài có ảnh: ô "Bài viết" mở bản xem trước có ảnh

`push` tải `article.md` lên Drive dưới dạng tệp Markdown. Tệp đó **không hiện ảnh**: ảnh trong bài trỏ
đường dẫn tương đối `images/<tên>.jpg` mà các tệp ảnh không đi theo. Lần đầu bài 002 có ảnh, người
duyệt mở bài trên Lark và không thấy ảnh nào, trong khi cổng duyệt bài chính là chỗ duyệt cả ảnh lẫn
chú thích.

Nay bài nào có thư mục `images/` thì `push` dựng thêm một **tài liệu Lark có ảnh**
(`scripts/lark/preview_doc.py`): nội dung bài, mỗi ảnh chèn ngay trên dòng chú thích của nó, dòng ghi
công đi sau chú thích, và Title / Meta / Slug ở đầu. Ô **Bài viết** trên Base trỏ vào tài liệu đó.
Lần push sau **ghi đè đúng tài liệu cũ** rồi chèn lại ảnh, nên link người duyệt đã mở vẫn dùng được;
mã tài liệu nằm ở `preview_token` trong `.lark.json`. Tệp `.md` vẫn được tải lên như cũ làm bản nguồn.

Dựng bản xem trước mà lỗi thì `push` **không dừng**: nó in cảnh báo và ô Bài viết trỏ về tệp `.md`.

## Sửa bài sau khi đã duyệt: quay về cổng bài

"Đã xong" và "Đã lên nháp WordPress" là trạng thái cuối **chỉ khi nội dung không đổi**. Push một bản
có nội dung khác (hoặc push với `--bump`) thì bài quay về **Chờ duyệt bài**, cụm duyệt bị xoá trắng,
và `gate` trả exit 1 cho tới khi người thật duyệt lại.

Trước 25/09/2026 hai trạng thái đó là cuối tuyệt đối. Chèn ảnh vào bài 002 sau khi đã lên bản nháp
rồi push thì bài vẫn ghi "Đã lên nháp WordPress · Bạn đọc bản nháp rồi đăng", `gate` trả **exit 0**
vì "không phải cổng", và `wp_draft.py` — vốn tin đúng exit 0 đó — sẵn sàng đưa bản **chưa ai duyệt**
lên WordPress. Đó là lỗ hổng của quy tắc 10, không phải lỗi hiển thị. `derive_state` nay nhận cờ
`changed` và kéo bài về cổng bài.

## Sửa schema rồi `--rebuild`: hai điều đã trả giá để biết

`--rebuild` **thuần thêm** — nó không xoá bảng, không xoá trường, không xoá option. Nhưng hai chỗ
từng làm hỏng dữ liệu thật, cả hai đã sửa trong `lark_setup.py` ngày 24/09/2026:

- **Thêm một option vào cột select sẽ xoá trắng mọi ô đang dùng option cũ**, nếu lệnh cập nhật không
  gửi kèm `id` của các option cũ. Lark coi danh sách không có id là toàn bộ option mới và cấp id
  khác. Lần đó chỉ thêm trạng thái "Đã lên nháp WordPress" mà ô Trạng thái của bài 001 mất giá trị
  "Chờ duyệt bài", và **không có thông báo lỗi nào** — chỉ lộ ra khi kênh theo dõi báo nhầm bài đó
  thành "từ khoá mới". `sync_select_options` nay gửi lại option cũ kèm id.
- **Sắp lại thứ tự cột sẽ bật hiện lại những cột người duyệt đã cố ý ẩn**, vì lệnh đặt
  `visible_fields` bằng toàn bộ danh sách của schema. `sync_view_order` nay chỉ sắp lại các cột
  đang hiện, cộng những cột vừa được tạo trong chính lượt rebuild đó.

Sau mỗi lần `--rebuild` trên Base có dữ liệu thật, hãy đọc lại một bản ghi và đối chiếu các cột
select — đó là loại mất mát im lặng nhất.

## Bốn bảng

| Bảng | Trường | Nội dung |
|---|---|---|
| **Điều phối** | 17 + 1 liên kết | Một bản ghi mỗi bài |
| **Bằng chứng** | 9 + 1 liên kết | Một bản ghi mỗi claim, có trích dẫn nguyên văn |
| **Nhật ký** | 7 | Mọi lần đồng bộ và duyệt |
| **Hướng dẫn** | 2 | Bản rút gọn của trang này, ngay trong Base |

Hai bảng đầu **nối với nhau bằng trường liên kết hai chiều**: ở Điều phối có trường **Claim**, bấm
vào là thấy toàn bộ claim của bài; ở Bằng chứng có trường **Bài** trỏ ngược lại. Trước đây phải tự
lọc theo Mã bài.

Ba trường **Kết quả duyệt**, **Người duyệt**, **Góp ý** là của bạn. Mọi trường còn lại do agent
quản lý và **sẽ bị ghi đè ở lần đồng bộ kế tiếp** — muốn đổi brief thì ghi vào Góp ý và từ chối,
đừng sửa trực tiếp.

Hai trường đọc nhanh:

- **Tóm tắt bằng chứng** — dạng `12 đã xác minh · 1 thiếu nguồn`. "Thiếu nguồn" là claim chưa tra ra
  nguồn; claim đó không được xuất hiện trong bài dưới dạng câu khẳng định. Bấm trường **Claim** để
  xem chi tiết.
- **Máy kiểm** — dạng `ĐẠT · 0 chặn · 3 cảnh báo`. Giải trình từng cảnh báo nằm trong
  `work/<slug>/qa-report.md`, **không** có trên Base: bảng Điều phối không còn trường cho báo cáo QA.

Ba trường **Slug**, **Tiêu đề**, **Mô tả meta** lấy thẳng từ front matter của `article.md`, không ai
phải gõ lại. Chúng để ở đây vì đó là những chuỗi sẽ lên Google, và là thứ hay bị sửa tay nhất trước
khi đăng. Bài chưa viết thì ba ô này rỗng; `push` không ghi đè giá trị cũ bằng chuỗi rỗng.

Mã bài là **số thứ tự thuần**: `001`, `002`, `003`. Khi cấp mã mới, `next_content_id` vẫn đọc được
dạng cũ `SEO-001` nên bản ghi từ trước không bị bỏ sót lúc đếm.

## Duyệt là tự chạy: ba lớp, và giới hạn thật của nó

Người duyệt tích ô trên Base rồi mong phần còn lại tự đi tiếp. Việc đó dựa trên **ba lớp**, cố ý
xếp chồng vì lớp nào cũng có lúc hỏng:

| Lớp | Cái gì chạy | Bắt được khi nào | Chậm nhất |
|---|---|---|---|
| 1. Kênh theo dõi | `lark_watch.py --interval 60` gắn qua công cụ Monitor | phiên đang mở và Monitor đang chạy | ~60 giây |
| 2. Hook kết lượt | `.claude/hooks/lark-stop.py` → `lark_watch.py --todo` | phiên đang mở, kể cả khi Monitor đã hết hạn | cuối lượt trả lời kế tiếp |
| 3. Hook mở phiên | `.claude/hooks/lark-start.py` → `--once` + `--todo` | mỗi lần mở Claude Code | lúc mở phiên sau |

**Vì sao cần lớp 2 và 3, không chỉ lớp 1.** Monitor tối đa 29 phút rồi phải gắn lại, và nó là công
cụ của agent nên hook không tự gắn được. Đã hai lần người duyệt tích ô xong mà không có gì chạy, vì
agent quên gắn. Lớp 2 lấp đúng chỗ đó.

**Vì sao `--todo` khác `--once`.** `--once` báo *thay đổi*, và nó cập nhật mốc trong
`work/.lark-watch.json` **ngay sau khi in**. Một dòng tin báo không ai đọc là mất luôn: lượt sau
không báo lại nữa. `--todo` thì không có ký ức — mỗi lần chạy nó đọc lại trạng thái sống trên Base
và trả lời "ngay bây giờ có việc gì đang chờ", nên bỏ qua bao nhiêu lần cũng không mất việc. Mã
thoát 3 nghĩa là có việc, và hook kết lượt dựa vào đúng mã đó.

**Hook kết lượt chặn lượt, và có ba chốt chống vòng lặp:** cờ `stop_hook_active` của Claude Code,
chữ ký việc ghi ở `work/.lark-stop.json` (cùng việc thì chỉ nhắc một lần), và luôn thoát 0 khi lỗi
để Lark hỏng không làm agent mắc kẹt.

**Giới hạn phải nói thẳng: không có lớp nào chạy khi không có phiên Claude Code nào mở.** Phiên
`@larksuite/cli` nằm trên chính máy này, nên một tác vụ đặt lịch trên máy chủ không đăng nhập được
vào Lark thay bạn; và bước sau khi duyệt là *viết nội dung*, việc chỉ agent làm được, không phải
một script. Vì vậy chuỗi này là "mở Claude lên là việc chạy ngay, không cần nhắc", chứ không phải
"chạy trong lúc bạn ngủ". Nếu cần thật thì phải dựng thêm một dịch vụ chạy nền trên máy, và đó là
một quyết định khác.

## Lệnh

```powershell
python scripts/lark/lark_sync.py push   work/<slug>     # đẩy lên, tính lại trạng thái
python scripts/lark/lark_sync.py gate   work/<slug>     # cổng hiện tại mở chưa (exit 0 = mở)
python scripts/lark/lark_sync.py pull   work/<slug>     # đọc trạng thái duyệt về máy
python scripts/lark/lark_sync.py status                 # xem toàn bộ pipeline
python scripts/lark/lark_sync.py remove work/<slug>     # gỡ một bản ghi
```

Năm lệnh này **không đổi** so với bản dùng Sheet — chỉ tầng bên dưới đổi.

`gate` không cần tham số chặng: nó tự biết bản ghi đang ở cổng nào.

`push --bump` tăng Bản và xóa cụm duyệt ngay cả khi nội dung không đổi. Hiếm khi cần, vì push
thường đã tự nhận ra nội dung đã đổi.

Thiết lập:

```powershell
python scripts/lark/lark_setup.py --title "..."   # tạo Base lần đầu
python scripts/lark/lark_setup.py --verify        # kiểm tra bảng và trường
python scripts/lark/lark_watch.py --todo          # việc đang chờ (exit 3 = có việc)
python scripts/lark/lark_setup.py --rebuild       # bổ sung bảng/trường còn thiếu
```

`--rebuild` từ chối chạy khi bảng Điều phối còn bản ghi, để không âm thầm làm mất bản ghi đang chạy.

## Tiếng Việt trên Base, khóa nội bộ trong code

Tên trường trên Base là nhãn tiếng Việt; code làm việc bằng khóa ASCII ổn định (`content_id`,
`state`, `review`...). `read_table()` dịch nhãn → khóa khi đọc, `build_fields()` dịch ngược khi ghi.

Muốn đổi cách gọi một trường hay một trạng thái, sửa duy nhất `scripts/lark/schema.py` rồi chạy
`lark_setup.py --rebuild`. Không đụng tới logic.

Phần đọc ngược chấp nhận **cả** nhãn tiếng Việt lẫn giá trị gốc tiếng Anh, nên gõ tay kiểu nào
cũng hiểu.

## Outline và bài nằm ở đâu

Không nhét được 1500 chữ vào một ô. `push` tải bốn tài liệu lên **Drive** dưới dạng Markdown và ghi
đường dẫn vào bảng Điều phối: **Brief** (dựng từ `brief.yaml`, đọc dễ hơn nhiều so với 18 ô rời rạc),
**Outline**, **Bài viết**. Báo cáo QA **không** lên Drive — bảng Điều phối không còn trường cho nó.

Lần push sau ghi đè đúng tệp cũ nên đường dẫn không đổi — link bạn đã mở vẫn dùng được. Đây là lý do
tài liệu **không** để dạng đính kèm của Base: đính kèm sinh token mới mỗi lần ghi, làm chết link cũ.

### Thư mục trên Drive

Tài liệu nằm trong thư mục **Content Blog AI**, khai ở `config.json` qua `doc_folder_token`. Cách xếp
bên trong do `doc_layout` quyết định:

| `doc_layout` | Cách xếp | Quyền cần |
|---|---|---|
| `type` (đang dùng) | Bốn thư mục theo giai đoạn, khai trong `doc_folders`: Brief, Outline, Content Draft, QA | Không cần thêm |
| `article` | Mỗi bài một thư mục chứa đủ bốn tài liệu | `space:folder:create` |

Giai đoạn nào chưa khai thư mục trong `doc_folders` thì tài liệu của giai đoạn đó rơi về thư mục gốc —
hiện là trường hợp của báo cáo QA, vì chưa có thư mục dành cho nó.

Đổi cách xếp không cần chạy lệnh riêng: sửa `doc_layout` trong `config.json` rồi `push` lại, `place_docs`
sẽ tự chuyển tệp sang chỗ mới. `.lark.json` ghi nhớ từng tệp đang nằm ở thư mục nào (`placed`) nên push
lại nhiều lần không gọi lệnh chuyển thừa.

Chuyển thư mục **không đổi `file_token`**, nên mọi đường dẫn đã ghi trong bảng Điều phối vẫn mở được.
Còn `markdown +overwrite` thì ngược lại: nó ghi đè nội dung nhưng **không** đổi thư mục, nên tệp cũ
luôn phải được chuyển bằng một lệnh riêng.

## Báo khi có kết quả duyệt

Hai kênh, phục vụ hai người đọc khác nhau:

| Kênh | Báo cho ai | Sống khi nào |
|---|---|---|
| **Base Workflow** "Báo khi có kết quả duyệt" | Bạn, qua nhóm Lark **Duyệt content SEO** | 24/7 trên máy chủ Lark, không cần máy bạn bật |
| **`lark_watch.py`** | Agent, để nó chạy tiếp | Chỉ khi có phiên Claude Code đang mở |

```powershell
python scripts/lark/lark_workflow.py --create   # tạo (ở trạng thái tắt)
python scripts/lark/lark_workflow.py --show     # đọc lại định nghĩa
python scripts/lark/lark_workflow.py --enable

python -u scripts/lark/lark_watch.py            # theo dõi, tự dừng sau 29 phút
python -u scripts/lark/lark_watch.py --once     # kiểm một lượt
```

### Mở Claude là tự chạy

Hook `SessionStart` ở `.claude/settings.json` gọi `.claude/hooks/lark-start.py` mỗi khi phiên bắt
đầu, được resume, hoặc sau `/clear`. Hook làm đúng hai việc:

1. Chạy `lark_watch.py --once` để **báo những gì đã đổi trong lúc không có phiên nào mở**. File mốc
   `work/.lark-watch.json` sống lâu hơn tiến trình, nên mở Claude lên là biết ngay ai đã duyệt hay
   từ chối cái gì — kể cả khi việc đó xảy ra đêm qua.
2. Nhắc agent gắn kênh theo dõi. `Monitor` là công cụ của agent nên hook không tự gắn được, nhưng
   dòng nhắc đó nằm trong context nên agent gắn ngay ở lượt đầu tiên.

Hook **luôn thoát mã 0**: Lark hỏng không được làm hỏng cả phiên làm việc.

### Vì sao hai kênh mà không phải một

Đường gọn nhất lẽ ra là: Base Workflow nhắn vào nhóm có bot, bot đẩy event về máy, agent nghe
`im.message.receive_v1`. **Đường đó không đi được**, và lý do đáng ghi lại:

- Lark **không có event nào cho bản ghi Base thay đổi**. Đã tra hết 26 EventKey của `lark-cli`.
- Bot chỉ nhận được tin nhóm khi app khai `im:message.group_msg` (mọi tin trong nhóm) hoặc
  `im:message.group_at_msg:readonly` (chỉ tin @nhắc bot). Đã thử thật: người gõ `test` vào nhóm,
  consumer chạy tốt nhưng `RECEIVED = 0`.
- Thẻ tin của trợ lý Base **không @nhắc bot được**: `content` của `LarkMessageAction` chỉ nhận
  `text` và `ref`, không có kiểu mention.

Nên phần đánh thức agent phải là đọc định kỳ. Một lượt đọc là **một** lời gọi API cho tất cả bài.

### Hai điều `lark_watch.py` không làm

1. **Không gọi `pull`.** `pull` ghi một dòng vào bảng Nhật ký mỗi lần chạy; đọc mỗi 60 giây sẽ đổ
   1.440 dòng rác một ngày. Watcher chỉ đọc bảng, không ghi gì lên Lark.
2. **Không tự `push`.** `derive_state` đẩy `Đang lên outline → Chờ duyệt outline` **kể cả khi chưa
   có outline**, và cú push đó tiêu thụ luôn phê duyệt — xóa mất thứ bạn vừa bấm. Phản ứng đúng khi
   cổng mở là *chạy skill trước, skill push sau*.

Tin báo chỉ là chuông cửa. Chỉ `gate` trả về exit 0 mới là đã duyệt.

### Chốt chống vòng lặp

Trigger dùng `operator: containsAny` với đúng hai lựa chọn **Đồng ý** và **Từ chối**. Khi agent
**xóa trắng** ô duyệt sau lúc tiêu thụ phê duyệt, ô rỗng không khớp lựa chọn nào nên workflow không
kích hoạt lại. Sai chỗ này thì mỗi lần `push` agent tự bắn thông báo cho chính mình.

Ghi chú kỹ thuật cho lần sửa sau: trường select **không nhận** `value_type: "text"`, và với select
một lựa chọn thì `operator: "is"` **chỉ nhận đúng một** option — muốn khớp nhiều phải dùng
`containsAny`.

## Trạng thái đồng bộ cục bộ

`work/<slug>/.lark.json` giữ `content_id`, `record_id`, checksum nội dung và token các tệp. Đừng xóa;
mất nó, lần push sau sẽ cấp mã bài mới và tạo bản ghi trùng. Lỡ xóa thì `remove --content-id 00X`
rồi push lại.

`record_id` của Base là **bất biến**: bạn sắp xếp, lọc, ẩn hay xóa bản ghi khác thoải mái mà đồng bộ
không lung lay. Bản dùng Sheet trước đây định vị theo số hàng nên mong manh hơn nhiều.

## Xác thực

Agent gọi `@larksuite/cli`; CLI tự giữ phiên đăng nhập. **Không có secret nào trong project này.**
`config.json` chỉ chứa `base_url`, `app_token`, id các bảng và đường dẫn tới node/CLI.

Base cần **scope riêng**, không dùng chung với Sheet. Thiếu quyền thì mọi lệnh sẽ báo
`missing_scope`. Cấp một lần:

```powershell
lark-cli auth login --domain base
```

## Giới hạn

- Base này **không publish**. Nó dừng ở gói bàn giao.
- Máy kiểm `ĐẠT` chỉ nghĩa là không còn lỗi cơ học. Độ chính xác và tính hữu ích vẫn phải người kiểm.
- Cổng duyệt là **quy ước làm việc, không phải cơ chế bảo mật**. Nó ngăn agent tự cho phép mình;
  nó không ngăn được người tự chọn "Đồng ý" mà chưa đọc.
