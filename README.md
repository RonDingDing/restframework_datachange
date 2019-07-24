Restframework-datachange is an enhancement of rest_framework. To use it, we must have basic understandings of Django and rest_framework. 

# 1. Installation

As usual, use pip:

```
$ pip install restframework_datachange
$ pip install django
$ pip install djangorestframework
```

# 2. Before using restframework_datachange

We make a sample restframework-support project.


```
$ django-admin startproject my_project
my_project$ cd my_project
my_project$ django-admin startapp movie
```
Now we write files as followed:

## Make models.

my_project/movie/models.py
```python
from django.db import models


# Create your models here.
class Cast(models.Model):
    SEX_CHOICE = ((1, 'Male'), (2, 'Female'))

    sex = models.IntegerField(choices=SEX_CHOICE, default=1)
    profession = models.CharField(max_length=100, default='')
    foreign_name = models.CharField(max_length=100, default='')


    def __str__(self):
        return self.foreign_name


class OneMovie(models.Model):
    COUNTRY_CHOICE = ((1, 'USA'), (2, 'UK'))

    name = models.CharField(max_length=200, default='')
    director = models.ManyToManyField(Cast, related_name='director')
    actors = models.ManyToManyField(Cast, related_name='actors')
    country = models.IntegerField(default='', choices=COUNTRY_CHOICE)


    def __str__(self):
        return self.name

```

## Make Serializers. For usage of ```SlugRelatedField```, please turn to documents of djangorestframework

my_project/movie/serializers.py
```python
from rest_framework.serializers import ModelSerializer, SlugRelatedField
from movie.models import OneMovie, Cast


class MovieSerializer(ModelSerializer):
    director = SlugRelatedField(slug_field='foreign_name', queryset=Cast.objects.all(), many=True)
    actors = SlugRelatedField(slug_field='foreign_name', queryset=Cast.objects.all(), many=True)
    class Meta:
        model = OneMovie
        fields = '__all__'
```

## Make views

my_project/movie/views.py
```python
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from movie.models import OneMovie
from movie.serializers import MovieSerializer

# Create your views here.

class MovieViewSet(ModelViewSet):
    queryset = OneMovie.objects.all()
    serializer_class = MovieSerializer

```

## Change settings
my_project/my_project/settings.py

```python
...

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'movie'

]

...

```
## Make migrations and migrate.

```
my_project/my_project $ cd ..
my_project $ python manage.py makemigrations
Migrations for 'movie':
  movie/migrations/0001_initial.py
    - Create model Cast
    - Create model OneMovie

my_project$ python3 manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, movie, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying movie.0001_initial... OK
  Applying sessions.0001_initial... OK
```

## Make URLs for the whole project.

my_project/my_project/urls.py
```python
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from movie.views import MovieViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
]


router = routers.DefaultRouter()
router.register(r'movie', MovieViewSet, base_name='movie')


urlpatterns += router.urls
```

## Now we create some data for the database.

```
my_project $ python manage.py shell
 
In [1]: from movie.models import OneMovie

In [2]: from movie.models import Cast

In [3]: daniel = Cast.objects.create(sex=1, profession='actor', foreign_name='Daniel')

In [4]: daniel
Out[4]: <Cast: Daniel>

In [5]: emma =  Cast.objects.create(sex=2, profession='actor', foreign_name='Emma')
 
In [6]: Cast.objects.all()
Out[6]: <QuerySet [<Cast: Daniel>, <Cast: Emma>]>

In [7]: david = Cast.objects.create(sex=1, profession='director', foreign_name='David')

In [8]: harry_potter_movie = OneMovie.objects.create(name='Harry Potter and the Goblet of Fire', country=2)

In [9]: harry_potter_movie.director.add(david)

In [10]: harry_potter_movie.actors.add(daniel)

In [11]: harry_potter_movie.actors.add(emma)

In [12]: harry_potter_movie.save()
 
In [13]: harry_potter_movie
Out[13]: <OneMovie: Harry Potter and the Goblet of Fire>

In [14]: harry_potter_movie.director.all()
Out[14]: <QuerySet [<Cast: David>]>

In [15]: harry_potter_movie.actors.all()
Out[16]: <QuerySet [<Cast: Daniel>, <Cast: Emma>]>


```


## Now we run the server.
```
my_project/my_project $ cd ..
my_project $ python manage.py runserver 0.0.0.0:8000

```

## Click   "movie": "http://127.0.0.1:8000/movie/"

Ta da! Everything seems perfect. Below is what you'll see.
```
[
    {
        "id": 1,
        "director": [
            "David"
        ],
        "actors": [
            "Daniel",
            "Emma"
        ],
        "name": "Harry Potter and the Goblet of Fire",
        "country": 2
    }
]
```

# 3. Changing Data 

We just want the movie ```name``` to be 'Harry' instead of 'Harry Potter and the Goblet of File'. That is to say, we want to change the data returned. That's when restframework_datachange comes in!

my_project/movie/views.py
```python
from restframework_datachange.viewsets import RModelViewSet # changed
from movie.models import OneMovie
from movie.serializers import MovieSerializer

# Create your views here.

class MovieAdjust(object):           # changed
    def change_name(self, value):    # changed, xx = name
        return value.split(' ')[0]   # changed

class MovieViewSet(MovieAdjust, RModelViewSet):  # changed
    queryset = OneMovie.objects.all()
    serializer_class = MovieSerializer
```

By adding a ```change_xx``` to the ```Adjust``` object and changing inheritance to ```RModelViewSet```, we can change 'Harry Potter and the Goblet of File' to 'Harry'!


```
[
    {
        "id": 1,
        "director": [
            "David"
        ],
        "actors": [
            "Daniel",
            "Emma"
        ],
        "name": "Harry",
        "country": 2
    }
]

```

Now we change the country code into respective country name:

my_project/movie/views.py
```python
...
class MovieAdjust(object):         
    def change_name(self, value):   
        return value.split(' ')[0]  

    def change_country(self, value):
        dic = {1: 'UK', 2: 'US'}
        return dic[value]
...
```

Ta da!

```
[
    {
        "id": 1,
        "director": [
            "David"
        ],
        "actors": [
            "Daniel",
            "Emma"
        ],
        "name": "Harry",
        "country": "US"
    }
]
```

# 4. Adding new data based on one field

We want a new field that is based on the data's original field. For example, we want a string version of ```actors``` named as ```string_actors```.


my_project/movie/views.py
```python
...
class MovieAdjust(object):
    string_actors_src1 = 'actors'
    def change_name(self, value):
        return value.split(' ')[0]

    def change_country(self, value):
        dic = {1: 'UK', 2: 'US'}
        return dic[value]
    
    def add_string_actors(self, value):
        return ', '.join(value)
...
```

Make an ```add_xx``` method, pass a ```value``` and modify it, and specify the source field as ```xx_src1```. Then you can see this.

```
[
    {
        "id": 1,
        "director": [
            "David"
        ],
        "actors": [
            "Daniel",
            "Emma"
        ],
        "name": "Harry",
        "country": "US",
        "string_actors": "Daniel, Emma"
    }
]
```

# 4. Adding new data based on two or more fields

Suppose we want to join the ```country``` field and the ```name``` field to form a ```detail``` field.

```python
class MovieAdjust(object):
    string_actors_src1 = 'actors'
    detail_src1 = 'country'  # xx = detail
    detail_src2 = 'name'     # xx = detail

    def change_name(self, value):
        return value.split(' ')[0]

    def change_country(self, value):
        dic = {1: 'UK', 2: 'US'}
        return dic[value]

    def add_string_actors(self, value):
        return ', '.join(value)

    def add_detail(self, *value):  # xx = detail
        return ', '.join([str(i) for i in value])
```

Now you can see:

```
[
    {
        "id": 1,
        "director": [
            "David"
        ],
        "actors": [
            "Daniel",
            "Emma"
        ],
        "name": "Harry",
        "country": "US",
        "detail": "2, Harry Potter and the Goblet of Fire",
        "string_actors": "Daniel, Emma"
    }
]
```

Pay attention to the ```country``` part in  ```detail```, it is the original value ```1``` instead of the modified value ```UK```. Here, ```detail``` has a source field ```country```, so ```value[0]``` is the value of ```country``` field, ```1```. ```value[1]``` is the value of ```name```.

You can also write the code like this:

```python
class MovieAdjust(object):
    string_actors_src1 = 'actors'
    detail_src1 = 'country'
    detail_src2 = 'name'

    def change_name(self, value):
        return value.split(' ')[0]

    def change_country(self, value):
        dic = {1: 'UK', 2: 'US'}
        return dic[value]

    def add_string_actors(self, value):
        return ', '.join(value)[:3]

    def add_detail(self, country, name): 
        return str(country) + ', ' + str(name)
```

Make sure the number and the position of parameters beside ```self``` are the same as the ```src```s of your newly-named field.

# 5. Meddle with other actions.

If you happen to know the ```retrieve```, ```create```, ```update```, ```delete``` actions of restframework, you can meddle your return by creating ```Adjust``` objects based on the tables below: 

| Actions  |  Modification  | Method Prefix | Source Field Suffix |
|:---------|:--------------:|:-------------:|:-------------------:|
| list     |  add a field   |      add      |         src         |
| list     | change a field |    change     |         --          |
| retrieve |  add a field   |    append     |         org         |
| retrieve | change a field |    modify     |         --          |
| create   |  add a field   |    attach     |         bir         |
| create   | change a field |    reform     |         --          |
| update   |  add a field   |    adjoin     |         lch         |
| update   | change a field |     vary      |         --          |

For example:

http://127.0.0.1:8000/movie/1/ calls the ```retrieve``` method.

```python
class MovieAdjust(object):
    string_actors_src1 = 'actors'
    detail_src1 = 'country'  # xx = detail(list)
    detail_src2 = 'name'     # xx = detail(list)
    string_actors_retrieve_org1 = 'actors'  # xx = string_actors_retrieve(retrieve)

    def change_name(self, value):
        return value.split(' ')[0]

    def change_country(self, value):
        dic = {1: 'UK', 2: 'US'}
        return dic[value]

    def add_string_actors(self, value):
        return ', '.join(value)

    def add_detail(self, *value):  # xx = detail
        return ', '.join([str(i) for i in value])

    def modify_country(self, value):
        dic = {1: 'United Kingdom', 2: 'United States'}
        return dic[value]

    def append_string_actors_retrieve(self, value):
        return ', '.join(value)
```


```
{
    "id": 1,
    "director": [
        "David"
    ],
    "actors": [
        "Daniel",
        "Emma"
    ],
    "name": "Harry Potter and the Goblet of Fire",
    "country": "United States",
    "string_actors_retrieve": "Daniel, Emma"
}

```


# 6. Show/hide a field

If you want to show or hide a field, you can modify the action-specific ```_fields``` and ```_exclude``` property.

```python
class MovieAdjust(object):
    list_exclude = ['actors']

```

will get you:

```
[
    {
        "id": 1,
        "director": [
            "David"
        ],
        "name": "Harry Potter and the Goblet of Fire",
        "country": 2
    }
]
```

```python
class MovieAdjust(object):
    list_fields = ['actors', 'name']

```

will get you:

```
[
    {
        "actors": [
            "Daniel",
            "Emma"
        ],
        "name": "Harry Potter and the Goblet of Fire"
    }
]

```

# 7. Turn json into a model

If you have a python dic and wants to turn it into a Django model, use modelmaker
```python
model_maker(dic, file='fake_model.py', class_name='Default', name_changer=camel_to_, **config)
```


```dic``` A python dic.
```file``` The model will be written in the file specified. Passed as '' will only return a printed version.
```class_name``` Model name.
```name_changer``` A method to change some string into other string. Default is a function that turns camel cases to underlines.
```config``` Set the properties of model.

Example:

```python

from restframework_datachange.model_maker import model_maker
from datetime import datetime

dic = {
    'apple': 1,                  # IntegerField
    'boy': 1.2,                  # FloatField
    'cat': 'string',             # CharField
    'dog': [{'json': 1}],        # JSONField
    'elephant': datetime.now(),   # DatetimeField
    'changed': 'string'
}

config = {
    'apple__choices': [(1, 'UK'), (2, 'US')],
    'boy__null': True,
    'cat__max_length': 20,
    'dog__verbose_name': 'Dog',
    'elephant__auto_now': True
}

def name_changer(string):
    li = ['apple', 'boy', 'cat', 'dog', 'elephant']
    if string not in li:
        return 'fog'
    return string

print(model_maker(dic, file='', class_name='M', name_changer=name_changer, **config))


```

will give you:

```python
from django.contrib.postgres.fields import JSONField
from django.db import models


class M(models.Model):
    apple = models.IntegerField(verbose_name="", help_text="", null=True, choices=[(1, 'UK'), (2, 'US')])
    boy = models.FloatField(verbose_name="", help_text="", null=True)
    cat = models.CharField(verbose_name="", help_text="", default="", max_length=20)
    dog = JSONField(verbose_name="Dog", help_text="", null=True, blank=True)
    elephant = models.DateTimeField(verbose_name="", help_text="", auto_now=True, auto_now_add=False)
    fog = models.CharField(verbose_name="", help_text="", default="", max_length=64)


```