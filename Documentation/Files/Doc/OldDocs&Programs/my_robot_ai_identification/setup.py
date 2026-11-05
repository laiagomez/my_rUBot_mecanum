from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'my_robot_ai_identification'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.*'))),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.*'))),
        (os.path.join('share', package_name, 'models'), glob(os.path.join('models', '*.*'))),
        (os.path.join('share', package_name, 'photos'), glob(os.path.join('photos', '*.*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rubot_rt_yolo_cls_exec = my_robot_ai_identification.rubot_rt_yolo_cls:main',
            'rubot_rt_yolo_det_exec = my_robot_ai_identification.rubot_rt_yolo_det:main',
            'rubot_identification_yolo_det_exec = my_robot_ai_identification.rubot_identification_yolo_det:main',
            'rubot_identification_yolo_cls_exec = my_robot_ai_identification.rubot_identification_yolo_cls:main',
            'rubot_targets_yolo_exec = my_robot_ai_identification.rubot_targets_yolo:main',
            'traffic_sign_yolo_exec = my_robot_ai_identification.traffic_sign_yolo:main',
        ],
    },
)
