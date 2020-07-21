[QBT WebUI v3.2.0-v4.0.4 API](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation)
- [Add Torrent From Disk](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation#upload-torrent-from-disk) **POST /command/upload HTTP/1.1**
- [Add Torrent With URLs](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation#download-torrent-from-url) **POST /command/download HTTP/1.1**
  - Content-Type: application/x-www-form-urlencoded is required
  - urls contains a list of links; links are separated with %0A (LF newline, python eqivalent is '\r' ?)
  - Links' contents must be escaped, e.g. & becomes %26 (don't know about other characters but ampersand MUST be escaped)
- [Get Torrent List](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation#get-torrent-list) **GET /query/torrents HTTP/1.1**
  - Use response JSON's 'hash' field to start/stop/delete torrent
- [Search Torrent with Hash](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation#get-torrent-generic-properties) **GET /query/propertiesGeneral/<HASH_STRING> HTTP/1.1**
- [Start Torrent](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation#resume-torrent) **POST /command/resume HTTP/1.1**
- [Stop Torrent](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation#pause-torrent) **POST /command/pause HTTP/1.1**
- [Delete Torrent](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation#delete-torrent) **POST /command/delete HTTP/1.1**
  - To delete both Torrent **AND** Data, Refer to [Delete torrent with downloaded data](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation#delete-torrent-with-downloaded-data)
```rest
POST /command/upload HTTP/1.1
Content-Type: multipart/form-data; boundary=--AUTOMATICALLY_GENERATED_BY_PY-REQUESTS
User-Agent: Fiddler
Host: 127.0.0.1
Cookie: SID=your_sid
Content-Length: length

----AUTOMATICALLY_GENERATED_BY_PY-REQUESTS
Content-Disposition: form-data; name="torrents"; filename="8f18036b7a205c9347cb84a253975e12f7adddf2.torrent"
Content-Type: application/x-bittorrent

file_binary_data_goes_here
----AUTOMATICALLY_GENERATED_BY_PY-REQUESTS
Content-Disposition: form-data; name="torrents"; filename="UFS.torrent"
Content-Type: application/x-bittorrent

file_binary_data_goes_here
----AUTOMATICALLY_GENERATED_BY_PY-REQUESTS
Content-Disposition: form-data; name="savepath"

C:/Users/qBit/Downloads
----AUTOMATICALLY_GENERATED_BY_PY-REQUESTS
Content-Disposition: form-data; name="category"

movies
----AUTOMATICALLY_GENERATED_BY_PY-REQUESTS
Content-Disposition: form-data; name="skip_checking"

true
----AUTOMATICALLY_GENERATED_BY_PY-REQUESTS
Content-Disposition: form-data; name="paused"

true
----AUTOMATICALLY_GENERATED_BY_PY-REQUESTS--
```

[requests_toolbelt](https://stackoverflow.com/questions/12385179/how-to-send-a-multipart-form-data-with-requests-in-python)
```bash
pip install requests-toolbelt
```
```python
from requests_toolbelt import MultipartEncoder
mp_encoder = MultipartEncoder(
    fields={
        'foo': 'bar',
        # plain file object, no filename or mime type produces a
        # Content-Disposition header with just the part name
        'spam': ('spam.txt', open('spam.txt', 'rb'), 'text/plain'),
    }
)
req = requests.post(
    'http://httpbin.org/post',
    data=mp_encoder,  # The MultipartEncoder is posted as data, don't use files=...!
    # The MultipartEncoder provides the content-type header with the boundary:
    headers={'Content-Type': mp_encoder.content_type}
)
```
