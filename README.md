# video_downloader

A very simple script to sniff m3u8 data from web servers or software like wechat or QQ. This script must be used with mitmdump.

```
pip install mitmdump
mitmdump -s .\video_downloader.py
```
Follow the steps below to start the video download step.
- Start up mitmdump by mitmdump -s .\video_downloader.py, and make sure you can visit http://mitm.it/. If you get error like "if you can see this, traffic is not passing through mitmproxy", please look for solutions in https://stackoverflow.com/questions/67821404/how-to-install-mitmproxy-certificate-on-windows-10.
- open google chrome or IE or Edge, and open a video. Mitmdump will capture the m3u8 url and our script will download all the ts files in that url asynchronously.
- If you open the video and nothing is captured, then you have to modify the scirpt to parse the m3u8 link.

