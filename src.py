import shutil
import threading
import time
import os
import sys
from datetime import datetime

class Dir_handler(threading.Thread):

	def __init__(self, source_dir, replica_dir, log_file_dir, interval=1):

		super().__init__()
		self.source_dir = source_dir
		self.replica_dir = replica_dir
		self.log_file_dir = os.path.abspath(log_file_dir)
		self.interval = interval
		self.thread_event = threading.Event()
		self.dir_dict = []

	def run(self):

		while self.thread_event.is_set() != True:

			self.update_replica(self.source_dir, self.replica_dir)
			time.sleep(self.interval)

	def compare_files(self, elem_path_src, elem_path_rep, chunk_size=1024): # Compares files byte by byte (XOR)

		with open(elem_path_src, 'rb') as elem_path_src, open(elem_path_rep, 'rb') as elem_path_rep:

			while True:

				chunk_source = elem_path_src.read(chunk_size)
				chunk_replica = elem_path_rep.read(chunk_size)

				if not chunk_source and not chunk_replica:
					return True

				for byte_1, byte_2 in zip(chunk_source, chunk_replica):
					if byte_1 ^ byte_2 != 0:
						return False

	def update_file(self, elem_path_src, elem_path_rep, replica_dirs_list):

		if os.path.basename(elem_path_src) not in replica_dirs_list:
			self.write_log("c", source=elem_path_src, replica=elem_path_rep)
			shutil.copy(elem_path_src, elem_path_rep)

		elif os.path.getsize(elem_path_src) != os.path.getsize(elem_path_rep) or not self.compare_files(elem_path_src, elem_path_rep):
			os.remove(elem_path_rep)
			shutil.copy(elem_path_src, elem_path_rep)
			self.write_log("u", path=elem_path_rep)

	def update_replica(self, source_curr_dir, replica_curr_dir):

		source_dirs_list = os.listdir(os.path.abspath(source_curr_dir))
		replica_dirs_list = os.listdir(os.path.abspath(replica_curr_dir))

		for elem in replica_dirs_list: # Deletes files and directories that are not in the source directory

			elem_path_src = os.path.join(source_curr_dir, elem)
			elem_path_rep = os.path.join(replica_curr_dir, elem)

			if not os.path.exists(os.path.abspath(elem_path_src)):
			
				if os.path.isdir(os.path.abspath(elem_path_rep)):

					shutil.rmtree(os.path.abspath(elem_path_rep))
					self.write_log("d", path=elem_path_rep)

				elif os.path.isfile(os.path.abspath(elem_path_rep)):

					os.remove(elem_path_rep)
					self.write_log("d", path=elem_path_rep)

		for elem in source_dirs_list: # Updates files and directories that are in the source directory

			elem_path_src = os.path.join(source_curr_dir, elem)
			elem_path_rep = os.path.join(replica_curr_dir, elem)

			if os.path.isfile(os.path.abspath(elem_path_src)):
				self.update_file(os.path.abspath(elem_path_src), os.path.abspath(elem_path_rep), replica_dirs_list)

			elif os.path.isdir(os.path.abspath(elem_path_src)):

				if not os.path.isdir(os.path.abspath(elem_path_rep)):
					os.makedirs(os.path.abspath(elem_path_rep))
					self.write_log("u", path=os.path.abspath(elem_path_rep))

				self.update_replica(os.path.join(source_curr_dir, elem), os.path.join(replica_curr_dir, elem))

	def write_log(self, flag, **kwargs):
		
		log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		if flag == "u":
			if 'path' not in kwargs:
				raise ValueError("For 'u' flag, 'path' argument is required.")
			log_data = kwargs['path']
			message = f"[{log_time}] Updated: {log_data}"

		elif flag == "c":
			if 'source' not in kwargs or 'replica' not in kwargs:
				raise ValueError("For 'c' flag, 'source' and 'replica' arguments are required.")
			source_dir = kwargs['source']
			replica_dir = kwargs['replica']
			log_data = f"Source: {source_dir}, Replica: {replica_dir}"
			message = f"[{log_time}] Copied: {log_data}"

		elif flag == "d":
			if 'path' not in kwargs:
				raise ValueError("For 'd' flag, 'path' argument is required.")
			log_data = kwargs['path']
			message = f"[{log_time}] Deleted: {log_data}"

		elif flag == "e":
			if 'error' not in kwargs:
				raise ValueError("For 'e' flag, 'error' argument is required.")
			log_data = kwargs['error']
			message = f"[{log_time}] Error: {log_data}"
		
		else:
			if 'info' not in kwargs:
				raise ValueError("For default flag, 'info' argument is required.")
			log_data = kwargs['info']
			message = f"[{log_time}] Info: {log_data}"

		print(message)
		with open(self.log_file_dir, 'a') as log_file:
			log_file.write(f"{message}\n")

if __name__ == "__main__":

	if len(sys.argv) != 4:

		print("Usage: python src.py <source_dir> <target_dir> <log_file>")
		sys.exit(1)

	source_dir = sys.argv[1]
	replica_dir = sys.argv[2]
	logfile_dir = sys.argv[3]

	if not os.path.isdir(source_dir):

		print(f"Error: Source directory '{source_dir}' does not exist.")
		sys.exit(1)

	if not os.path.isdir(replica_dir):

		print(f"Error: Target directory '{replica_dir}' does not exist.")
		# os.makedirs(replica_dir, exist_ok=True)
		sys.exit(1)

	handler = Dir_handler(source_dir, replica_dir, logfile_dir)
	handler.start()

	try:
		while True:
			time.sleep(10)

	except KeyboardInterrupt:
		print("Stopping directory monitoring...")
		handler.thread_event.set()
		handler.join()
		print("Stopped directory monitoring...")