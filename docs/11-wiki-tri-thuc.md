# Wiki tri thức — để bằng chứng không chết theo từng bài

## Vấn đề

`evidence-ledger.csv` sống và chết trong một thư mục `work/<slug>/`. Bài sau không thừa hưởng được
gì từ bài trước. Mỗi lần viết về đất đai là một lần đi tra lại Nghị định, một lần mở lại cùng những
URL đó, một lần chép lại cùng những đoạn nguyên văn đó.

Với dự án lấy **không bịa đặt** làm ràng buộc số một, bằng chứng đã xác minh là tài sản đắt nhất
mình có. Hiện nó đang bị vứt đi sau mỗi bài.

Nút thắt của quy trình không nằm ở khâu viết. Nó nằm ở khâu ghim được nguyên văn điều khoản.

## Ý tưởng

Mẫu này lấy từ **LLM Wiki** của Andrej Karpathy
(https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), điều chỉnh cho ràng buộc của
dự án này.

Thay vì mỗi lần hỏi lại đi truy xuất từ nguồn thô, agent **dựng và bảo trì một wiki bền lâu** nằm
giữa nguồn gốc và bài viết. Thêm một nguồn mới không phải là lập chỉ mục nó, mà là đọc, rút thông
tin, rồi *hòa* nó vào wiki đang có: cập nhật trang thực thể, sửa lại tóm tắt, ghi nhận mâu thuẫn.

Điểm mấu chốt: **wiki là tài sản tích lũy**. Nó giàu lên sau mỗi bài, thay vì bắt đầu lại từ đầu.

Người lo phần tìm nguồn, đặt câu hỏi, quyết định. Agent lo phần tóm tắt, đối chiếu, xếp chỗ và
**sổ sách** — chính phần sổ sách mới là thứ làm con người bỏ cuộc với mọi wiki cá nhân, vì chi phí
bảo trì tăng nhanh hơn giá trị. Agent không chán và không quên cập nhật chéo 15 trang trong một lượt.

## Luật số 1 — wiki không phải nguồn

Đây là chỗ mẫu gốc phải được sửa cho dự án này, và là ràng buộc quan trọng nhất của cả tài liệu.

Wiki là nội dung **do máy sinh ra**. Nó không phải văn bản pháp luật, không phải công bố của cơ quan
nhà nước, không phải số liệu thống kê.

- Bài viết **luôn trích dẫn `source_url` gốc**, không bao giờ trích dẫn trang wiki.
- Wiki là chỗ **tìm lại** bằng chứng, không phải chỗ **thay thế** bằng chứng.
- Mỗi claim trên wiki bắt buộc mang theo `source_url`, `supporting_quote` nguyên văn và
  `retrieved_date`.

Nếu để agent trích dẫn wiki, zero-fabrication biến thành fabrication có vẻ ngoài đáng tin —
tệ hơn hẳn việc không có wiki. `wiki_lint.py` chặn ở mức `BLOCK`.

## Ba lớp

Nguồn gốc (URL thật, bất biến, nằm ngoài repo) → wiki (`wiki/`, agent sở hữu hoàn toàn) →
bài viết (`work/<slug>/`, có ba cổng duyệt trên Lark).

Bảng đầy đủ và ranh giới sở hữu của từng lớp nằm ở `wiki/schema.md`.

## Ba thao tác

- **`ingest`** — thêm nguồn mới: sửa trang đã có trước khi tạo trang mới, đánh dấu văn bản bị thay thế.
- **`query`** — tra wiki **trước** khi đi tìm nguồn; điền `wiki_ref` vào ledger.
- **`lint`** — `wiki_lint.py` + `wiki_index.py check`, chạy hằng tháng và sau mỗi lần radar phát hiện
  văn bản mới.

Từng bước cụ thể nằm ở `wiki/schema.md`. Đừng chép lại ở đây — một quy trình chỉ nên có một bản.

## Vì sao việc này đáng làm với dự án này

**Một.** Bằng chứng dùng lại được. Nghị định về đất đai xuất hiện trong nhiều bài; ghim một lần,
dùng nhiều lần, và mọi bài dùng chung một cách hiểu.

**Hai — quan trọng nhất.** Trường `used_in` là chỉ mục ngược: nó trả lời thẳng câu hỏi *"văn bản
này vừa hết hiệu lực, những bài nào đang dẫn nó?"* Đây đúng là thứ `docs/09-phat-hien-chu-de.md`
gọi là giá trị lớn nhất của radar — tìm bài cũ đang dẫn quy định đã hết hiệu lực. Trước đây phải
rà bằng mắt; giờ `wiki_lint.py` chặn ở mức `BLOCK`, và `evidence-ledger.csv` nào có `wiki_ref`
trỏ tới trang đã hết hiệu lực cũng bị chặn.

**Ba.** Mâu thuẫn lộ ra sớm. Hai bài hiểu khác nhau về cùng một điều khoản sẽ va nhau trên wiki
trước khi kịp lên bài.

## Phạm vi

- **Không đẩy wiki lên Lark.** Ba cổng duyệt là để duyệt bài, không phải duyệt tri thức nền.
- **Không lưu bản chụp nguồn** trong repo.
- **Không dùng wiki làm nơi nháp bài.**
- Wiki **không** thay thế `evidence-ledger.csv`. Ledger vẫn là hồ sơ bằng chứng của từng bài và vẫn
  là thứ `evidence_check.py` đọc. Wiki chỉ làm cho việc điền ledger nhanh hơn và nhất quán hơn.

## Quy ước chi tiết

Nằm ở `wiki/schema.md`: cấu trúc thư mục, front matter, khối claim, liên kết chéo, định dạng
`log.md`, ngưỡng độ tuổi. Khung trang mới nằm ở `templates/wiki-page.md`.

## Kiểm ngược bộ kiểm

Như hai fixture bài viết, wiki cũng có fixture ngược chiều:

```powershell
python scripts/wiki_lint.py --wiki examples/fixture-wiki-dat   --work work   # kỳ vọng: 0 BLOCK
python scripts/wiki_lint.py --wiki examples/fixture-wiki-hong  --work work   # kỳ vọng: 6 BLOCK
```

Sau mỗi lần sửa ngưỡng trong `scripts/wiki_common.py`, chạy lại cả hai.
