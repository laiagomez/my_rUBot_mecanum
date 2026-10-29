import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'my_robot_ai_perception'


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'models'), glob('models/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Manel Puig',
    maintainer_email='manel.puig@ub.edu',
    description='AI perception nodes for the rUBot.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'traffic_sign_classifier_exec = '
            'my_robot_ai_perception.traffic_sign_classifier:main',
        ],
    },
)
