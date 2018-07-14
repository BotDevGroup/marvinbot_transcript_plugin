from distutils.core import setup
from setuptools import find_packages

REQUIREMENTS = [
    'marvinbot', 'google-api-python-client', 'httplib2'
]

setup(name='marvinbot-transcript-plugin',
      version='0.1',
      description='Converter voice note to text',
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
