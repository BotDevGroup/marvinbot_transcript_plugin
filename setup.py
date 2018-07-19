from distutils.core import setup
from setuptools import find_packages

REQUIREMENTS = [
    'marvinbot',
    'urllib3',
    'googleapis-common-protos==1.5.3', # 1.6 beta versions are incompatible
    'google-cloud-speech==0.35.0'
]

setup(name='marvinbot-transcript-plugin',
      version='0.2',
      description='Transcribes voice notes to their textual representation.',
      author='Conrado Reyes',
      author_email='coreyes@gmail.com',
      url='',
      packages=[
        'marvinbot_transcript_plugin',
      ],
      package_dir={
        'marvinbot_transcript_plugin':'marvinbot_transcript_plugin'
      },
      zip_safe=False,
      include_package_data=True,
      package_data={'': ['*.ini']},
      install_requires=REQUIREMENTS,
      dependency_links=[
          'git+ssh://git@github.com:BotDevGroup/marvin.git#egg=marvinbot',
      ],
)
