import os
import re
import time
import tqdm
import asyncio
import aiohttp
import requests
import nest_asyncio


# global urls to avoid downloading the same url more than once
nest_asyncio.apply()
total_video_files = []


class DownLoadTsv:
    def __init__(self, url, num, path_out):
        self.url = url
        self.header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 '
                                     '(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        self.num = num
        self.path_out = path_out
        self.tsv_items = []
        self.total_results = []

    @staticmethod
    async def fetch(*args):
        tsv, session, semaphore = args
        # 60 seconds timeout
        timeout = aiohttp.ClientTimeout(total=None, sock_connect=60, sock_read=60)
        async with semaphore:
            async with session.get(tsv, timeout=timeout) as result:
                # return the code of the video
                video = await result.read()
                # return a tuple, tsc is used for sorting
                return os.path.basename(tsv), video

    async def download(self):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]: Start parsing {self.url}")
        semaphore = asyncio.Semaphore(int(self.num))
        tasks = []
        connector = aiohttp.TCPConnector(limit_per_host=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            for each_tsv in self.tsv_items:
                task = asyncio.ensure_future(self.fetch(each_tsv, session, semaphore))
                tasks.append(task)
                # self.total_results = await asyncio.gather(*tasks)
            # show the process bar for all the tsc downloads
            self.total_results = [await f for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks))]
            # same meaning as the following codes
            # pbar = tqdm.tqdm(total=len(tasks))
            # for f in asyncio.as_completed(tasks):
            #    value = await f
            #    self.total_results.append(value)
            #    # pbar.set_description(value)
            #    pbar.update()
            # pbar.close()

    def run(self):
        # requests get m3u8 file from url
        content = requests.get(self.url, headers=self.header).text
        self.tsv_items = re.findall(r"EXTINF:.*,\n(.*)\n#", content)
        if not self.tsv_items:
            print(f"[WARNING]: Failed to get tsv items from {self.url}")
            return False
        # sort the ts files according to the number in the url
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.download())
        # loop.close()
        sorted_ts = list(map(lambda k: k[1],
                             sorted(self.total_results, key=lambda k: int(k[0].split(".")[1].split("_")[1]))))
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]: Start writing to {self.path_out}")
        with open(self.path_out, "wb") as out:
            for each_ts in sorted_ts:
                out.write(each_ts)


def response(flow):
    url = flow.request.url
    run = False
    m3u8_name = ""
    if re.search(r"\.m3u8\?time", url):
        run = True
    elif re.search(r"\.m3u8", url):
        run = True
    if run:
        m3u8_name = re.findall(r"(.*?)\.m3u8", os.path.basename(url))[0]
        if not m3u8_name:
            raise ValueError("Invalid M3U8 name!")
        path_out = f"D:\\mask_videos\\{m3u8_name}.mp4"
        if path_out not in total_video_files:
            total_video_files.append(path_out)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]: Sniffing m3u8 {url}")
            this_downloadtsv = DownLoadTsv(url=url, num=10, path_out=path_out)
            this_downloadtsv.run()


