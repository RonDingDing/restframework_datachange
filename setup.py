from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='restframework_datachange',
      version='0.0.1',
      description='Change data in ModelViewSet',
      long_description=open('README.md', 'r').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/RonDingDing/restframework_datachange',
      author='Ron Ding',
      author_email='ronweasleyding@163.com',
      license='Anti 996 License',
      packages=find_packages(),
      install_requires=[
          'django>=2.1.7',
          'djangorestframework>=3.9.1',

      ]

      )
