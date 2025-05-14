import re, requests, json
from html import unescape


class VideoExtraction:
    def __init__(self):
        pass

    def get_platform(self, url: str) -> bool:
        url = url.strip().lower()

        if 'youtube.com'in url or 'youtu.be' in url:
            return True
        return False

    def get_video_id(self, url: str) -> str:
        """
            input (Parameter): Get the video URL.
            Output: Return the Video ID.
        """
        if not url: return None

        if self.get_platform(url=url):
            url = url.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/|.*[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})'
            video_id = re.findall(pattern, url)
            return video_id[0]
        return None
    
    def get_meta_data(self, video_id) -> dict:
        """
            Get meta data for the given Video Id.
        """
        meta_data = {
            "title": f"Youtube Video: {video_id}",
            "paltform": "Youtube",
            "description": "",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            "duration": 300,
            "views": 0,
            "author": "Unknown",
            "video_id": video_id,
        }

        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            }
            response = requests.get(url=url, headers=headers)
            
            if response.status_code != 200:
                print(f"Bad response, so couldn't find the metadatas as response: {response.status_code}")
                return meta_data
            
            html = response.text
            match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
            if not match:
                print("ytInitialPlayerResponse not found.")
                return meta_data

            player_response = json.loads(match.group(1))
            video_details = player_response.get("videoDetails", {})
            microformat = player_response.get("microformat", {}).get("playerMicroformatRenderer", {})

            meta_data["title"] = video_details.get("title", meta_data["title"])
            meta_data["author"] = video_details.get("author", meta_data["author"])
            meta_data["views"] = int(video_details.get("viewCount", 0))
            meta_data["duration"] = int(video_details.get("lengthSeconds", 0))

            # Get clean description (cut off at first 2 paragraphs or 500 chars)
            raw_description = unescape(video_details.get("shortDescription", ""))
            lines = raw_description.strip().split("\n")
            filtered_lines = [line for line in lines if not line.lower().startswith("http")]
            meta_data["description"] = "\n".join(filtered_lines[:5])[:500].strip()

            # Try high-quality thumbnail fallback
            thumbnails = video_details.get("thumbnail", {}).get("thumbnails", [])
            if thumbnails:
                meta_data["thumbnail_url"] = thumbnails[-1]["url"].split("?")[0]  # remove query params

            return meta_data

        except Exception as e:
            raise Exception(e)

v = VideoExtraction()
url = "www.youtube.com/watch?v=bR7mQgwQ_o8&list=PLgUwDviBIf0rENwdL0nEH0uGom9no0nyB&index=19"

platform = v.get_platform(url=url)
if platform:
    video_id = v.get_video_id(url=url)
    meta_data = v.get_meta_data(video_id=video_id)
    print(meta_data)
else:
    print(f"Oops, seems like you have given url of other platform, please provide Youtube URL!")