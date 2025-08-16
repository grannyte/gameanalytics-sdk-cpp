import argparse
import os
import subprocess
import shutil
import glob

def run_command(command, shell=True, cwd=None):
	if os.name == 'nt':  # Check if the OS is Windows
		command = f'powershell.exe -Command "{command}"'
  
	result = subprocess.run(command, shell=shell, check=True, text=True, cwd=cwd)
	return result

def main():
	parser = argparse.ArgumentParser(description="CMake Build and Test Script")
	parser.add_argument('--platform', required=True, choices=['linux_x64', 'linux_x86', 'osx', 'win32', 'win64', 'uwp'], help='Platform to build for')
	parser.add_argument('--cfg', default='Debug', choices=['Release', 'Debug'], help='Configuration Type')
	parser.add_argument('--build', action='store_true', help='Execute the build step')
	parser.add_argument('--test', action='store_true', help='Execute the test step')
	parser.add_argument('--coverage', action='store_true', help='Generate code coverage report')
 
	args = parser.parse_args()

	build_output_dir = os.path.join(os.getcwd(), 'build')
	os.makedirs(build_output_dir, exist_ok=True)

	# Configure
	cmake_command = f'cmake -B \'{build_output_dir}\' -S \'{os.getcwd()}\''
	if args.platform == 'osx':
		cmake_command += ' -G "Xcode"'
	if args.platform:
		cmake_command += f' -DPLATFORM:STRING={args.platform}'
	if args.coverage:
		cmake_command += ' -DENABLE_COVERAGE=ON'

	print(cmake_command)
	run_command(cmake_command)

	# Build
	if args.build:
		print(f'cmake --build \'{build_output_dir}\' --config {args.cfg}')
		run_command(f'cmake --build \'{build_output_dir}\' --config {args.cfg}')
	else:
		exit(0)

	# Test
	if args.test:
		print(f'ctest --build-config {args.cfg} --verbose --output-on-failure')
		run_command(f'ctest --build-config {args.cfg} --verbose --output-on-failure', cwd=build_output_dir)
	else:
		exit(0)

	# Code Coverage
	if args.coverage:
		# Prepare coverage data
		print(f'cmake --build \'{build_output_dir}\' --target cov')
		run_command(f'cmake --build \'{build_output_dir}\' --target cov', cwd=build_output_dir)

	# Package Build Artifacts
	package_dir = os.path.join(build_output_dir, 'package')
	os.makedirs(package_dir, exist_ok=True)
	files_to_copy = glob.glob(f'{build_output_dir}/{args.cfg}/*GameAnalytics.*')
	for file in files_to_copy:
		shutil.copy(file, package_dir)
	shutil.copytree(os.path.join(os.getcwd(), 'include'), os.path.join(package_dir, 'include'), dirs_exist_ok=True)

	# Print Package Contents
	if args.platform.startswith('win'):
		print(f'dir {package_dir}')
		run_command(f'dir {package_dir}', shell=True)
	else:
		print(f'ls -la {package_dir}')
		run_command(f'ls -la {package_dir}', shell=True)

	if args.platform == 'osx':
		print(f'lipo -info {package_dir}/*GameAnalytics.*')
		run_command(f'lipo -info {package_dir}/*GameAnalytics.*')

if __name__ == "__main__":
	main()
