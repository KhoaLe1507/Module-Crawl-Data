from profile_scraper import scrape_profiles
from post_scraper import scrape_posts
import os
import json
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
        return make_response(jsonify({"error": "File urls.txt không tồn tại"}), 500)
    
    # Cào dữ liệu profile và post
    try:
        scrape_profiles(urls_file, output_profile_file)
    except Exception as e:
        return make_response(jsonify({"error": "Lỗi khi cào dữ liệu profile", "details": str(e)}), 500)

    try:
        scrape_posts(urls_file, output_post_file, results_limit)
    except Exception as e:
        return make_response(jsonify({"error": "Lỗi khi cào dữ liệu post", "details": str(e)}), 500)

    # Trả về thông báo thành công mà không cần đọc lại dữ liệu từ file
    response_data = {
        "message": "Dữ liệu đã được cào thành công từ Instagram",
        "profile_data_file": output_profile_file,
        "post_data_file": output_post_file
    }

    return jsonify(response_data)
