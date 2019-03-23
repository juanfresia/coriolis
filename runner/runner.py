import os
import errno
import re
import sys

ROOTDIR = "/home/ale/Programacion/ConcuVoley"
C_EXTENSIONS = [".c", ".h", ".cpp"]
EXTRA_FILES = ["makefile", "conf.txt", "ipcrma.sh"]
RUNNER_DEST_PATH = ROOTDIR + "/runner.d"

LOG_PATTERN = re.compile("^.*\/\/.*@log.*")

def format_logging_argument(line_args, index):
	# TODO: format arguments properly with %s or %d looking on the table
	if (index == 0) or (index == 2): return "%s", "\"" + line_args[index] + "\""
	return "%d", line_args[index]

def format_logging_line(line_args):
	log_line = "longstrider_write(\""
	args = ""
	for i in range(len(line_args)):
		formatter, arg = format_logging_argument(line_args, i)
		args += ("," + arg)
		log_line += (formatter + " ")
	log_line = log_line[:-1] + "\"" + args + ");\n"
	return log_line

def parse_and_copy_file_for_runner(src_file, dest_file):
	fs = open(src_file)
	fd = open(dest_file, "w+")
	fd.write("#include \"longstrider.h\"\n")
	for line in fs:
		log_line = line
		if LOG_PATTERN.match(line):
			line_args = line.replace("//", "").replace("@log", "").split()
			if len(line_args) > 2: log_line = format_logging_line(line_args)
		fd.write(log_line)
	fs.close()
	fd.close()

def create_runner_dest_folder():
	try:
		os.mkdir(RUNNER_DEST_PATH, 0755);
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(RUNNER_DEST_PATH):
			pass
		else:
			raise

def copy_files_to_runner_folder(extra_files):
	for subdir, dirs, files in os.walk(ROOTDIR):
		if subdir == RUNNER_DEST_PATH: continue
		for file in files:
			src_file = os.path.join(subdir, file)
			dest_file = os.path.join(RUNNER_DEST_PATH, file)
			ext = os.path.splitext(file)[-1].lower()
			if ext in C_EXTENSIONS:
				parse_and_copy_file_for_runner(src_file, dest_file)
				
	if extra_files:
		src_files = [(ROOTDIR + "/" + f) for f in extra_files]
		for f in src_files: os.system("cp " + f + " " + RUNNER_DEST_PATH + "/")
				
	os.system("cp longstrider* " + RUNNER_DEST_PATH + "/")
	os.system("cp runner_lock* " + RUNNER_DEST_PATH + "/")


create_runner_dest_folder()
copy_files_to_runner_folder(EXTRA_FILES)
