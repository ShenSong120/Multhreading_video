import os
import cv2
import time
import numpy as np
from threading import Thread


class Video:
    def __init__(self, video_path, video_width, video_height):
        # 视频尺寸
        self.video_width = video_width
        self.video_height = video_height
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
        # 畸变矫正相关参数
        npz_file = np.load('../calibrate.npz')
        self.mtx = npz_file['mtx']
        self.dist = npz_file['dist']
        self.map_x = None
        self.map_y = None
        # 开启视频流
        Thread(target=self.video_stream, args=()).start()

    # 消除畸变
    def undistortion(self, img, mtx, dist):
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        # print('roi ', roi)
        # 耗时操作
        # dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        # 替代方案(节省时间)/map_x, map_y使用全局变量更加节省时间
        if self.map_x is None and self.map_y is None:
            # 计算一个从畸变图像到非畸变图像的映射(只需要执行一次, 找出映射关系即可)
            self.map_x, self.map_y = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
        # 使用映射关系对图像进行去畸变
        dst = cv2.remap(img, self.map_x, self.map_y, cv2.INTER_LINEAR)
        # 裁剪图片
        # x, y, w, h = roi
        # if roi != (0, 0, 0, 0):
        #     dst = dst[y:y + h, x:x + w]
        return dst


    def video_stream(self):
        # cap = cv2.VideoCapture(0)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
        # cap = cv2.VideoCapture('D:/Test/Python/CameraCalibrate/video/multiple_frame_60s.mp4')
        cap = cv2.VideoCapture('D:/Test/Python/CameraCalibrate/video/test/test.mp4')
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
        out = cv2.VideoWriter(self.video_file_name, fourcc, 120.0, (self.video_width, self.video_height))
        while 1:
            if len(self.frame_list) > 0:
                # frame = self.undistortion(self.frame_list[0], self.mtx, self.dist)
                # out.write(frame)
                out.write(self.frame_list[0])
                self.frame_list.pop(0)
            elif self.record_flag is False:
                while 1:
                    if len(self.frame_list) > 0:
                        # frame = self.undistortion(self.frame_list[0], self.mtx, self.dist)
                        # out.write(frame)
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
        # 判断视频是否保存完成(保存完毕才允许再次开始录像)
        if self.restart_record_flag is False:
            print('上一个视频还未保存完成, 请稍等...')
            while self.restart_record_flag is False:
                time.sleep(0.002)
        # 传入视频类型和视频名
        self.case_type = case_type
        self.case_name = case_name
        # 创建文件夹(没有就创建)
        video_path = self.video_path + '/' + self.case_type
        if os.path.exists(video_path) is False:
            os.makedirs(video_path)
        self.video_file_name = self.video_path + '/' + self.case_type + '/' + self.case_name + '.mp4'
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
    # video = Video(video_path='D:/Test/Python/CameraCalibrate/video', video_width=1600, video_height=1000)
    # video = Video(video_path='C:/Work/video', video_width=1280, video_height=720)
    video = Video(video_path='C:/Work/video', video_width=1600, video_height=1000)
    time.sleep(2)
    # time.sleep(10)
    # 第一个视频
    video.start_record(case_type='test', case_name='123')
    time.sleep(5)
    video.stop_record()

    # 第二个视频
    video.start_record(case_type='test', case_name='456')
    time.sleep(5)
    video.stop_record()
    video.stop_record_thread()