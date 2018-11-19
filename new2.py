#!/usr/bin/python3
import argparse
import os
import shutil
import hashlib
import datetime
import time


def process_agruments():
    parser = argparse.ArgumentParser(description='----------lgit.')
    parser.add_argument('command', nargs='+', help='git command -- add/commit/log...')
    parser.add_argument('-m','--message', action='store')
    parser.add_argument('--author', action='store')
    args = parser.parse_args()
    return args


# This function returns all files with a given directory path
def list_all_files(dirName):
    all_files = list()
    for root, dirs, files in os.walk(dirName):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files


# intialize a .lgit folder-----------------
def init():
    if os.path.exists('.lgit'):
        if os.path.isdir('.lgit'):
            shutil.rmtree('.lgit')
            intial_git()
            print('Reinitialized existing Git repository in ' + lgit_path)
        elif os.path.isfile('.lgit'):
            print('fatal: Invalid gitfile format: ' + lgit_path)
    else:
        intial_git()
        print("Initialized empty Git repository in " + lgit_path)


def intial_git():

    os.mkdir(lgit_path)
    os.mkdir(os.path.join(lgit_path, 'objects'))
    os.mkdir(os.path.join(lgit_path, 'commits'))
    os.mkdir(os.path.join(lgit_path, 'snapshots'))
    open('.lgit/index', 'wb').close()
    open('.lgit/config', 'a').close()
    #  write LOGNAME into config
    fd = os.open(os.path.join(lgit_path, 'config'), os.O_WRONLY)
    log_name = os.environ['LOGNAME']
    os.write(fd, log_name.encode())
    os.close(fd)


# this function convert a string into SHA1----------
def convert_text_sha1(text):
    hash_object = hashlib.sha1(text.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig


# copy file to lgit/objects/ ------sha1 (folder_name and file_name)
def copy_file_to_objects(filename):
    path = os.getcwd()
    # open the file on the command line and get the content
    file_content = open(filename, 'r').read()
    # convert the file context into sha1
    sha1 = convert_text_sha1(file_content)
    dirname = sha1[:2]
    filename = sha1[2:]
    path_objects = path + '/.lgit/objects/'
    if not os.path.exists(path_objects + dirname):
        os.mkdir(path_objects + dirname)
    # open filename(SHA1 code) and write the content
    file = open(path_objects + dirname + '/' + filename, 'w+')
    file.write(file_content)
    file.close()



def get_timestamp(filename):
    # get modify time of a file
    utime = os.path.getmtime(filename)
    # change to timestamp
    result = datetime.datetime.fromtimestamp(utime)
    my_string = str(result)
    lst = list(my_string)
    em_str = ''
    for i in lst:
        if i != '-' and i != ' ' and i != ':':
            em_str += i
    return em_str


# get file name file index-------------
def get_f_name_in_index():
    lst = convert_f_content_to_list('.lgit/index')
    list_filename_index = []
    for i in lst:
        list_filename_index.append(i[-1])
    return list_filename_index


def convert_f_content_to_list(filename):
    path = os.getcwd()
    lst = []
    index = open(path + '/' + filename)
    lines = index.readline()
    while lines != "":
        lst.append([lines])
        lines = index.readline()
    for item in range(len(lst)):
        lst[item] = lst[item][0].split()
    return lst



# file_git_added, file_commited
def write_file_index(file_in_cwd):
    path = os.getcwd()
    # get the timestamp of the file -------------
    timestamp = get_timestamp(file_in_cwd)[:-7]
    # read file in current working direc
    content_cwd = open(file_in_cwd, 'r').read()
    sha1_cwd = convert_text_sha1(content_cwd)
    # get dirname and filename to locate the file in objects directory
    dirname = sha1_cwd[:2]
    filename = sha1_cwd[2:]
    content_objects = open(path + '/' + '.lgit/objects/' + dirname + '/' + filename).read()
    sha1_obj = convert_text_sha1(content_objects)
    # check if the file_in_cwd commit or not
    if not os.path.isfile(path + '/' + '.lgit/commits' + str(timestamp)):
        space = ' ' * 40


    file_index_content = open('.lgit/index').read()
    if sha1_cwd not in file_index_content and sha1_obj not in file_index_content:
        with open(path + '/.lgit/index', 'a') as the_file:
            the_file.write(timestamp + ' ' + sha1_cwd + ' ' + sha1_obj + ' ' + space + ' ' + file_in_cwd + '\n')


def write_to_file(filename, list):
    f = open(filename, 'w+')
    for i in list:
        str1 = ''.join(i)
        f.write(str1 + '\n')
    f.write('\n')
    f.close()


def raise_errors_when_open_file(item):
    try:
        # f = open(filename, 'r')
        file_content = open(item, 'r').read()
    except PermissionError:
        print("error: open(\"" + item + "\"): Permission denied")
        print("error: unable to index file test")
        print("fatal: adding files failed")
        exit()
    except FileNotFoundError:
        print("fatal: pathspec '" + item + "' did not match any files")
        exit()


# this function adds files to objects dir and write to index
def process_add_command(list_item):
    for item in list_item:
        if os.path.isfile(item):
            raise_errors_when_open_file(item)
            copy_file_to_objects(item)
            write_file_index(item)
        elif os.path.isdir(item):
            # list all files in a given directory path
            files = list_all_files(item)
            for file in files:
                copy_file_to_objects(file)
                write_file_index(file)


def process_rm_command(list_file_to_remove):
    lst = convert_f_content_to_list('.lgit/index')
    list_filename_index = get_f_name_in_index()
    # return error if file to remove not exist in index
    for i in list_file_to_remove:
        if i not in list_filename_index:
            print('fatal: pathspec ' + '\'' + i + '\'' + ' did not match any files')
            return
    # get the filename in index --------> to remove afterwards
    f_name = []
    for f in list_filename_index:
        if f not in list_file_to_remove:
            f_name.append(f)
        else:
            os.remove(f)
    f = open('.lgit/index', 'w')
    delete_content(f)
    if f_name != []:
        for f in f_name:
            write_file_index(f)


def delete_content(filename):
    filename.seek(0)
    filename.truncate()

def read_index():
    f = open(index_path, 'r')
    lines = f.readlines()
    for line in lines:
        file_name = line.split()[-1]
        first_field = line[0:14]
        second_field = line[15:55]
        third_field = line[56:96]
        fourth_field = line[97:137]
    return file_name, first_field, second_field, third_field, fourth_field


def list_all_files2():
    all_files = []
    list = os.listdir(path)
    for item in list:
        if os.path.isdir(os.path.join(path, item)):
            all_files.append(item + "/")
        else:
            all_files.append(item)
    all_files.remove('.lgit/')
    return all_files


def find_changes():
    modified_files = []
    deleted_files = []
    f = open(index_path, 'r')
    f_content = f.read()
    # f.close()
    lines = f_content.split('\n')
    for line in lines:
        # print(line)
        if len(line) == 0:
            # print("haha")
            continue
        # tracked_files = get_f_name_in_index()
        tracked_file = line.split()[-1]
        line_number = f_content.find(line)
        # for tracked_file in tracked_files:

        try:
            # print(tracked_file)
            # print("hei")
            file_content = open(tracked_file, 'r').read()
            sha1_file = convert_text_sha1(file_content)
            file_mtime = get_timestamp(tracked_file)
            if sha1_file != line.split()[1]:  # <==== Wrong
                modified_files.append(tracked_file)
            file = os.open(index_path, os.O_RDWR)
            os.lseek(file, line_number, 0)
            os.write(file, file_mtime.encode())
            os.lseek(file, line_number + 15, 0)
            os.write(file, sha1_file.encode())
            os.close(file)
        except FileNotFoundError:
            deleted_files.append(tracked_file)
    return modified_files, deleted_files


def status():
    all_files = list_all_files2()
    untracked_files = []

    #
    # print(list)
    print(all_files)
    tracked_files = get_f_name_in_index()
    print("tracked files:")
    print(tracked_files)
    modified_files, deleted_files = find_changes()
    print("modified files:")
    print(modified_files)
    print("deleted files:")
    print(deleted_files)
    not_staged = []
    to_be_committed = []
    new = []
#
#
    for file in all_files:
        if file not in tracked_files:
            untracked_files.append(file)
    f = open(index_path, 'r')
    lines = f.readlines()
    for line in lines:
        file_name = line.split()[-1]
        first_field = line[0:14]
        second_field = line[15:55]
        third_field = line[56:96]
        fourth_field = line[97:137]
        # print("first", first_field)
        # print("second", second_field)
        # print("third", third_field)
        # print("fourth", fourth_field)
        if second_field != third_field:
            not_staged.append(file_name)
        if third_field != fourth_field:
            to_be_committed.append(file_name)
        if fourth_field == ' ' * 40:
            new.append(file_name)


    print("hey")
    print(new)
    print(not_staged)
    print(to_be_committed)
    print("yo")

    print("On branch master\n\n")
    if to_be_committed:
        print("Initial commit\n\n")

        print("Changes to be committed:\n  (use \033[93m \"./lgit.py reset HEAD ...\" \033[00m to unstage)\n")
        for file in to_be_committed:
            if file in new:
                print("new file:   ", file)
            elif file in modified_files:
                print("modified:   ", file)
            elif file in deleted_files:
                print("deleted:   ", file)
    if not_staged:
        print("Changes not staged for commit:\n  (use \"./lgit.py ad ...\" to update what will be committed)\n(use \"./lgit.py checkout -- ...\" to discard changes in working directory)")
        for file in not_staged:
            if file in modified_files:
                print("modified:   ", file)
            elif file in deleted_files:
                print("deleted:   ", file)
    if untracked_files:
        untracked_files.sort()
        print("Untracked_files:\n  (use \"./lgit.py add <file>...\" to include in what will be committed\n\n)")
        for file in untracked_files:
            print(file)



def main():
    global lgit_path, index_path, path
    path = os.getcwd()
    command = process_agruments().command
    message = process_agruments().message
    author = process_agruments().author
    dirs = os.listdir(path)
    lgit_path = os.path.abspath('.lgit')
    index_path = os.path.join(lgit_path, 'index')
    # handle if file .lgit not exist but type other command
    if '.lgit' not in dirs:
        if command != ['init']:
            print('fatal: not a git repository (or any of the parent directories)')
            exit()
    if command == ['init']:
        init()
    elif 'add' in command:
        # ----- copy file to .lgit/objects/
        lst_cmd = command[1:]
        process_add_command(lst_cmd)
    elif 'rm' in command:
        list_file_to_remove = command[1:]
        process_rm_command(list_file_to_remove)
    elif 'config' in command:
        f_config = open('.lgit/config', 'w+')
        f_config.write('%s\n' % (author))
        f_config.close()
    elif 'commit' in command:
        second = time.time()
        timing = str(datetime.datetime.fromtimestamp(second))
        # process time -----> time stamp
        lstTime = [timing]
        get_time = ''
        for i in lstTime[0]:
            if i != '-' and i != ' ' and i != ':':
                get_time += i
        file_in_commit = open('.lgit/commits/' + get_time, 'w+')
        file_in_commit.write(open('.lgit/config', 'r').read() + '\n' + get_time[:-7] + '\n\n' + str(message) + '\n\n')
        file_in_commit.close()

        file_in_snapshots = open('.lgit/snapshots/' + get_time, 'w+')
        content_f_index = convert_f_content_to_list('.lgit/index')
        # create a list sha1_name in folder objects to write to snapshots
        object_sha1 = []
        for i in content_f_index:
            object_sha1.append(i[1] + ' ' + i[-1])
        write_to_file('.lgit/snapshots/' + get_time, object_sha1)
    elif 'ls-files' in command:
        list = get_f_name_in_index()
        for i in list:
            print(i)
    if "status" in command:
        status()



if __name__ == '__main__':
    main()
