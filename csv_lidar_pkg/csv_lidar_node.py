import rclpy
from rclpy.node import Node
import csv
from sensor_msgs.msg import LaserScan
import os
from datetime import datetime

class CSVLidarNode(Node):
    def __init__(self):
        super().__init__('lidar_to_csv_node')

        self.scan_subscription = self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10)

        self.declare_parameter('num_scans', 1)
        self.num_scans = self.get_parameter('num_scans').get_parameter_value().integer_value
        self.scans_received = 0

        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename = f"lidar_scans_{timestamp}.csv"

        # Open het CSV-bestand en maak een writer
        self.filepath = os.path.expanduser('~/ros2_ws/src/csv_lidar_pkg/data_lidar/'+ filename)
        self.csv_file = open(self.filepath, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        # Schrijf de header naar het CSV-bestand
        self.csv_writer.writerow(['Scan_number', 'Angle', 'Distance'])
        #self.csv_writer.writerow(['Angle', 'Distance'])

    def lidar_callback(self, msg):
        if self.scans_received < self.num_scans:
            self.scans_received += 1

            angle_increment = msg.angle_increment
            angle = msg.angle_min

            for distance in msg.ranges:
                self.csv_writer.writerow([self.scans_received, angle, distance])
                angle += angle_increment
            #for distance in msg.ranges:
            #    self.csv_writer.writerow([angle, distance])
            #    angle += angle_increment

            self.csv_file.flush()
            

            # Als we klaar zijn met het aantal gewenste scans, dan stoppen we bijvoorbeeld de subscription
            if self.scans_received >= self.num_scans:
                # terminal vol met berichten, check of de scan is opgeslagen. 
                print(f"Alle {self.num_scans} scans opgeslagen in {self.filepath}. Node wordt gestopt.")
                self.scan_subscription.destroy()


def main(args=None):
    rclpy.init(args=args)
    node = CSVLidarNode()
    rclpy.spin(node)
    node.csv_file.close()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
