#!/usr/bin/python3
import argparse
import os
import shutil
import hashlib
import datetime
import time


def process_agruments():
    parser = argparse.ArgumentParser(description='----------lgit.')
    parser.add_argument('command', nargs='+', help='-- add/commit/log...')
    parser.add_argument('-m', '--message', action='store')
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
        # print("Initialized empty Git repository in " + lgit_path)


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


# get_timestamp of a file
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


# get get_timestamp now
def get_now():
    second = time.time()
    timing = str(datetime.datetime.fromtimestamp(second))
    # process time -----> time stamp
    lstTime = [timing]
    get_time = ''
    for i in lstTime[0]:
        if i != '-' and i != ' ' and i != ':':
            get_time += i
    return get_time


# get file name file index-------------
def get_f_name_in_index():
    lst = convert_f_content_to_list('.lgit/index')
    list_filename_index = []
    for i in lst:
        list_filename_index.append(i[0].split()[-1])
    return list_filename_index


def convert_f_content_to_list(filename):
    path = os.getcwd()
    lst = []
    index = open(path + '/' + filename)
    lines = index.readline()
    while lines != "":
        lst.append([lines.strip()])
        lines = index.readline()
    return lst


def write_to_file(filename, list):
    with open(filename, 'w') as f:
        for item in list:
            f.write("%s\n" % item[0])


# file_git_added, file_commited
def format_file_index(file_in_cwd):
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
    # --------------------------sai----------------
    space = ' ' * 40
    if os.listdir('.lgit/snapshots/') != []:
        name_f_in_snapshots = list_all_files('.lgit/snapshots/')[0]
        content_f_snapshots = convert_f_content_to_list(name_f_in_snapshots)
        for i in content_f_snapshots:
            if file_in_cwd == i[0].split()[-1]:
                space = i[0].split()[0]
    return [timestamp + ' ' + sha1_cwd + ' ' + sha1_obj + ' ' + space + ' ' + file_in_cwd]


# this function adds files to objects dir and write to index
def process_add_command(list_item):
    for item in list_item:
        if os.path.isfile(item):
            copy_file_to_objects(item)
            _item_code = format_file_index(item)
            lst = check_exist_in_index(_item_code)
            write_to_file('.lgit/index', lst)
        elif os.path.isdir(item):
            for file in files:
                copy_file_to_objects(file)
                _item_code = format_file_index(item)
                lst = check_exist_in_index(_item_code)
                write_to_file('.lgit/index', lst)


def delete_content(filename):
    filename.seek(0)
    filename.truncate()


# check function checks if a file already exists in index_ ---> return a list
def check_exist_in_index(list): #[]
    content_index = convert_f_content_to_list('.lgit/index')
    flag = 0
    name = list[0].split()[-1]
    for i in range(len(content_index)):
        if content_index[i][0].split()[-1] == name:
            content_index[i] = list
            flag = 1
    if flag == 0:
        content_index.append(list)
    return content_index


def process_rm_command(list_file_to_remove):
    lst = convert_f_content_to_list('.lgit/index')
    filename_index = get_f_name_in_index()
    # return error if file to remove not exist in index
    for i in list_file_to_remove:
        if i not in filename_index:
            print('fatal: pathspec ' + '\'' + i + '\'' + ' did not match any files')
            return
    # get the filename in index --------> to remove afterwards
    f_name = []
    for f in filename_index:
        if f not in list_file_to_remove:
            f_name.append(f)
        else:
            os.remove(f)
    f = open('.lgit/index', 'w')
    delete_content(f)
    ls_rong = []
    if f_name != []:
        for f in f_name:
            _item_code = format_file_index(f)
            ls_rong.append(_item_code)
    write_to_file('.lgit/index', ls_rong)


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
        # ----------------------- thieu dien kien kiem tra file ton tai
        lst_cmd = command[1:]
        for f in lst_cmd:
            if not os.path.isfile(f):
                print('fatal: not a git repository (or any of the parent directories)')
                exit()
        process_add_command(lst_cmd)
    elif 'rm' in command:
        list_file_to_remove = command[1:]
        process_rm_command(list_file_to_remove)
    elif 'config' in command:
        f_config = open('.lgit/config', 'w+')
        f_config.write('%s\n' % (author))
        f_config.close()
    elif 'commit' in command:
        get_time = get_now()
        file_in_commit = open('.lgit/commits/' + get_time, 'w+')
        config = open('.lgit/config', 'r')
        msg = config.read()
        config.close()
        file_in_commit.write(msg + '\n' + get_time[:-7] + '\n\n' +
                             str(message) + '\n\n')
        file_in_commit.close()
        # Empty snapshots_dir and create a new file --- sau khi go lenh commit
        if os.listdir('.lgit/snapshots/') != []:
            name_f_in_snapshots = list_all_files('.lgit/snapshots/')[0]
            os.remove(name_f_in_snapshots)
        file_in_snapshots = open('.lgit/snapshots/' + get_time, 'w+')
        content_f_index = convert_f_content_to_list('.lgit/index')
        # create a list sha1_name in folder objects to write to snapshots
        object_sha1 = []
        # tao cai nay de luu filename trong muc snapshots lai roi sau do cap
        # nhat trong index
        filenames_in_snapshot = []
        for i in content_f_index:
            # sha1_obj + filename ----  de ghi vo file in dir snapshot
            object_sha1.append(i[0].split()[1] + ' ' + i[0].split()[-1])
            filenames_in_snapshot.append(i[0].split()[-1])
        # ['', ''] ---> [[''], ['']] to pass to write_to_file()
        lst_rong = []
        for i in object_sha1:
            lst_rong.append([i])

        write_to_file('.lgit/snapshots/' + get_time, lst_rong)
        # viet lai file index-----------update file index
        get_content_index = convert_f_content_to_list('.lgit/index')

        result = []
        for i in range(len(get_content_index)):
            get_content_index[i] = get_content_index[i][0].split()
            if len(get_content_index[i]) == 4:
                tem = get_content_index[i][3]
                get_content_index[i][3] = get_content_index[i][2]
                get_content_index[i].append(tem)
            elif len(get_content_index[i]) == 5:
                get_content_index[i][3] = get_content_index[i][2]
            rong = ''
            for j in get_content_index[i]:
                rong += j + ' '
            get_content_index[i] = rong[:-1]

        for i in get_content_index:
            result.append([i])
        write_to_file('.lgit/index', result)


if __name__ == '__main__':
    main()
