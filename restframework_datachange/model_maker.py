import os, re, datetime


def camel_to_(camel):
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel)
    re_str = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()
    return re_str


COMMON_FIELD_OPTIONS = {'null', 'blank', 'choices', 'db_column', 'db_index', 'db_tablespace', 'default', 'editable',
                        'error_messages', 'help_text', 'primary_key', 'unique', 'verbose_name', 'validators'}

INTEGER_FIELD_DEFAULT = {'verbose_name': '', 'help_text': '', 'null': True}
CHAR_FIELD_DEFAULT = {'verbose_name': '', 'help_text': '', 'default': '', 'max_length': 64}
DATETIME_FIELD_DEFAULT = {'verbose_name': '', 'help_text': '', 'auto_now': False, 'auto_now_add': False}
DATE_FIELD_DEFAULT = {'verbose_name': '', 'help_text': '', 'auto_now': False, 'auto_now_add': False}
JSON_FIELD_DEFAULT = {'verbose_name': '', 'help_text': '', 'null': True, 'blank': True}
BOOLEAN_FIELD_DEFAULT = {'verbose_name': '', 'help_text': '', 'null': True}
FLOAT_FIELD_DEFAULT = {'verbose_name': '', 'help_text': '', 'null': True}


def write_common_field(key, name_changer, what, available_options, default_options, **config):
    """
    :param key: (str)字段名称
    :param name_changer: (callable) 将字段变成另一种形式的函数指针，比如 camel_to_ 能将 'AppleCart' 转化成 'apple_cart'
    :param what: (str) field_name = {}Field() 中的 {}，比如 models.Char
    :param available_options: ([str, ...]/{str, ...}/(str, ...))该字段除了默认字段选项之外还允许什么 Options
    :param default_options: (dict)通常来说该类字段的默认配置
    :param config: 各字段的配置，用双下划线隔开，如 AppleCart__verbose_name="苹果车"，表示将 AppleCart 字段的 verbose_name 字段选项变成 "苹果车"
    :return:
    根据字段类型及参数输出 Model 下每一行字段
    """
    real_config = {k.replace(key + '__', '').replace(str(name_changer(key) + '__'), ''): v
                   for k, v in config.items()
                   if k.startswith(key + '__') or k.startswith(str(name_changer(key)) + '__')}

    allowed_options = COMMON_FIELD_OPTIONS | set(available_options) if available_options else COMMON_FIELD_OPTIONS
    banned_options = (set(real_config.keys()) - set(allowed_options)) | (
    (set(default_options.keys()) - set(allowed_options)))
    # 有该字段不允许的字段选项
    if banned_options:
        raise RuntimeError("{what}Field '{key}' have wrong options {banned} ".
                           format(what=what, key=key, banned=banned_options))
    options = default_options.copy()
    options.update(real_config)
    string_list = []

    # 将每个选项变成XX=XXField()，特殊处理字符串类型
    for k, v in options.items():
        if isinstance(v, str):
            string_list.append(str(k) + '="' + str(v) + '"')
        else:
            string_list.append(str(k) + '=' + str(v))

    options_string = ', '.join(string_list)
    return "    {key} = {what}Field({options_string})\n".format(key=name_changer(key), what=what,
                                                                options_string=options_string)


def write_integer_field(key, name_changer, default_settings=None, **config):
    if default_settings and isinstance(default_settings, dict):
        default = default_settings.get("int", INTEGER_FIELD_DEFAULT)
    else:
        default = INTEGER_FIELD_DEFAULT
    return write_common_field(key, name_changer, 'models.Integer', None, default, **config)


def write_char_field(key, name_changer, default_settings=None, **config):
    if default_settings and isinstance(default_settings, dict):
        default = default_settings.get("str", CHAR_FIELD_DEFAULT)
    else:
        default = CHAR_FIELD_DEFAULT
    return write_common_field(key, name_changer, 'models.Char', ['max_length'], default, **config)


def write_datetime_field(key, name_changer, default_settings=None, **config):
    if default_settings and isinstance(default_settings, dict):
        default = default_settings.get("datetime", DATETIME_FIELD_DEFAULT)
    else:
        default = DATETIME_FIELD_DEFAULT

    return write_common_field(key, name_changer, 'models.DateTime',
                              ['auto_now', 'auto_now_add', 'unique_for_date', 'unique_for_month',
                               'unique_for_year', ], default, **config)


def write_date_field(key, name_changer, default_settings=None, **config):
    if default_settings and isinstance(default_settings, dict):
        default = default_settings.get("date", DATE_FIELD_DEFAULT)
    else:
        default = DATE_FIELD_DEFAULT
    return write_common_field(key, name_changer, 'models.Date',
                              ['auto_now', 'auto_now_add', 'unique_for_date', 'unique_for_month',
                               'unique_for_year', ], default, **config)


def write_json_field(key, name_changer, default_settings=None, **config):
    if default_settings and isinstance(default_settings, dict):
        default = default_settings.get("json", JSON_FIELD_DEFAULT)
    else:
        default = JSON_FIELD_DEFAULT
    return write_common_field(key, name_changer, 'JSON', None, default, **config)


def write_boolean_field(key, name_changer, default_settings=None, **config):
    if default_settings and isinstance(default_settings, dict):
        default = default_settings.get("bool", BOOLEAN_FIELD_DEFAULT)
    else:
        default = BOOLEAN_FIELD_DEFAULT
    return write_common_field(key, name_changer, "models.Boolean", None, default, **config)


def write_float_field(key, name_changer, default_settings=None, **config):
    if default_settings and isinstance(default_settings, dict):
        default = default_settings.get("float", FLOAT_FIELD_DEFAULT)
    else:
        default = FLOAT_FIELD_DEFAULT
    return write_common_field(key, name_changer, "models.Float", None, default, **config)


def write_model_file(dic, file, class_name, name_changer, default_settings=None, **config):
    if not isinstance(dic, dict):
        raise RuntimeError("Parameter dic is not an instance of python dict!")
    # 根据字典值的类型选择处理函数并分派，找不到的类型都归入write_char_field
    type_method_map = {
        int: write_integer_field,
        str: write_char_field,
        datetime.date: write_date_field,
        datetime.time: write_datetime_field,
        datetime.datetime: write_datetime_field,
        dict: write_json_field,
        list: write_json_field,
        bool: write_boolean_field,
        float: write_float_field,
    }

    string = "from django.db import models\n\n\n"
    string += "class {}(models.Model):\n".format(class_name)
    json_import = "from django.contrib.postgres.fields import JSONField\n"
    # 防止没有 import JSONField

    for key, value in dic.items():
        method = type_method_map.get(type(value), write_char_field)

        if method == write_json_field and json_import not in string:
            string = json_import + string
        result = method(str(key), name_changer, default_settings, **config)
        string += result

    if file:
        try:
            os.makedirs(os.path.dirname(file))
        except:
            pass
        with open(file, 'w', encoding='utf-8') as f:
            f.write(string)
    return string


def model_maker(dic, file='fake_model.py', class_name='Default', name_changer=camel_to_, default_settings=None,
                **config):
    """
    输出与 python 字典对应的 Django Model
    :param dic: (dict)要输入的原生 python 字典
    :param file: (str)输出的文件路径
    :param class_name: (str)表的名称
    :param name_changer: (callable)将字段变成另一种形式的函数指针，比如 camel_to_ 能将 'AppleCart' 转化成 'apple_cart'
    :param config: 各字段的配置，用双下划线隔开，如 AppleCart__verbose_name="苹果车"，表示将 AppleCart 字段的 verbose_name 字段选项变成 "苹果车"
    :return:
    """
    if not file:
        file = ''
    if os.path.isfile(file):
        yes_no = input('File {} already exists, do you want to overwrite it? [y/N]'.format(file))
        # 防止覆盖已存在的文件
        if yes_no.lower() == 'y':
            return write_model_file(dic, file, class_name, name_changer, default_settings, **config)
    else:
        return write_model_file(dic, file, class_name, name_changer, default_settings, **config)
