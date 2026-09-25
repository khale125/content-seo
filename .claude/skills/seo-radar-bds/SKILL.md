---
name: seo-radar-bds
description: "Tự phát hiện chủ đề bất động sản từ nguồn chính thống: quét văn bản pháp luật mới, công bố của Bộ Xây dựng, lãi suất Ngân hàng Nhà nước, số liệu Cục Thống kê; đối chiếu với nội dung đã có trên blog để tìm bài lỗi thời cần cập nhật; đề xuất ứng viên kèm nguồn đã xác minh rồi trình danh sách gợi ý để người dùng chọn từ khóa (không đẩy lên Lark). Dùng khi người dùng nói: tìm chủ đề, đề xuất đề tài, có gì mới, quét nguồn, radar, chủ đề tuần này, hoặc không biết viết gì."
---

# Radar phát hiện chủ đề

> **Skill này đã ra khỏi quy trình chính.** Quy trình hiện tại bắt đầu bằng việc người dùng đưa
> **từ khóa chính kèm volume search**, nên không còn cổng duyệt chủ đề và không còn bước radar bắt
> buộc. Chỉ dùng skill này khi người dùng **hỏi thẳng** rằng có chủ đề gì đáng viết.

Đầu ra là **danh sách gợi ý để người dùng chọn từ khóa**, mỗi ứng viên kèm nguồn đã mở thật.
**Không đẩy lên Lark, không tạo bản ghi chờ duyệt** — trạng thái `Chờ duyệt chủ đề` không còn tồn
tại. Người dùng chọn xong thì đưa từ khóa kèm volume, rồi chạy `seo-outline-bds` như bình thường.

**Không viết outline, không viết bài.** Dừng sau khi trình danh sách gợi ý.

## Đọc trước

1. `CLAUDE.md` (hard rules)
2. `docs/09-phat-hien-chu-de.md`
3. `docs/01-intent-va-keyword.md` (phần điều kiện chọn đề tài và chống trùng)
4. `docs/04-chinh-sach-nguon.md` (thứ tự ưu tiên nguồn)
5. `docs/11-wiki-tri-thuc.md` + `wiki/schema.md` (kho tri thức dùng lại giữa các bài)

## Bước 1 — Xem danh mục nguồn

```powershell
python scripts/radar/radar.py sources
```

Danh mục chỉ chứa URL **đã mở được thật**.
Nguồn địa phương không ghi sẵn URL — phải tự tìm và mở trước khi dùng.

## Bước 2 — Quét

Quét theo thứ tự ưu tiên nguồn, không quét theo thứ tự tiện tay:

1. **Văn bản pháp luật mới** (`vanban.chinhphu.vn`) — nghị định, thông tư về đất đai, nhà ở,
   kinh doanh bất động sản. Đặc biệt chú ý văn bản **sửa đổi hoặc thay thế** cái mà bài cũ đang dẫn.
2. **Bộ Xây dựng** (`moc.gov.vn`) — công bố quý về nhà ở và thị trường, chỉ đạo về nhà ở xã hội.
3. **Ngân hàng Nhà nước** (`sbv.gov.vn`) — lãi suất điều hành, tín dụng bất động sản.
4. **Cục Thống kê** (`nso.gov.vn`) — CPI nhóm nhà ở và vật liệu xây dựng.
5. **Báo chí** — chỉ để phát hiện sự kiện. Bắt buộc truy ngược về văn bản gốc.

Mặc định quét tin trong **30 ngày**; nới rộng khi tìm bài cập nhật (văn bản cũ hơn vẫn làm bài cũ
lỗi thời). Với mỗi ứng viên, **mở thật trang nguồn** và lấy được: ngày công bố, số hiệu văn bản,
và ít nhất một câu trích dẫn nguyên văn. Không lấy được ba thứ đó thì bỏ ứng viên.

## Bước 3 — Đối chiếu nội dung đã có

Đây là chỗ radar tạo ra giá trị lớn nhất, đừng bỏ qua.

```
site:muaban.net/blog <truy vấn liên quan>
```

Với mỗi văn bản mới, tự hỏi: **bài nào trên blog đang dẫn quy định cũ?** Một bài đang xếp hạng tốt
nhưng dẫn căn cứ đã hết hiệu lực vừa là rủi ro vừa là cơ hội — `UPDATE` gần như luôn đáng làm hơn
`CREATE`, vì nó giữ được thứ hạng và sửa được thông tin sai.

Chốt `url_decision` cho từng ứng viên: `CREATE` / `UPDATE` / `MERGE` / `SKIP`, kèm lý do và các
URL hiện có.

## Bước 3b — Đối chiếu với wiki tri thức

Bước 3 làm bằng mắt. Bước này làm bằng máy, và nó bắt được thứ mắt bỏ sót.

Mở `wiki/index.md`, tìm trang của văn bản mà ứng viên đang nói tới.

**Nếu văn bản mới thay thế một văn bản đã có trang wiki:**

1. Ở trang cũ, đặt `status: het-hieu-luc` và `superseded_by: <id trang mới>`.
2. Tạo trang mới cho văn bản mới (khung ở `templates/wiki-page.md`), điền `supersedes: [<id trang cũ>]`.
3. Chạy:

```powershell
python scripts/wiki_lint.py
```

`wiki_lint` đọc trường `used_in` của trang cũ và **gọi tên từng bài đang dẫn văn bản vừa hết hiệu
lực** ở mức `BLOCK`, kèm mọi `evidence-ledger.csv` có `wiki_ref` trỏ tới nó. Đây chính là thứ
`docs/09-phat-hien-chu-de.md` gọi là giá trị lớn nhất của radar — trước đây phải rà bằng mắt.

Mỗi bài lộ ra ở đây là một ứng viên `UPDATE` đã có sẵn bằng chứng vì sao đáng làm. Đưa thẳng vào
danh sách ứng viên ở bước 6, với `gap_type: loi-thoi` và `gap_evidence` dẫn id trang wiki.

**Nếu văn bản chưa có trang wiki:** chưa cần tạo ngay. Trang wiki được dựng ở bước evidence ledger
của skill `seo-outline-bds`, sau khi chủ đề đã được duyệt — tránh dựng tri thức cho chủ đề bị loại.

Ghi một dòng vào `wiki/log.md` cho mỗi thay đổi:

```
- 2026-09-16 · RETIRE · nghi-dinh-cu · bị thay thế bởi nghi-dinh-moi, 2 bài cần UPDATE
```

## Bước 4 — Sàng

Giữ lại ứng viên thỏa **tất cả**:

- Có thông tin mới và **ngày rõ ràng**.
- Nguồn thuộc `LAW` / `GOV` / `STATS`, hoặc là `SIGNAL` nhưng đã xác định được văn bản gốc cần truy.
- Intent cụ thể, hình dung được người đọc là ai và họ quyết định được gì sau bài.
- Có góc riêng ngoài việc tóm tắt lại văn bản.
- Muaban.net có lý do chính đáng để nói về nó, và có đường dẫn hợp lý cho người đọc sau khi đọc xong.

Loại bỏ khi: chỉ là tin tức không đổi hành vi người đọc; chưa có văn bản chính thức (mới là dự thảo,
đề xuất, phát biểu); hoặc trùng intent với bài đang có mà không có gì mới để bổ sung.

**Không có ứng viên nào đạt thì báo cáo là không có.** Đề xuất một chủ đề yếu để lấp chỗ trống
chính là đường dẫn tới scaled content abuse.

## Bước 5 — Chống trùng

```powershell
python scripts/radar/radar.py check --url "<url nguồn>" --event "<mô tả sự kiện>"
```

Exit 0 là chưa từng đề xuất. Lệnh cũng cảnh báo khi gần trùng với đề xuất cũ (cùng sự kiện,
khác URL).

## Bước 6 — Ghi nhận và đẩy lên Lark

Viết ứng viên ra file JSON (mảng các object), mỗi object gồm tối thiểu:

```json
{
  "slug": "chu-thuong-khong-dau",
  "primary_query": "truy vấn người dùng thật sự gõ",
  "intent": "informational-thu-tuc",
  "event": "sự kiện là gì, nói đủ để phân biệt với sự kiện khác",
  "source_url": "https://... (đã mở được thật)",
  "source_tier": "LAW | GOV | STATS | SIGNAL",
  "published_date": "YYYY-MM-DD",
  "primary_source_todo": "bắt buộc khi tier = SIGNAL",
  "why_now": "...", "reader": "...", "reader_task": "...",
  "gap_type": "loi-thoi | thieu-cu-the | sai-format | thieu-nhom-nguoi-doc | thieu-du-lieu-dia-phuong",
  "gap_evidence": "bằng chứng cụ thể, dẫn URL",
  "unique_angle": "thứ bài này có mà top hiện tại không có",
  "url_decision": "CREATE | UPDATE | MERGE | SKIP",
  "existing_urls": ["..."],
  "entities": ["..."], "questions_to_answer": ["..."],
  "ymyl_areas": ["..."], "cta": "..."
}
```

```powershell
python scripts/radar/radar.py add <file.json>
python scripts/lark/lark_sync.py push work/<slug>
```

`add` **từ chối** ứng viên thiếu nguồn HTTPS, thiếu ngày công bố, ngày ở tương lai, hoặc nguồn
báo chí mà chưa ghi văn bản gốc cần truy. Đây là chốt chặn chống bịa đặt — đừng tìm cách đi vòng;
nếu bị từ chối thì quay lại xác minh nguồn.

`add` dựng `work/<slug>/` với `brief.yaml`, `serp-notes.md` và ledger rỗng. Nó **không** tạo
`outline.md` — outline là việc của skill sau, và một file mẫu chưa điền sẽ bị tính nhầm là
outline đã viết xong.

## Bước 7 — Báo cáo và dừng

Với mỗi ứng viên, nói ngắn gọn: sự kiện gì, nguồn nào + ngày, vì sao đáng viết, `url_decision`
và lý do, rủi ro YMYL đã thấy trước. Xếp theo mức đáng làm, nêu rõ tiêu chí xếp.

Nêu cả **ứng viên đã loại và lý do** — điều đó cho người duyệt biết radar đã quét gì.

**Dừng tại đây.** Người thật duyệt chủ đề trên Lark (`Kết quả duyệt = Đồng ý` + `Người duyệt`).
Chỉ sau đó mới chạy `seo-outline-bds` cho ứng viên được duyệt.

Sau khi một chủ đề có kết cục, ghi lại để radar không đề xuất lại:

```powershell
python scripts/radar/radar.py close <slug> VIET|BO_QUA|GOP --note "..."
```

## Nhịp chạy gợi ý

| Nguồn | Nhịp |
|---|---|
| Văn bản pháp luật, Bộ Xây dựng, Ngân hàng Nhà nước | hằng tuần |
| Cục Thống kê (CPI) | hằng tháng, khoảng ngày 6 |
| Công bố quý của Bộ Xây dựng | 3–4 tuần sau khi kết thúc quý |
| Rà bài cũ bị văn bản mới làm lỗi thời | hằng tháng |

Đừng chạy radar dày hơn năng lực viết. Hàng đợi ứng viên dài mà không ai viết chỉ tạo cảm giác
bận rộn.
