import os


def _directory_element(elem_type, name, dot_path=None):
    """instantiate directory element dictionary"""
    element = {
        'type': elem_type,
        'name': name,
        'dot_path': dot_path,
        'sub_elements': []
    }
    return element


def generate_file_structure_dict(full_path, original_path=None):
    """Generates a dictionary with the preserved structure of a given
    directory.
    Files are stored in tuples, with the first element being the name
    of the file without its extention and the second element
    the dot path to the file.

    For example, given the following directory:
    test/
         subdir1/
                 subdir2/
                         file5
                 file3
                 file4

         file1
         file2

    The result will be:
    test = {
        'subdir1': {
            'subdir2': {
                'subdir2': {
                    ('file5', 'subdir1.subdir2.file5'): None,
                },
                ('file3', 'subdir1.file3'): None,
                ('file4', 'subdir1.file4'): None,
        },
        ('file1', 'file1'): None,
        ('file2', 'file2'): None,
    }
    """
    root_dir_name = os.path.basename(os.path.normpath(full_path))
    if not original_path:
        original_path = full_path
    _ = os.path.relpath(full_path, original_path).replace(os.sep, '.')
    element = _directory_element('directory', root_dir_name, _)

    all_sub_elements = os.listdir(full_path)
    files = []
    directories = []
    for elem in all_sub_elements: 
        if os.path.isdir(os.path.join(full_path, elem)):
            if elem not in ['__pycache__']:
                directories.append(elem)
        else:
            cond1 = elem not in ['__init__.py', '.DS_Store']
            cond2 = not elem.endswith('.csv')
            if cond1 and cond2:
                files.append(os.path.splitext(elem)[0])
    for directory in directories:
        _ = generate_file_structure_dict(os.path.join(full_path, directory),
                                               original_path)
        element['sub_elements'].append(_)
    for filename in files:
        full_file_path = os.path.join(full_path, filename)

        rel_file_path = os.path.relpath(full_file_path, original_path)
        dot_file_path = rel_file_path.replace(os.sep, '.')
        file_element = _directory_element('file', filename, dot_file_path)
        element['sub_elements'].append(file_element)

    return element


def get_files_dot_path(base_path):
    """generate a list of all the files inside a directory and
    subdirectories with the relative path as a dotted string.
    for example, given the files:
      C:/base_dir/dir/file1.py
      C:/base_dir/dir/sub_dir/file2.py
    get_files_in_directory_dotted_path('C:/base_dir/'):
    >['dir.file1', 'dir.sub_dir.file2']
    """
    all_files = []
    files_with_dotted_path = []
    for path, subdirs, files in os.walk(base_path):
        if not '__pycache__' in path:
            for name in files:
                if name not in ['__init__.py', '.DS_Store']:
                    filepath = os.path.join(path, os.path.splitext(name)[0])
                    all_files.append(filepath)
    for file in all_files:
        rel_path_as_list = file.replace(base_path, '').split(os.sep)
        rel_path_as_list = [x for x in rel_path_as_list if x != '']
        files_with_dotted_path.append('.'.join(rel_path_as_list))
    return files_with_dotted_path


def create_directory(path_list=None, path=None, add_init=False):
    """crate an empty directory with the option to add an __init__.py
    file inside it
    """
    if path_list:
        path = os.sep.join(path_list)
    if not os.path.exists(path):
        os.makedirs(path)
    if add_init:
        # add __init__.py file to make the new directory a python package
        init_path = os.path.join(path, '__init__.py')
        open(init_path, 'a').close()


def rename_file(old_path, old_file, new_path, new_file):
    """rename a file
    If there are no errors, returns an empty string.
    If there are errors return a string with the error description"""
    error = ''
    os.makedirs(new_path, exist_ok=True)
    old_fullpath = os.path.join(old_path, old_file)
    new_fullpath = os.path.join(new_path, new_file)
    if os.path.isfile(new_fullpath):
        error = 'File {} already exists'.format(new_fullpath)
    else:
        try:
            os.rename(old_fullpath, new_fullpath)
        except:
            error = 'There was an error renaming \'{}\' to \'{}\''.format(
                        old_fullpath, new_fullpath)
    return error


def new_directory_of_type(root_path, project, parents, dir_name, dir_type):
    """Creates a new directory for suites, tests or pages.
    If the directory is inside other directories, these should already exist.
    parents is a list of parent directories.
    dir_type should be in ['tests', 'suites', 'pages']"""
    parents = os.sep.join(parents)
    path = os.path.join(root_path, 'projects', project, dir_type, parents, dir_name)
    errors = []
    if os.path.exists(path):
        errors.append('A directory with that name already exists')
    else:
        create_directory(path=path, add_init=True)
    return errors
