#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
import tf

class SimpleStraight:
    def __init__(self):
        rospy.init_node('simple_straight_test')

        # パブリッシャ：速度指令
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        
        # サブスクライバ：IMU（データが来ているか確認用）
        self.imu_sub = rospy.Subscriber('/imu/data', Imu, self.imu_callback)
        
        self.current_imu = None
        self.rate = rospy.Rate(10) # 10Hz

    def imu_callback(self, msg):
        # IMUのクォータニオンをオイラー角（RPY）に変換
        quaternion = (msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w)
        euler = tf.transformations.euler_from_quaternion(quaternion)
        self.current_imu = euler # (roll, pitch, yaw)

    def drive(self, duration, speed):
        rospy.loginfo(f"{duration}秒間、秒速{speed}mで直進します...")
        start_time = rospy.Time.now().to_sec()
        
        move_cmd = Twist()
        move_cmd.linear.x = speed
        move_cmd.angular.z = 0.0

        while rospy.Time.now().to_sec() - start_time < duration:
            if rospy.is_shutdown():
                break
            
            # 速度指令を出す
            self.cmd_pub.publish(move_cmd)
            
            # IMUの情報を画面に出す
            if self.current_imu:
                rospy.loginfo(f"IMU Yaw(向き): {self.current_imu[2]:.2f} rad")
            
            self.rate.sleep()

        # 停止させる
        rospy.loginfo("停止します。")
        self.cmd_pub.publish(Twist())

if __name__ == '__main__':
    try:
        tester = SimpleStraight()
        rospy.sleep(1) # 準備待ち
        
        # 【設定】5秒間、秒速 0.2m で進む
        tester.drive(duration=5.0, speed=0.2)
        
    except rospy.ROSInterruptException:
        pass