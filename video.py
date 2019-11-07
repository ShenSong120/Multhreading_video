import os
import cv2
import time
import numpy as np
from threading import Thread


# 生成测试视频(显示1-5000)--检查是否丢帧
# font=cv2.FONT_HERSHEY_SIMPLEX
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# out = cv2.VideoWriter('video/test/test.mp4', fourcc, 120.0, (1600, 1000))
#
# for i in range(5000):
#     print(i+1)
#     img=np.zeros((1000, 1600, 3), np.uint8)
#     cv2.putText(img, str(i+1) , (200, 200), font, 4, (255, 255, 255), 2)
#     out.write(img.copy())
# out.release()

# class Video:
#     def __init__(self):
#         # 帧id
#         self.frame_id = 0
#         # 存储需要保存的帧
#         self.frame_list = []
#         # record结束标志
#         self.record_stop_flag = False
#         self.record_flag = True
#         self.record_thread_flag = True
#         self.robot_start_flag = False
#         # 是否可以重新开始录制视频
#         self.restart_record_flag = True
#         # 视频类型(app冷/app热/滑动流畅度等等)
#         self.case_type = None
#         # 视频名称(桌面滑动)
#         self.case_name = None
#
#
#     def video_stream(self):
#         cap = cv2.VideoCapture('D:/Test/Python/CameraCalibrate/video/test/test.mp4')
#         while self.record_thread_flag :
#             _, image = cap.read()
#             if self.record_flag is True:
#                 if self.robot_start_flag is False:
#                     self.frame_list.append(image)
#                 else:
#                     self.frame_list.append(image[0].fill(255))
#                 self.frame_id += 1
#         cap.release()
#         print('退出视频录像线程')
#
#
#     def save_video(self):
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         out = cv2.VideoWriter('video/test/123.mp4', fourcc, 120.0, (1600, 1000))
#         while True:
#             if len(self.frame_list) > 0:
#                 out.write(self.frame_list[0])
#                 self.frame_list.pop(0)
#             elif self.record_stop_flag is True:
#                 while True:
#                     if len(self.frame_list) > 0:
#                         out.write(self.frame_list[0])
#                         self.frame_list.pop(0)
#                     else:
#                         break
#                 break
#             else:
#                 time.sleep(0.001)
#         out.release()
#         print('保存结束')
#
#
# if __name__=='__main__':
#     video = Video()
#     Thread(target=video.video_stream, args=()).start()
#     Thread(target=video.save_video, args=()).start()
#     time.sleep(5)
#     video.record_flag = False
#     video.record_stop_flag = True
#     print(video.frame_id)
#     video.record_thread_flag = False



class Video:
    def __init__(self, video_path):
        # 视频存放根目录
        self.video_path = video_path
        # 保存的视频名
        self.video_file_name = None
        # 帧id
        self.frame_id = 0
        # 存储需要保存的帧
        self.frame_list = []
        # 是否正在record标志
        self.record_flag = False
        # 是否停止record线程标志
        self.record_thread_flag = True
        # 机械臂设置起点标记标志
        self.robot_start_flag = False
        # 是否可以重新开始录制视频
        self.restart_record_flag = True
        # 视频类型(app冷/app热/滑动流畅度等等)
        self.case_type = None
        # 视频名称(桌面滑动)
        self.case_name = None
        Thread(target=self.video_stream, args=()).start()


    def video_stream(self):
        cap = cv2.VideoCapture('D:/Test/Python/CameraCalibrate/video/multiple_frame_60s.mp4')
        # cap = cv2.VideoCapture('D:/Test/Python/CameraCalibrate/video/test/test.mp4')
        while self.record_thread_flag:
            _, image = cap.read()
            if self.record_flag is True:
                if self.robot_start_flag is False:
                    self.frame_list.append(image)
                else:
                    self.frame_list.append(image[0].fill(255))
                self.frame_id += 1
        cap.release()
        print('退出视频录像线程')


    def save_video(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.video_file_name, fourcc, 120.0, (1600, 1000))
        while True:
            if len(self.frame_list) > 0:
                out.write(self.frame_list[0])
                self.frame_list.pop(0)
            elif self.record_flag is False:
                while True:
                    if len(self.frame_list) > 0:
                        out.write(self.frame_list[0])
                        self.frame_list.pop(0)
                    else:
                        break
                break
            else:
                time.sleep(0.001)
        out.release()
        self.restart_record_flag = True
        print('视频保存结束: ', self.video_file_name)


    def start_record(self, case_type='test', case_name='test'):
        self.case_type = case_type
        self.case_name = case_name
        # 创建文件夹(没有就创建)
        video_path = self.video_path + '/' + self.case_type
        if os.path.exists(video_path) is False:
            os.makedirs(video_path)
        self.video_file_name = self.video_path + '/' + self.case_type + '/' + self.case_name + '.mp4'
        # 判断视频是否保存完成
        if self.restart_record_flag is False:
            print('上一个视频还未保存完成, 请稍等...')
            while self.restart_record_flag is False:
                time.sleep(0.002)
            # 重新录制视频标志重新置位
        self.restart_record_flag = False
        '''开始录像(通过标志位)'''
        self.record_flag = True
        Thread(target=self.save_video, args=()).start()
        print('开始录制视频: ', self.video_file_name)


    def stop_record(self):
        self.record_flag = False
        print('当前视频帧数为: ', self.frame_id)
        self.frame_id = 0


    def stop_record_thread(self):
        # 判断视频是否保存完成(保存完才能停止线程)
        if self.restart_record_flag is False:
            print('上一个视频还未保存完成, 请稍等一会再退出线程...')
            while self.restart_record_flag is False:
                time.sleep(0.002)
        time.sleep(0.5)
        self.record_thread_flag = False


if __name__=='__main__':
    video = Video(video_path='D:/Test/Python/CameraCalibrate/video')
    time.sleep(2)
    # 第一个视频
    video.start_record(case_type='test', case_name='123')
    time.sleep(5)
    video.stop_record()

    time.sleep(10)

    # 第二个视频
    video.start_record(case_type='test', case_name='456')
    time.sleep(5)
    video.stop_record()
    video.stop_record_thread()