# Nhật ký wiki

Append-only. Dòng mới thêm **xuống cuối**, không sửa dòng cũ, không sắp xếp lại.

Định dạng — `wiki_lint.py` kiểm từng dòng:

```
- YYYY-MM-DD · ACTION · <page-id hoặc —> · mô tả ngắn
```

`ACTION`: `INGEST` (thêm nguồn mới) · `UPDATE` (sửa trang đã có) · `QUERY` (câu hỏi đã trả lời và
lưu lại) · `LINT` (chạy rà soát) · `RETIRE` (đánh dấu hết hiệu lực).

Log là thứ duy nhất cho biết wiki đang được bảo trì hay đã bị bỏ hoang. Xem `wiki/schema.md`.

## Nhật ký

