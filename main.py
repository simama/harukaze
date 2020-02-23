import os
import sys
import json
import argparse
from multiprocessing import Process, Queue, Manager

import cv2
import numpy as np
import pyrealsense2 as rs
from openpose import pyopenpose as op

from pose import Pose, pose_points_from_json
from animation import Animation
from drawables import ChaserBall


# inference_directory = 'data/pose_output/output'
# inference_files = sorted([os.path.join(inference_directory, f) for f in os.listdir(inference_directory)])

# cap = cv2.VideoCapture('data/ai_dance_short.MOV')


# pose = Pose()
# animation = Animation()
# animation.add_pose(pose)

# animation.objects.append(ChaserBall(pose.joints["right_hand"], x=300, y=300))
# animation.objects.append(ChaserBall(pose.joints["head"], x=300, y=300))
# animation.objects.append(ChaserBall(pose.joints["left_hand"], x=300, y=300))


def parse_arguments():
    parser = argparse.ArgumentParser(description="Harukaze performance code.")
    parser.add_argument("--op-model-folder",
                        default="~/openpose/models/",
                        type=str,
                        help="Absolute path to network models.")
    parser.add_argument("--otput-pose-dir",
                        default="~/harukaze/output",
                        type=str,
                        help="Absolute path to the desired output folder.")
    parser.add_argument("--data-dir",
                        default="~/harukaze/data",
                        type=str,
                        help="Absolute path to the folder containing data for inference.")
    return parser.parse_known_args()


def set_openpose(args):
    params = dict()
    # manager = Manager()
    # params = manager.dict()

    for arg in vars(args[0]):
        if arg.startswith("op_"):
            val = getattr(args[0], arg)
            argument = arg.strip("op_")
            params[argument] = val
    # print(params)
    return params


def run_openpose(openpose_params):
    print(openpose_params)
    opWrapper = op.WrapperPython()
    opWrapper.configure(openpose_params)
    opWrapper.start()

    datum = op.Datum()
    print("Initialized OpenPose!")


def initialize_realsense():
    cv2.namedWindow("projection", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("projection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # fan_graphics = cv2.imread("/home/ascent/Pictures/fan_diff_small.png")
    stream = cv2.VideoCapture(-1)
    pipe = rs.pipeline()
    profile = pipe.start()
    return stream, pipe, profile


def project_visuals():
    stream, pipe, profile = initialize_realsense()
    while True:
        frames = pipe.wait_for_frames()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

        cv2.imshow("projection", color_image)
        key = cv2.waitKey(1)
        if key == ord("q"):
            return "Closing the app, user pressed 'q' key!"


# i = 0
# while(cap.isOpened()):
#     print(i)
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#     width, height = frame.shape[:2]

#     if ret == True:

#         json_path = inference_files[i]

#         pose_points = pose_points_from_json(json_path)
#         if pose_points is not None:
#             animation.update_pose(pose_points)

#         # exit()

#         # animation.update()
#         frame = animation.draw_pose(frame)
#         print(animation.pose)
#         print(animation.pose.joints["right_hand"])

#         animation.update()
#         frame = animation.draw(frame)

#         cv2.imshow('Frame', frame)

#       # Press Q on keyboard to  exit
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#           break

#     # Break the loop
#     else:
#         break

#     i += 1

# # When everything done, release the video capture object
# cap.release()

# # Closes all the frames
# cv2.destroyAllWindows()


if __name__ == "__main__":
    arguments = parse_arguments()
    openpose_params = set_openpose(arguments)
    q = Queue()
    p = Process(target=run_openpose, args=(openpose_params,))
    p.start()
    message = project_visuals()
    print(message)
    p.join()