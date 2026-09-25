# Nơi làm việc cho từng bài

Mỗi bài một thư mục `work/<slug>/`.

**Đừng copy cả `templates/` vào đây.** Mỗi giai đoạn chỉ tạo file của giai đoạn đó:

| Giai đoạn | File được tạo |
|---|---|
| Radar (`radar.py add`) | `brief.yaml`, `serp-notes.md`, `evidence-ledger.csv` (chỉ header) |
| Outline (`seo-outline-bds`) | thêm `competitors.json`, `outline.md` |
| Viết (`seo-writer-bds`) | thêm `article.md`, và `image-manifest.csv` nếu bài có ảnh |
| QA (`seo-qa-bds`) | thêm `qa-report.md`, `qa-report.json` |

Lý do: `lark_sync.py` coi một `outline.md` "thực chất" là outline đã viết xong. Copy sẵn file mẫu
chưa điền sẽ làm bản ghi nhảy qua cổng duyệt chủ đề. Tương tự, `qa-report.md` mẫu chưa điền vẫn
được đẩy lên Drive như một báo cáo QA thật.

`.lark.json` do `lark_sync.py` tự quản lý, không sửa tay và không thuộc gói bàn giao.

Gói bàn giao đầy đủ: `docs/07-qa-va-ban-giao.md`.
