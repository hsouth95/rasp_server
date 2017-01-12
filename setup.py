from setuptools import setup

setup(
	name='rasp_server',
	packages=['rasp_server'],
	include_package_data=True,
	install_requires=[
		'flask',
	]
)