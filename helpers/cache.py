from datetime import datetime, timedelta

# کش موقت در RAM: جلوگیری از دانلود مجدد ویدیو در 5 دقیقه
VIDEO_CACHE = {}  # { video_url: (file_id, expire_time) }

def set_video_cache(video_url: str, file_id: str):
    VIDEO_CACHE[video_url] = (file_id, datetime.now() + timedelta(minutes=5))

def get_video_cache(video_url: str):
    if video_url in VIDEO_CACHE:
        file_id, expire = VIDEO_CACHE[video_url]
        if datetime.now() < expire:
            return file_id
        else:
            del VIDEO_CACHE[video_url]
    return None
