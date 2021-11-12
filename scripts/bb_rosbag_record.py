#!/usr/bin/python2.7

import sys
import os
import logging
import subprocess
import datetime

import rospy

from std_msgs.msg import Int32MultiArray, Float32, Int32, Float32MultiArray, String, Bool

from carecules_data_recording.srv import cc_rosbag_recorder, cc_rosbag_recorderRequest, cc_rosbag_recorderResponse

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('carecules_ros_bag_recorder')


class CareculesRosBagRecorder(object):
    def __init__(self):
        self.__update_rate = 1
        self.__rate = None

        current_time = datetime.datetime.now()
        self.__date_time_str = current_time.strftime("%d.%m.%Y_%H-%M-%S")
        self.__rosbag_folder = rospy.get_param("/carecules_rosbag_recorder/rosbag_base_path", os.path.join(os.getenv('HOME'), 'cc_rosbags'))
        rospy.loginfo('CareculesRosBagRecorder recording bags to path: ' + self.__rosbag_folder)

        self.__active_bag_file_name = ''
        self.__default_topics = []

        current_run_directory = os.path.join(self.__rosbag_folder, self.__date_time_str)
        if not os.path.exists(current_run_directory):
            os.makedirs(os.path.join(self.__rosbag_folder, self.__date_time_str), 0o755)
            rospy.loginfo('CareculesRosBagRecorder successfully created current recording run directory: ' + current_run_directory)
        else:
            rospy.logerror('CareculesRosBagRecorder FAILED TO CREATE current recording run directory: ' + current_run_directory + '! Either it already exists, or directory permissions prevent creation.')
    
        self.__rosbag_process = None
        self.__rosbag_record_service = None

    def __call__(self, *args, **kwargs):
        try:
            rospy.loginfo('CareculesRosBagRecorder __call__')
            self.__update_rate = rospy.get_param('~rate', 1)
            self.__rate = rospy.Rate(self.__update_rate)

            self.__default_topics = rospy.get_param('default_topic_list')

            self.__rosbag_record_service = rospy.Service('cc_rosbag_recorder', cc_rosbag_recorder,
                                                         self.cc_record_cb)

            rospy.loginfo('Calling self.spin() now.')
            self.spin()

        except rospy.ROSInterruptException:
            pass

    def cc_record_cb(self, request):
        rospy.loginfo('Received rosbag recording request: ' + str(request))
        resp = cc_rosbag_recorderResponse()
        if request.startRecording:
            topics_to_record = request.topicsToRecord
            if request.useDefaultTopics:
                topics_to_record = self.__default_topics

            rospy.loginfo('Request start of rosbag recording. Topics: ' + str(topics_to_record))
            current_time = datetime.datetime.now()
            date_time_str = current_time.strftime("%d.%m.%Y_%H-%M-%S")
            self.__active_bag_file_name = 'cc_bag_' + date_time_str + '.bag'
            self.start_rosbag_node(self.__active_bag_file_name, topics_to_record)
            resp.recordingActive = True
            resp.recordingStatus = 'Started recording to rosbag file: ' + self.__active_bag_file_name
        else:
            rospy.loginfo('Request stop of running rosbag recording: ' + self.__active_bag_file_name)
            self.terminate_ros_node('/record')
            resp.recordingActive = False
            resp.recordingStatus = 'Finished recording to rosbag file: ' + self.__active_bag_file_name

        return resp

    def spin(self):
        rospy.loginfo("CareculesRosBagRecorder spin()")

        rospy.on_shutdown(self.shutdown)

        while not rospy.is_shutdown():
            rospy.logdebug('Sleeping: ' + str(self.__rate.remaining()) + ' ns.')
            self.__rate.sleep()

        rospy.spin()

    def shutdown(self):
        rospy.loginfo("CareculesRosBagRecorder shutdown()")
        rospy.sleep(1)

    def start_rosbag_node(self, bag_file_name, topic_list):
        rospy.loginfo('Start rosbag recording.')
        command = 'rosbag record -O ' + bag_file_name + ' ' + ' '.join(topic_list)
        self.__rosbag_process = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True, cwd=self.__rosbag_folder)

    def terminate_ros_node(self, s):
        # Adapted from http://answers.ros.org/question/10714/start-and-stop-rosbag-within-a-python-script/
        list_cmd = subprocess.Popen("rosnode list", shell=True, stdout=subprocess.PIPE)
        list_output = list_cmd.stdout.read()
        retcode = list_cmd.wait()
        assert retcode == 0, "List command returned %d" % retcode
        for str in list_output.split("\n"):
            if (str.startswith(s)):
                os.system("rosnode kill " + str)


if __name__ == '__main__':
    logger.info('Starting CareculesRosBagRecorder')

    logger.debug('init_node - calling')
    rospy.init_node('CareculesRosBagRecorder', anonymous=False)
    logger.debug('init_node - called')

    cc_mapping_co = CareculesRosBagRecorder()
    cc_mapping_co()

    logger.info('Stopping CareculesRosBagRecorder.')

    sys.exit(0)
