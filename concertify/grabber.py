import requests as _requests
from urllib.parse import quote as _quote
from bs4 import BeautifulSoup as _BeautifulSoup

class Grabber:
    """Grabs lrcs. Initialize with token."""
    
    def __init__(self, token: str):
        """Get token from Network tab. """
        # TODO: make this smarter
        self.token = token

    def get_lrc_json(self, track_url: str) -> tuple[int, dict]:
        """Get lrc as its status code and dictionary."""

        track = _requests.get(track_url)
        if track.status_code != 200:
            return track.status_code, {}
        soup = _BeautifulSoup(track.content, 'html.parser')
        track_info = soup.title.get_text()
        track_name = track_info[:track_info.index('-') - 1]
        image_url = soup.find('img', {'alt': track_name})['src'] # check for other possible urls?
        image_encoded = _quote(image_url).replace('/', '%2F')

        track_id = track_url[31:track_url.index('?')]

        lrc_url = f'https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}/image/{image_encoded}?format=json&vocalRemoval=false'
        lrc = _requests.get(lrc_url, headers = {"Accept": "application/json",
                                                "App-Platform": "WebPlayer",
                                                "Authorization": f"Bearer {self.token}"})
        if lrc.status_code != 200:
            return lrc.status_code, {}
        lrc_json = lrc.json()
        
        return lrc.status_code, lrc_json