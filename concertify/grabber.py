import os as _os
import shutil as _shutil
from typing import Generator as _Generator
import requests as _requests
from urllib.parse import quote as _quote
from bs4 import BeautifulSoup as _BeautifulSoup
from pydub import AudioSegment as _AudioSegment

class Grabber:
    """Grabs lrcs. Initialize with token."""
    
    def __init__(self, keep_cache=False):
        """Create a new grabber, creating a new cache by default."""
        
        # TODO: make this smarter
        self.track_counter = 0
        # self.album_counter = 0
        self.headers = {}
        self.cache = {}
        self.PATH = _os.path.join(_os.getcwd(), 'tmp')
        if not keep_cache:
            self.clear_cache()
        
    def clear_cache(self) -> None:
        """Clear spotdl and grabber cache."""
        
        self.track_counter = 0
        # self.album_counter = 0
        self.cache = {}
        if _os.path.exists(self.PATH):
            _shutil.rmtree(self.PATH)
        _os.mkdir(self.PATH)
        
    def set_token(self, token: str) -> None:
        """Get token using dev tools. Set the token. Required."""
        
        self.headers = {"Accept": "application/json",
                        "App-Platform": "WebPlayer",
                        "Authorization": f"Bearer {token}"}

    def get_lrc_json(self, track_url: str) -> tuple[int, dict, str]:
        """Get lrc as its status code, dictionary, and track info."""

        track = _requests.get(track_url)
        if track.status_code != 200:
            return track.status_code, {}, ''
        soup = _BeautifulSoup(track.content, 'html.parser')
        track_info = soup.title.get_text()
        track_name = track_info[:track_info.index('-') - 1]
        image_url = soup.find('img', {'alt': track_name})['src'] # check for other possible urls?
        image_encoded = _quote(image_url).replace('/', '%2F')

        track_id = track_url[31:track_url.index('?')]

        lrc_url = f'https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}/image/{image_encoded}?format=json&vocalRemoval=false'
        lrc = _requests.get(lrc_url, headers = self.headers)
        if lrc.status_code != 200:
            return lrc.status_code, {}, track_info
        lrc_json = lrc.json()
        
        return lrc.status_code, lrc_json, track_info
    
    def get_audio_segment(self, info: str) -> _AudioSegment:
        """Get the audio segment associated with the Spotify info from the cache."""
        
        return _AudioSegment.from_mp3(_os.path.join(self.PATH, "track", f"{self.cache[info]}.mp3"))
    
    def audio_generator(self, lrc_json: dict, info: str) -> _Generator[int, None, None]:
        """Yield each clip, joining empty/instrumental clips to the previous."""
        
        lines = lrc_json['lyrics']['lines']
        audio_segment = self.get_audio_segment(info)
        timestamps = [0] + [int(line['startTimeMs']) for line in lines if line['words'] not in ('', '♪')] + [len(audio_segment)]
        for i in range(1, len(timestamps)):
            yield audio_segment[timestamps[i - 1] : timestamps[i]]

    def download(self, url: str) -> str:
        """Download from a Spotify url."""
        
        if "track" in url:
            return self.download_track(url)
        
    def download_track(self, track_url: str) -> str:
        """Download a track to ./tmp/track/[index].mp3. Return the relevant Spotify info."""
        
        _os.system(f'spotdl -p track/{self.track_counter}.mp3 -o {self.PATH} --output-format mp3 {track_url}')
        _, _, info = self.get_lrc_json(track_url)
        self.cache[info] = self.track_counter
        self.track_counter += 1
        return info
        
    # def download_album(self, album_url: str) -> None:
    #     """Download an album to ./tmp/song.mp3"""

    #     _os.system(f"spotdl -p album/{self.album_counter}'{{artist}}/{{album}}/{{title}} - {{artist}}.mp3' -o {self.PATH} --output-format mp3 {album_url}")
    #     _, _, info = self.get_lrc_json(album_url)
    #     self.cache[info] = self.track_counter
    #     self.track_counter += 1