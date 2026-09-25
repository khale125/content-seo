# Schema wiki tri thức

Tài liệu này quy định **cách bảo trì wiki**. Đọc nó trước khi chạm vào bất kỳ file nào trong `wiki/`.
Nền tảng khái niệm nằm ở `docs/11-wiki-tri-thuc.md`; file này là phần quy ước máy kiểm được.

## Luật số 1 — wiki không phải nguồn

Bài viết **luôn trích dẫn `source_url` gốc**, không bao giờ trích dẫn trang wiki. Lý do đầy đủ nằm ở
`docs/11-wiki-tri-thuc.md` và ở hard rule 12 trong `CLAUDE.md`.

Phần `wiki_lint.py` thực thi:

- Claim `VERIFIED` phải có `source_url` HTTPS, `supporting_quote` ≥ 25 ký tự và `retrieved_date`.
- Trang `het-hieu-luc` mà `used_in` còn bài đang dùng là `BLOCK`.
- `evidence-ledger.csv` có `wiki_ref` trỏ tới trang không tồn tại hoặc đã hết hiệu lực là `BLOCK`.

## Ba lớp

| Lớp | Là gì | Ai sở hữu |
|---|---|---|
| Nguồn gốc | URL thật trên `vanban.chinhphu.vn`, `moc.gov.vn`, `sbv.gov.vn`, `nso.gov.vn`… | Không ai — bất biến, nằm ngoài repo |
| Wiki (`wiki/`) | Trang markdown do agent viết và bảo trì | Agent sở hữu hoàn toàn |
| Bài viết (`work/<slug>/`) | Brief, outline, ledger, bài | Quy trình sẵn có, có ba cổng duyệt |

Dự án **không lưu bản chụp nguồn**. Trang wiki giữ URL + trích dẫn nguyên văn + ngày lấy về.
Đổi lại: phải mở lại URL khi rà soát, vì repo không tự biết nguồn đã đổi hay chết.

## Cấu trúc thư mục

```
wiki/
├── schema.md          file này
├── index.md           mục lục — do wiki_index.py dựng, đừng sửa tay
├── log.md             nhật ký append-only
├── van-ban/           một trang cho mỗi văn bản pháp luật
├── khai-niem/         khái niệm dùng lại nhiều bài: tiền sử dụng đất, hạn mức giao đất ở…
├── dia-ban/           tỉnh/thành: bảng giá đất, hạn mức, đầu mối nộp hồ sơ
├── so-lieu/           chuỗi số liệu theo kỳ: lãi suất điều hành, CPI, công bố quý
└── tong-hop/          trang tổng hợp: dòng thời gian hiệu lực, so sánh, giải đáp
```

Tên file = `<id>.md`, và `id` phải **trùng tên file**, viết kebab không dấu.
Thư mục phải **khớp trường `type`**. Cả hai đều bị `wiki_lint.py` chặn ở mức `BLOCK`.

## Front matter

```yaml
---
id: nghi-dinh-50-2026          # bắt buộc, kebab không dấu, trùng tên file
type: van-ban                  # bắt buộc: van-ban | khai-niem | dia-ban | so-lieu | tong-hop
title: "Nghị định 50/2026/NĐ-CP"   # bắt buộc, hiển thị trong mục lục
status: con-hieu-luc           # bắt buộc, xem bảng dưới
updated: 2026-09-16            # bắt buộc, ngày kiểm lại gần nhất
effective_from: 2026-01-31     # tùy chọn, ngày có hiệu lực
review_after: 2027-03-16       # tùy chọn, hạn rà soát
superseded_by: ""              # id trang thay thế, bắt buộc khi status = het-hieu-luc
supersedes: []                 # id các trang mà trang này thay thế
related: [tien-su-dung-dat]    # id trang liên quan
used_in: [chi-phi-chuyen-dat-nong-nghiep-len-tho-cu-2026]   # slug bài đang dùng
---
```

### Giá trị của `status`

| Giá trị | Nghĩa |
|---|---|
| `con-hieu-luc` | Đã kiểm tại ngày `updated`, còn áp dụng |
| `het-hieu-luc` | Đã bị thay thế. **Phải** ghi `superseded_by` |
| `sua-doi` | Còn hiệu lực nhưng đã bị sửa đổi, bổ sung một phần |
| `chua-ro` | Chưa xác minh được. Dùng cho bài là rủi ro — `wiki_lint` cảnh báo |
| `khong-ap-dung` | Trang khái niệm, không có hiệu lực pháp lý |

`used_in` là **chỉ mục ngược** quan trọng nhất của wiki: nó trả lời câu hỏi *"văn bản này vừa hết
hiệu lực, những bài nào đang dẫn nó?"* — đúng thứ `docs/09-phat-hien-chu-de.md` gọi là giá trị lớn
nhất của radar. Trang `het-hieu-luc` mà `used_in` còn bài là `BLOCK`.

## Khối claim

Claim là đơn vị mang bằng chứng. Tên trường **trùng khớp cột của `evidence-ledger.csv`**, để một
claim chuyển thẳng thành một dòng ledger mà không phải dịch tên.

```markdown
### C: Trong hạn mức giao đất ở, thu 30% phần chênh lệch
- source_url: https://vanban.chinhphu.vn/?docid=216861
- source_type: LAW
- published_date: 2026-01-31
- effective_date: 2026-01-31
- retrieved_date: 2026-09-15
- supporting_quote: "chép nguyên văn đoạn trong nguồn chứng minh claim này"
- status: VERIFIED
- note: ghi chú tùy chọn
```

Quy tắc:

- Tiêu đề claim bắt đầu bằng `### C:` và **viết đúng câu sẽ dùng trong bài**, không viết tóm tắt.
- `status: VERIFIED` bắt buộc có `source_url` HTTPS, `supporting_quote` ≥ 25 ký tự, `retrieved_date`.
- `status: PARTIAL` khi nguồn đỡ được một phần — ghi rõ phần nào còn nợ vào `note`.
- `status: GAP` khi chưa tra được. Được phép tồn tại trên wiki (khác với trong bài), nhưng
  `wiki_lint` luôn cảnh báo để nó không nằm im mãi.
- `FACT` rủi ro cao (pháp lý, thuế, tín dụng) phải có `source_type` thuộc `LAW` / `GOV` / `STATS`.

## Liên kết chéo

Dùng cú pháp Obsidian `[[id]]` trong thân trang, và `related:` trong front matter cho quan hệ chính.
Mọi đích đến phải là `id` có thật — trỏ sai là `BLOCK`.

Trang không ai trỏ tới và cũng không bài nào dùng là **trang mồ côi** → `WARN`. Tri thức không nối
vào đâu thì không khác gì chưa có.

## Nhật ký `log.md`

Append-only, dòng mới thêm **xuống cuối**. Mỗi dòng:

```
- YYYY-MM-DD · ACTION · <page-id hoặc —> · mô tả ngắn
```

`ACTION` thuộc: `INGEST` (thêm nguồn mới), `UPDATE` (sửa trang đã có), `QUERY` (câu hỏi đã trả lời
và đã lưu lại), `LINT` (chạy rà soát), `RETIRE` (đánh dấu hết hiệu lực).

Log là thứ duy nhất cho biết wiki đang được bảo trì hay đã bị bỏ hoang.

## Ba thao tác

### `ingest` — thêm nguồn mới

1. Mở thật URL, lấy ngày công bố và trích dẫn nguyên văn.
2. Tìm trang wiki đã có cho văn bản/khái niệm đó. **Sửa trang có sẵn trước khi tạo trang mới** —
   trùng lặp trong wiki nguy hiểm hơn trong bài, vì nó sinh ra hai phiên bản sự thật.
3. Thêm hoặc cập nhật claim. Cập nhật `updated`.
4. Nếu văn bản mới thay thế văn bản cũ: đặt `status: het-hieu-luc` và `superseded_by` cho trang cũ,
   `supersedes` cho trang mới. **Rồi chạy `wiki_lint.py`** — nó sẽ chỉ ra ngay những bài đang dẫn
   văn bản vừa hết hiệu lực.
5. Cập nhật `related` hai chiều, chạy `wiki_index.py build`, ghi một dòng `log.md`.

### `query` — tra cứu trước khi nghiên cứu

Trước khi đi tìm nguồn cho một claim mới, **tra wiki trước**. Có sẵn claim `VERIFIED` thì chép vào
`evidence-ledger.csv` và điền `wiki_ref` bằng `id` của trang. Đây là chỗ wiki trả lại thời gian.

Vẫn phải mở lại `source_url` nếu `updated` đã cũ hơn ngưỡng ở bảng dưới — wiki nói nguồn từng đúng,
không nói nguồn hiện còn đúng.

### `lint` — rà soát định kỳ

```powershell
python scripts/wiki_lint.py
python scripts/wiki_index.py check
```

Chạy hằng tháng, và **bắt buộc chạy sau mỗi lần radar phát hiện văn bản mới**.

## Ngưỡng độ tuổi

| Loại trang | Cũ hơn thì cảnh báo |
|---|---|
| `so-lieu` | 180 ngày |
| `dia-ban` | 270 ngày |
| còn lại | 400 ngày |

Số liệu cũ nhanh hơn văn bản pháp luật; bảng giá đất và hạn mức đổi theo nhiệm kỳ địa phương.

## Không thuộc phạm vi

Xem mục "Phạm vi" trong `docs/11-wiki-tri-thuc.md`.
