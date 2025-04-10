import time

import requests


class ImageEditor:
    """
    # 参考文档 https://help.aliyun.com/zh/model-studio/user-guide/wanx-image-edit?spm=a2c4g.11186623.help\
    -menu-2400256.d_0_5_1.4563733fXm1Uak
    """

    def __init__(self, api_key):
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
        self.headers = {
            "X-DashScope-Async": "enable",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(api_key),
        }
        self._payload_template = {
            "model": "wanx2.1-imageedit",
            "input": {
                "function": "stylization_all",
            },
            "parameters": {"n": 1},
        }

    def build_payload(self, prompt, base_image_url):
        self._payload_template["input"]["prompt"] = prompt
        self._payload_template["input"]["base_image_url"] = base_image_url
        return self._payload_template

    def image_2_image(self, prompt, base_image_url):
        # 2. 发送POST请求
        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                json=self.build_payload(prompt, base_image_url),
            )
            response.raise_for_status()

            resp = response.json()
            print("Response JSON:", resp)
            # {'output': {'task_status': 'PENDING', 'task_id': '4248e4d2-4034-4afe-89af-6dd4aa2e57ef'},
            # 'request_id': '35e6a587-dc4b-904a-b364-57cf987928b0'}
            return resp

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")

    def check_task_status(self, task_id: str, poll_interval: int = 5) -> dict:
        """
        轮询任务状态直到成功或失败

        Args:
            task_id (str): 任务ID
            poll_interval (int): 轮询间隔（秒）

        Returns:
            dict: 任务最终结果（包含图片URL）
        """
        base_url = "https://dashscope.aliyuncs.com/api/v1/tasks/{}"

        while True:
            response = requests.get(url=base_url.format(task_id), headers=self.headers)
            response.raise_for_status()

            data = response.json()
            task_status = data.get("output", {}).get("task_status", "UNKNOWN")

            print(f"当前状态：{task_status}（{time.ctime()}）")

            if task_status == "SUCCEEDED":
                print("任务成功！")
                return data["output"]
            elif task_status == "FAILED":
                raise RuntimeError(
                    f"任务失败: {data.get('output', {}).get('error', '未知错误')}"
                )
            else:
                time.sleep(poll_interval)
