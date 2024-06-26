# フィルタリング

<https://docs.graphene-python.org/projects/django/en/latest/filtering/>

- [フィルタリング](#フィルタリング)
  - [フィルタ可能なフィールド](#フィルタ可能なフィールド)
  - [カスタムフィルタセット](#カスタムフィルタセット)
  - [並び替え](#並び替え)

Graphene-Djangoは、結果のフィルタリングを提供する[django-filter](https://django-filter.readthedocs.io/en/master/)と統合しています。
`filter_fields`の詳細な書式は[ドキュメント](https://django-filter.readthedocs.io/en/master/guide/usage.html#the-filter)を参照してください。

`relay.Node`を実装した場合、このフィルタは自動的に利用できます。
さらに、`django-filter`は、Grapheneのオプショナルな依存です。

手動で`django-filter`をインストールする必要があるため、次の通り実行します。

```sh
pip install django-filter>=2
```

`django-filter`をインストール後、`settings.py`に`django-filter`を追加します。

```python
INSTALLED_APPS = [
  "django_filters",
]
```

> **⚠ 注意事項**
> 下のテクニックは、[cookbookアプリ例](https://github.com/graphql-python/graphene-django/tree/master/examples/cookbook)で紹介しています。

## フィルタ可能なフィールド

`filter_fields`ぱあメーターは、フィルタを適用したい特定のフィールドに使用されます。
ここで指定した値は、直接`django-filter`に渡されるため、利用可能なオプションの範囲の詳細は[フィルタリング](https://django-filter.readthedocs.io/en/master/guide/usage.html#the-filter)を参照してください。

例えば・・・

```python
class AnimalNode(DjangoObjectType):
    # 次のフィールドを持つAnimalモデルがあることを想定しています。
    class Meta:
        model = Animal
        filter_fields = ["name", "genus", "is_domesticated"]
        interfaces = (relay.Node,)


class Query(ObjectType):
    animal = relay.NodeField(AnimalNode)
    all_animals = DjangoFilterConnectionField(AnimalNode)
```

すると、次のようなクエリを実行できます。

```graphql
query {
  # フィールド名がキャメルケースになっていることに注意してください。
  allAnimals(genus: "cat", isDomesticated: true) {
    edges {
      node {
        id
        name
      }
    }
  }
}
```

また、より複雑な検索タイプも利用できます。

```python
class AnimalNode(DjangoObjectType):
    class Meta:
        model = Animal
        # より複雑な検索タイプを提供します。
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "genus": ["exact"],
            "is_domesticated": ["exact"],
        }
        interfaces = (relay.Node,)
```

次を問い合わせできます。

```graphql
query {
  allAnimals(name_Icontains: "lion") {
    edges {
      node {
        id
        name
      }
    }
  }
}

```

## カスタムフィルタセット

デフォルトで、Grapheneは、`django-filter`の最も一般的に使用される機能への簡単なアクセスを提供します。
これは、`django_filters.FilterSet`クラスを透過的に作成して、`filter_fields`の値を渡すことで実現できます。

しかし、これでは満足しないことに気づくかもしれません。
そのような場合、独自の`FilterSet`を作成できます。
次の通りそれを直接渡してください。

```python
class AnimalNode(DjangoObjectType):
    class Meta:
        model = Animal
        filter_fields = ["name", "genus", "is_domesticated"]
        interfaces = (relay.Node,)


class AnimalFilter(django_filters.FilterSet):
    # `name`の大文字小文字を区別しない検索
    name = django_filters.CharFilter(lookup_expr=["iexact"])

    class Meta:
        model = Animal
        fields = ["name", "genus", "is_domesticated"]


class Query(ObjectType):
    animal = relay.NodeField(AnimalNode)
    all_animals = DjangoFilterConnectionField(AnimalNode, filterset_class=AnimalFilter)
```

また、`DjangoObjectType`を定義しているときに、`filterset_class`パラメーターを使用して`FilterSet`クラスを指定できますが、これは`filter_fields`パラメーターと調和して使用できません。

```python
class AnimalFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr=["iexact"])

    class Meta:
        model = Animal
        fields = ["name", "genus", "is_domesticated"]


class AnimalNode(DjangoObjectType):
    class Meta:
        model = Animal
        filterset_class = AnimalFilter
        interfaces = (relay.Node,)


class Query(ObjectType):
    animal = relay.Node.Field(AnimalNode)
    all_animals = DjangoFilterConnectionField(AnimalNode)
```

コンテキスト引数は、`django_filters.FilterSet`インスタンスの[リクエスト引数](http://django-filter.readthedocs.io/en/master/guide/usage.html#request-based-filtering)として渡されます。
コンテキストに依存したフィルタをカスタマイズするためにこれを使用できます。
認証されたユーザーによって所有される同部部に事前フィルタするために、上記の`AnimalFilter`を修正します。

```python
class AnimalFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type=["iexact"])

    class Meta:
        model = Animal
        fields = ["name", "genus", "is_domesticated"]

    @property
    def qs(self):
        # クエリコンテキストはself.requestの中にあります。
        return super(AnimalFilter, self).qs.filter(owner=self.request.user)
```

## 並び替え

返された結果を並び替えする方法を定義するために`OrderFilter`を使用できます。

1つ以上のフィールドを使用して並び替えしたい場合は、フィールドのタプルに拡張してください。

```python
from django_filters import FilterSet, OrderingFilter


class UserFilter(FieldSet):
    class Meta:
        model = UserModel

    order_by = OrderingFilter(
        fields=(
          ("name", "created_at"),
        )
    )


class Group(DjangoObjectType):
    users = DjangoFilterConnectionField(Ticket, filterset_class= UserFilter)

    class Meta:
        name = "Group"
        model = GroupModel
        interfaces = (relay.Node,)

    def resolve_users(self, info, **kwargs):
        return UserFilter(kwargs).qs
```

この旬日を使用して、グループを基準にユーザーを並び替えできます。

```graphql
query {
  group(id: "xxx") {
    users(orderBy: "-created_at") {
      xxx
    }
  }
}
```
