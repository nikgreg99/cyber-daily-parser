import os
from base64 import urlsafe_b64decode


def get_size_format(b, factor=1024, suffix='B'):
    """
    Scale bytes to a proper format
    e.g:
        1253656 => '1.20MB'
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def clean(text):
    # pretty text for naming a folder
    return "".join(c if c.isalnum() else '_' for c in text)


def gen_folder_name(text):
    folder_name = clean(text)
    folder_count = 0
    while os.path.isdir(folder_name):
        folder_count += 1
        if folder_name[-1].isdigit() and folder_name[-2] == "_":
            folder_name = f"{folder_name[:-2]}_{folder_count}"
        elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
            folder_name = f"{folder_name[:-3]}_{folder_count}"
        else:
            folder_name = f"{folder_name[:-3]}_{folder_count}"
    os.mkdir(folder_name)
    return folder_name


def save_html_byte_content(folder_name, data, filename=''):
    if not filename:
        filename = 'index.html'
    html_filepath = os.path.join(folder_name, filename)
    print('Saving HTML to', html_filepath)
    with open(html_filepath, 'wb') as f:
        f.write(data)
    return html_filepath

