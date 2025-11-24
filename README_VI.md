
# Tài liệu hướng dẫn cho `main.py`

## 1. Tổng quan

Script `main.py` là một quy trình hoàn chỉnh được thiết kế để xử lý dữ liệu chuỗi thời gian từ các tệp MATLAB (`.mat`) cụ thể. Script sẽ thực hiện các bước sau cho mỗi tệp:
1.  **Tải dữ liệu** thô của cảm biến từ các trường (key) có tên kết thúc bằng 'X', 'Y', và 'Z'.
2.  **Lọc** dữ liệu để loại bỏ các tần số rất thấp (0-0.5 Hz).
3.  **Giảm mẫu** (decimate) dữ liệu để hạ tần số lấy mẫu.
4.  **Phân đoạn** dữ liệu đã xử lý thành các đoạn dài 50 giây.
5.  **Trực quan hóa** mỗi đoạn thành một biểu đồ đường và lưu dưới dạng tệp hình ảnh `.png`.

Toàn bộ quy trình này được thực hiện trong một lần chạy duy nhất mà không tạo ra các tệp trung gian.

## 2. Các thư viện yêu cầu

Để chạy script này, bạn cần một môi trường Python đã cài đặt các thư viện sau:
- `scipy`
- `numpy`
- `pandas`
- `matplotlib`

Các thư viện này đã có sẵn trong môi trường conda `lstm_fcn` mà chúng ta đã sử dụng.

## 3. Cách chạy script

Bạn có thể thực thi script từ cửa sổ dòng lệnh (terminal). Hãy chắc chắn rằng bạn đã kích hoạt đúng môi trường conda trước.

```bash
# 1. Kích hoạt môi trường conda
conda activate lstm_fcn

# 2. Chạy script main.py
python main.py
```

Sau khi chạy, script sẽ xử lý tất cả các tệp `.mat` được liệt kê bên trong nó và tạo ra các biểu đồ đầu ra trong thư mục `results`.

## 4. Giải thích các hàm

### `load_data_from_mat_file(file_path)`

Đây là hàm cốt lõi để trích xuất dữ liệu.

- **Đầu vào:** Nhận đường dẫn đến một tệp `.mat` duy nhất.
- **Quy trình:**
    1.  Tải tệp `.mat` thành một đối tượng dạng dictionary trong Python bằng `scipy.io.loadmat`.
    2.  Tìm kiếm tất cả các tên biến (key) trong tệp bắt đầu bằng `Untitled` và kết thúc bằng `X`, `Y`, hoặc `Z`. Điều này nhằm mục đích chỉ lấy dữ liệu từ các kênh cảm biến cụ thể.
    3.  Với mỗi key tìm thấy, nó truy cập vào cấu trúc dữ liệu lồng nhau. Dựa trên định dạng tệp, dữ liệu thực tế nằm ở `mat_data[key][0, 0]`.
    4.  Phần tử `[0, 0]` này là một đối tượng đặc biệt `numpy.void`, là cách SciPy biểu diễn một `struct` của MATLAB. Hàm sẽ kiểm tra xem `struct` này có chứa một trường tên là `'Data'` hay không.
    5.  Nếu trường `'Data'` tồn tại, nó sẽ trích xuất mảng số từ đó. Mảng này chứa dữ liệu đo lường chuỗi thời gian thực tế cho cảm biến đó.
    6.  Các mảng 1D được trích xuất (mỗi mảng cho một cảm biến) sau đó được xếp chồng lên nhau thành các cột để tạo thành một mảng 2D duy nhất.
- **Đầu ra:** Trả về một mảng NumPy 2D (`data_array`) trong đó mỗi cột là một cảm biến khác nhau, và một danh sách các key (`sensor_keys`) đã được trích xuất thành công.

### `main()`

Đây là hàm chính điều khiển toàn bộ quy trình làm việc.

- **Quy trình:**
    1.  Định nghĩa một danh sách tất cả các tệp `.mat` cần xử lý.
    2.  Lặp qua từng `file_path` trong danh sách.
    3.  Đối với mỗi tệp, nó gọi `load_data_from_mat_file` để lấy dữ liệu thô.
    4.  Chuyển đổi mảng dữ liệu đã tải thành một DataFrame của pandas để thực hiện các thao tác trên cột dễ dàng hơn. Mỗi cột được đặt tên theo key của cảm biến tương ứng (ví dụ: `Untitled3204Y`).
    5.  Sau đó, nó đi vào một vòng lặp để xử lý từng `sensor_col` (mỗi cột) trong DataFrame một cách độc lập.
    6.  **Lọc (Filtering):** Áp dụng bộ lọc thông cao Butterworth để loại bỏ các tần số dưới 0.5 Hz.
    7.  **Giảm mẫu (Decimation):** Giảm mẫu tín hiệu đã lọc với hệ số 20, giúp giảm đáng kể số lượng điểm dữ liệu và làm mịn tín hiệu.
    8.  **Phân đoạn và Trực quan hóa:** Tính toán số lượng đoạn 50 giây có thể được tạo ra từ dữ liệu đã giảm mẫu. Sau đó, nó lặp lại, tạo từng đoạn một và ngay lập tức tạo biểu đồ cho đoạn đó bằng `matplotlib`.
    9.  **Tùy chỉnh biểu đồ:** Mỗi biểu đồ được tạo với `figsize` là `(15, 3)` để đạt tỷ lệ khung hình 5:1 và không có tiêu đề, theo yêu cầu.
    10. **Lưu kết quả:** Biểu đồ được tạo sẽ được lưu trực tiếp dưới dạng tệp `.png` vào một cấu trúc thư mục đầu ra có tổ chức.

## 5. Cấu trúc thư mục đầu ra

Script sẽ tạo một thư mục cấp cao mới có tên là `results`. Cấu trúc của đầu ra sẽ như sau:

```
results/
├── SETUP1/
│   ├── Untitled3204Y/
│   │   ├── chunk_1.png
│   │   ├── chunk_2.png
│   │   └── ...
│   ├── Untitled3104Z/
│   │   ├── chunk_1.png
│   │   └── ...
│   └── ...
├── SETUP2/
│   ├── ...
└── ...
```

Mỗi tệp `.mat` sẽ có một thư mục riêng, và bên trong đó, mỗi kênh cảm biến đã xử lý sẽ có một thư mục con chứa các tệp hình ảnh `.png` của các đoạn dữ liệu của nó.
