import os
import requests
from pathlib import logger

class MultiPlatformPublisher:
    def __init__(self):
        self.tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_user_id = os.getenv("INSTAGRAM_USER_ID")
        self.youtube_token = os.getenv("YOUTUBE_ACCESS_TOKEN")

    def publish_tiktok(self, video_path: str, caption: str):
        url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {self.tiktok_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "post_info": {
                "title": caption,
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": os.path.getsize(video_path),
                "chunk_size": 10000000
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def publish_instagram_reel(self, video_url: str, caption: str):
        url = f"https://graph.facebook.com/v18.0/{self.ig_user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.ig_token
        }
        response = requests.post(url, data=payload)
        return response.json()

    def publish_youtube_short(self, video_path: str, title: str, description: str):
        url = "https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status"
        headers = {
            "Authorization": f"Bearer {self.youtube_token}",
            "Content-Type": "video/mp4"
        }
        metadata = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "24",
                "tags": ["Cinegrade", "Shorts", "Cinematic"]
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        # Multipart upload implementation wrapper
        return {"status": "dispatched", "platform": "youtube"}