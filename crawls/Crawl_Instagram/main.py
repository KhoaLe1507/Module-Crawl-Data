from profile_scraper import scrape_profiles
from post_scraper import scrape_posts
import os
import json
import traceback  # <- Thêm dòng này
from flask import make_response, jsonify

def crawl_instagram(request):
    """
    Hàm xử lý HTTP trigger cho Cloud Functions.
    Cào dữ liệu từ Instagram và trả về kết quả dưới dạng JSON.
    """
    urls_file = "urls.txt"            # File chứa danh sách URL
    output_profile_file = "/tmp/instagram_data.json"
    output_post_file = "/tmp/instagram_post.json"  # File lưu dữ liệu cào về
    results_limit = 1

    # Kiểm tra xem file urls.txt có tồn tại không
    if not os.path.exists(urls_file):
        print("[❌] Không tìm thấy file urls.txt")
        return make_response(jsonify({"error": "File urls.txt không tồn tại"}), 500)

    try:
        print("[🚀] Bắt đầu cào dữ liệu profile...")
        scrape_profiles(urls_file)
        print("[✅] Hoàn tất cào dữ liệu profile.")
    except Exception as e:
        print("[❌] Lỗi khi cào dữ liệu profile:", e)
        traceback.print_exc()
        return make_response(jsonify({
            "error": "Lỗi khi cào dữ liệu profile",
            "details": str(e),
            "trace": traceback.format_exc()
        }), 500)

    try:
        print("[🚀] Bắt đầu cào dữ liệu post...")
        scrape_posts(urls_file, results_limit)
        print("[✅] Hoàn tất cào dữ liệu post.")
    except Exception as e:
        print("[❌] Lỗi khi cào dữ liệu post:", e)
        traceback.print_exc()
        return make_response(jsonify({
            "error": "Lỗi khi cào dữ liệu post",
            "details": str(e),
            "trace": traceback.format_exc()
        }), 500)

    response_data = {
        "message": "Dữ liệu đã được cào thành công từ Instagram",
        "profile_data_file": output_profile_file,
        "post_data_file": output_post_file
    }

    return jsonify(response_data)
