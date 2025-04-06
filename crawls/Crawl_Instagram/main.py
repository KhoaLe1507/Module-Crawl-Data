from profile_scraper import scrape_profiles
from post_scraper import scrape_posts
import os
import json
import traceback
from flask import jsonify, make_response

def crawl_instagram(request):
    current_dir = os.path.dirname(__file__)
    urls_file = os.path.join(current_dir, "urls.txt")
    output_profile_file = "/tmp/instagram_data.json"
    output_post_file = "/tmp/instagram_post.json"
    results_limit = 1

    if not os.path.exists(urls_file):
        print("Không tìm thấy file urls.txt")
        return make_response(jsonify({"error": "File urls.txt không tồn tại"}), 500)

    try:
        print("Bắt đầu cào dữ liệu profile...")
        scrape_profiles(urls_file)
        print("Hoàn tất cào dữ liệu profile.")
    except Exception as e:
        print("Lỗi khi cào dữ liệu profile:", e)
        traceback.print_exc()
        return make_response(jsonify({
            "error": "Lỗi khi cào dữ liệu profile",
            "details": str(e),
            "trace": traceback.format_exc()
        }), 500)

    try:
        print("Bắt đầu cào dữ liệu post...")
        scrape_posts(urls_file, results_limit)
        print("Hoàn tất cào dữ liệu post.")
    except Exception as e:
        print("Lỗi khi cào dữ liệu post:", e)
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
