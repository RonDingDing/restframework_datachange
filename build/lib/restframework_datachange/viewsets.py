from django.db.models import Q
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin, RetrieveModelMixin, \
    ListModelMixin
from rest_framework.response import Response
from rest_framework import status


class RRetrieveMixin(RetrieveModelMixin):
    retrieve_fields = '__all__'
    retrieve_exclude = []
    retrieve_methods = {'+': 'append', '~': 'modify'}

    def retrieve(self, request, *args, **kwargs):
        # ListModelMixin + retrieve 方法 + GenericViewSet = 修改后的 ReadOnlyModelViewSet
        instance = self.get_object()
        # 获取 Model 中该字段的 verbose_name，放进 name_dic 中，以便获取字段的中文名

        serializer = self.get_serializer(instance)
        original_data = serializer.data if bool(instance) else {}
        first_data = self.re_data(original_data, 'retrieve')
        real_data = self.reretrieve_data(first_data)
        return Response(real_data)

    def reretrieve_data(self, data):
        return data


class RListModelMixin(ListModelMixin):
    list_fields = '__all__'
    list_exclude = []
    list_methods = {'+': 'add', '~': 'change'}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            first_data = [self.re_data(i, 'list') for i in serializer.data]
            real_data = self.relist_data(first_data)
            return self.get_paginated_response(real_data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            first_data = [self.re_data(i, 'list') for i in serializer.data]
            real_data = self.relist_data(first_data)
            return Response(real_data)

    def relist_data(self, data):
        return data


class RGenericViewSet(GenericViewSet):
    can_copy_fields = []  # 前端带有可复制的图标
    method_suffix = {'append': '_org', 'add': '_src', 'attach': '_bir', 'adjoin': '_lch'}

    def find_alter(self, name, value, method):
        update = getattr(self, method + '_' + name, None)
        # 以组合插件的形式，找到某个字段a的modify_a方法，然后调用这个方法获得修改值；若找不到该方法，则返回原值
        if value:
            if update:
                value = update(value)
        elif isinstance(value, (float, int)):
            value = 0
        elif isinstance(value, str):
            value = ''
        return value

    def find_insert(self, name, data, method):
        suffix = self.method_suffix[method]
        insert = getattr(self, method + '_' + name)
        class_key = name + suffix
        num = 1
        value = []

        while getattr(self, class_key + str(num), ''):
            real_key = getattr(self, class_key + str(num), '')
            value.append(data.get(real_key, None))
            num += 1
        real_value = insert(*value)
        return real_value

    def re_data(self, data, action):
        fields = getattr(self, action + '_fields', '__all__')
        exclude = getattr(self, action + '_exclude', [])
        c_method = getattr(self, action + '_methods', {})['~']
        a_method = getattr(self, action + '_methods', {})['+']

        if isinstance(data, dict):
            # 修改
            all_result = {}
            for name, value in data.items():
                if fields == '__all__' or (name in fields):
                    if name not in exclude:
                        value = self.find_alter(name, value, c_method)
                        all_result[name] = value

            # 增加
            for m in dir(self):
                if m.startswith(a_method + '_'):
                    # 获得增加的方法add_XX，然后找对应的原始字段XX_src, 再从data中获取这个原始值value，再执行add_XX(value)
                    name = m.replace(a_method + '_', '')
                    real_value = self.find_insert(name, data, a_method)
                    if fields == '__all__' or (name in fields):
                        if name not in exclude:
                            all_result[name] = real_value

            return all_result
        else:
            return data


class RReadOnlyModelViewSet(RListModelMixin, RRetrieveMixin, RGenericViewSet):
    pass


class RDestroyModelMixin(DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        real_data = self.redestroy_data(instance)
        return Response(real_data, status=status.HTTP_204_NO_CONTENT)

    def redestroy_data(self, instance):
        return str(instance)


class RUpdateModelMixin(UpdateModelMixin):
    update_methods = {'+': 'adjoin', '~': 'vary'}
    update_fields = '__all__'
    update_exclude = '__all__'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        first_data = self.re_data(serializer.data, 'update')
        real_data = self.reupdate_data(first_data)
        return Response(real_data)

    def reupdate_data(self, data):
        return data


class RCreateModelMixin(CreateModelMixin):
    create_methods = {'+': 'attach', '~': 'reform'}
    create_fields = '__all__'
    create_exclude = '__all__'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        first_data = self.re_data(serializer.data, 'create')
        real_data = self.recreate_data(first_data)
        return Response(real_data, status=status.HTTP_201_CREATED, headers=headers)

    def recreate_data(self, data):
        return data


class RModelViewSet(RCreateModelMixin, RDestroyModelMixin, RUpdateModelMixin,
                    RListModelMixin, RRetrieveMixin, RGenericViewSet):
    pass
