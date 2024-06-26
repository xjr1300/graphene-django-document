# Djangoにおける認可

<https://docs.graphene-python.org/projects/django/en/latest/authorization/>

- [Djangoにおける認可](#djangoにおける認可)
  - [フィールドへのアクセスを制限する](#フィールドへのアクセスを制限する)
  - [リストのクエリセットをフィルタする](#リストのクエリセットをフィルタする)
  - [ユーザーに基づいたクエリセットをフィルタする](#ユーザーに基づいたクエリセットをフィルタする)
  - [グローバルにフィルタする](#グローバルにフィルタする)
  - [IDに基づいたノードアクセスをフィルタする](#idに基づいたノードアクセスをフィルタする)
  - [ログイン必須を追加する](#ログイン必須を追加する)

GrapheneとDjangoを使用して実装するとき、データへのアクセスを制限する方法がいくつかあります。
GraphQLを介して隠せす可能なフィールドを制限したり、ユーザーがアクセスできるオブジェクトを制限できます。

簡単なモデル例を使用しましょう。

```python
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    published = models.BooleanField(default=False)
    owner = models.ForeignKey("auth.User")
```

## フィールドへのアクセスを制限する

GraphQLクエリでフィールドを制限するためには、単純に`fields`メタ属性を使用します。

```python
from graphene import relay
from graphene_django.types import DjangoObjectType

from .models import Post


class PostNode(DjangoObjectType);
    class Meta:
        model = Post
        fields = ("title", "content")
        interfaces = (relay.Node,)
```

逆に、`exclude`メタ属性を使用できます。

```python
from graphene import relay
from graphene_django.types import DjangoObjectType

from .models import Post


class PostNode(DjangoObjectType):
    class Meta:
        model = Post
        exclude = ("published", "owner")
        interfaces = (relay.Node,)
```

## リストのクエリセットをフィルタする

クエリセットに基づいたのリスト内のどのオブジェクトを利用可能かフィルタするために、そのフィールドのリソルブメソッドを定義して、必要なクエリセットを返します。

```python
from graphene import ObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Post


class Query(ObjectType):
    all_posts = DjangoFilterConnectionField(PostNode)

    def resolve_all_posts(self, info):
        return PostObjects.filter(published=True)
```

## ユーザーに基づいたクエリセットをフィルタする

`GraphQLViw`を使用している場合、コンテキスト引数でDjangoのリクエストにアクセスできます。

```python
from graphene import ObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Post


class Query(ObjectType):
    my_posts = DjangoFilterConnectionField(PostNode)

    def resolve_my_posts(self, info):
        # コンテキストはDjangoリクエストを参照します。
        if not info.context.user.is_authenticated:
            return Post.objects.none()
        else:
            return Post.objects.filter(owner=info.context.user)
```

独自のビューを使用している場合、スキーマにリクエストコンテキストを渡すことが単純です。

```python
result = schema.execute(query, context_value=request)
```

## グローバルにフィルタする

`DjangoObjectType`を使用している場合、独自の*get_queryset*を定義できます。

```python
from graphene import relay
from graphene_django.types import DjangoObjectType

from .models import Post


class PostNode(DjangoObjectType):
    class Meta:
        model = Post

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            return queryset.Filter(published=True)
        return queryset
```

## IDに基づいたノードアクセスをフィルタする

IDに基づいたノードアクセスに認可を追加するために、`DjangoObjectType`にメソッドを追加する必要があります。

```python
from graphene_django.types import DjangoObjectType

from .models import Post


class PostNode(DjangoObjectType):
    class Meta:
        model = Post
        fields = ("title", "content")
        interfaces = (relay.Node,)

    @classmethod
    def get_node(cls, info, id):
        try:
            post = cls._meta.model.objects.get(id=id)
        except cls._meta.model.DoesNotExist:
            return None

        if post.published or info.context.user == post.owner:
            return post
        return None
```

## ログイン必須を追加する

GraphQL APIページにアクセスするユーザーを制限するために、Django標準の[LoginRequiredMixin](https://docs.djangoproject.com/en/1.10/topics/auth/default/#the-loginrequired-mixin)を使用して、`LoginRequiredMixin`と`GraphQLView`のサブクラスを含む、独自の標準的なDjangoのクラスベースドビューを作成できます。

```python
# views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from graphene_django.views import GraphQLView


class PrivateGraphQLView(LoginRequiredMixin, GraphQLView):
    pass
```

この後、プロジェクトのURL構成ファイル`urls.py`で新しい`PrivateGraphQLView`を使用できます。

```python
urlpatterns = [
    path("graphql", PrivateGraphQLView.as_view(graphiql=True, schema=schema))
]
```
