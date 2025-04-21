- Tạo file env.json để chứa keys với định dạng như sau:

{
  "APIFY_KEYS": "[\\"apify_key_1\\", \\"apify_key_2\\", ...]",
}

- Đầu vào của function là file json (input.json) với các tham số tương ứng:

{
  "urls": [
    "https://www.instagram.com/example_user_1",
    "https://www.instagram.com/example_user_2"
  ],
  "NumberPost": 10, (với NumberPost là số Post muốn trả về trên 1 profile)
}

- Thực thi bằng PowerShell với lệnh:

$token = gcloud auth print-identity-token; $headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }; $body = Get-Content -Raw -Path "./input.json"; Invoke-WebRequest -Uri "https://asia-southeast1-creator-dev-453406.cloudfunctions.net/crawl-instagram-posts" -Method POST -Headers $headers -Body $body

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
* Cách dùng tempmail để tạo key free:
B1: Truy cập vào trang web https://temp-mail.org/en/ để lấy mail tạm
B2: Vào trang đăng kí tài khoản Apify: https://console.apify.com/sign-up
B3: Nhập mail tạm mới lấy được đó vào ô email và thiết lập mật khẩu
B4: Khi bên Apify yêu cầu xác minh email thì quay lại trang web lấy mail tạm, refresh lại trang để nhận mail xác thực của Apify rồi xác thực
B5: Sau khi xác thực xong thì lấy key ở mục API của web Apify